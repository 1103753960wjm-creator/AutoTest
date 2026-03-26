import api from '@/utils/api'

export const GENERATION_TERMINAL_STATUSES = Object.freeze(['completed', 'failed', 'cancelled'])

const STORAGE_PREFIX = 'testhub.ai-generation.current-task.project:'
const TERMINAL_CONTEXT_TTL = 30 * 60 * 1000

export function buildGenerationTaskStorageKey(projectId) {
  return `${STORAGE_PREFIX}${projectId || 'none'}`
}

export function saveGenerationTaskContext(projectId, context) {
  if (typeof window === 'undefined') {
    return
  }

  const storageKey = buildGenerationTaskStorageKey(projectId)
  const payload = {
    ...context,
    lastSeenAt: context?.lastSeenAt || new Date().toISOString()
  }
  window.sessionStorage.setItem(storageKey, JSON.stringify(payload))
}

export function loadGenerationTaskContext(projectId) {
  if (typeof window === 'undefined') {
    return null
  }

  const storageKey = buildGenerationTaskStorageKey(projectId)
  const raw = window.sessionStorage.getItem(storageKey)
  if (!raw) {
    return null
  }

  try {
    const parsed = JSON.parse(raw)
    const status = parsed?.status || ''
    const lastSeenAt = parsed?.lastSeenAt ? Date.parse(parsed.lastSeenAt) : 0

    if (
      GENERATION_TERMINAL_STATUSES.includes(status) &&
      lastSeenAt &&
      Date.now() - lastSeenAt > TERMINAL_CONTEXT_TTL
    ) {
      window.sessionStorage.removeItem(storageKey)
      return null
    }

    return parsed
  } catch (error) {
    window.sessionStorage.removeItem(storageKey)
    return null
  }
}

export function clearGenerationTaskContext(projectId) {
  if (typeof window === 'undefined') {
    return
  }

  window.sessionStorage.removeItem(buildGenerationTaskStorageKey(projectId))
}

export function createGenerationTaskTracker() {
  let eventSource = null
  let pollTimer = null
  let activeTaskId = ''
  let disposed = false
  let fallbackStarted = false

  const cleanupSse = () => {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  }

  const cleanupPolling = () => {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  const stopTracking = () => {
    cleanupSse()
    cleanupPolling()
    fallbackStarted = false
  }

  const emitTerminal = (callbacks, task) => {
    stopTracking()
    callbacks.onTerminal?.(task)
  }

  const startPolling = (taskId, callbacks) => {
    if (disposed || !taskId || pollTimer) {
      return
    }

    pollTimer = setInterval(async () => {
      try {
        const response = await api.get(`/requirement-analysis/testcase-generation/${taskId}/progress/`)
        const task = response.data
        callbacks.onPollData?.(task)

        if (GENERATION_TERMINAL_STATUSES.includes(task?.status)) {
          emitTerminal(callbacks, task)
        }
      } catch (error) {
        callbacks.onError?.(error)
      }
    }, 3000)
  }

  const ensurePollingFallback = (taskId, callbacks) => {
    if (fallbackStarted || disposed) {
      return
    }
    fallbackStarted = true
    cleanupSse()
    startPolling(taskId, callbacks)
  }

  const startSse = (taskId, callbacks) => {
    const currentOrigin = window.location.origin
    const apiUrl = `${currentOrigin}/api/requirement-analysis/testcase-generation/${taskId}/stream_progress/`
    eventSource = new EventSource(apiUrl, { withCredentials: true })

    eventSource.onmessage = async (event) => {
      if (disposed) {
        return
      }

      try {
        const data = JSON.parse(event.data)
        callbacks.onSsePayload?.(data)

        if (data.type === 'status' && GENERATION_TERMINAL_STATUSES.includes(data.status)) {
          const response = await api.get(`/requirement-analysis/testcase-generation/${taskId}/progress/`)
          emitTerminal(callbacks, response.data)
          return
        }

        if (data.type === 'done') {
          const response = await api.get(`/requirement-analysis/testcase-generation/${taskId}/progress/`)
          emitTerminal(callbacks, response.data)
        }
      } catch (error) {
        callbacks.onError?.(error)
      }
    }

    eventSource.onerror = () => {
      if (disposed) {
        return
      }

      if (!eventSource) {
        return
      }

      if (eventSource.readyState === 2) {
        ensurePollingFallback(taskId, callbacks)
        return
      }

      window.setTimeout(() => {
        if (!disposed && eventSource && eventSource.readyState === 0) {
          ensurePollingFallback(taskId, callbacks)
        }
      }, 5000)
    }
  }

  const startTracking = ({ taskId, outputMode = 'stream', ...callbacks }) => {
    stopTracking()
    activeTaskId = taskId || ''
    disposed = false

    if (!activeTaskId) {
      return
    }

    if (outputMode === 'stream') {
      startSse(activeTaskId, callbacks)
      return
    }

    startPolling(activeTaskId, callbacks)
  }

  const recoverTracking = ({ taskId, outputMode = 'stream', ...callbacks }) => {
    startTracking({ taskId, outputMode, ...callbacks })
  }

  const dispose = () => {
    disposed = true
    activeTaskId = ''
    stopTracking()
  }

  return {
    startTracking,
    recoverTracking,
    stopTracking,
    dispose,
    getActiveTaskId: () => activeTaskId
  }
}
