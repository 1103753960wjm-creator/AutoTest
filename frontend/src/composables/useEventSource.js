const DEFAULT_RECONNECT_DELAY_MS = 5000

function buildEventSourceUrl(url) {
  if (!url) {
    return ''
  }

  if (/^https?:\/\//i.test(url)) {
    return url
  }

  const path = url.startsWith('/') ? url : `/${url}`
  if (path.startsWith('/api/')) {
    return `${window.location.origin}${path}`
  }

  return `${window.location.origin}/api${path}`
}

export function createManagedEventSource(options = {}) {
  const {
    url,
    withCredentials = true,
    reconnectDelayMs = DEFAULT_RECONNECT_DELAY_MS,
    maxReconnectAttempts = 1,
    parseMessage = JSON.parse,
    onOpen,
    onMessage,
    onError,
    onFallback,
    onClose
  } = options

  let eventSource = null
  let reconnectTimer = null
  let reconnectAttempts = 0
  let closedByClient = false

  const clearReconnectTimer = () => {
    if (reconnectTimer) {
      window.clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  const close = (reason = 'manual') => {
    closedByClient = true
    clearReconnectTimer()
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    onClose?.(reason)
  }

  const fallback = (event) => {
    if (closedByClient) {
      return
    }
    close('fallback')
    onFallback?.(event)
  }

  const scheduleReconnectCheck = (event) => {
    clearReconnectTimer()

    reconnectTimer = window.setTimeout(() => {
      if (!eventSource || closedByClient) {
        return
      }

      if (eventSource.readyState === EventSource.CONNECTING) {
        reconnectAttempts += 1
        if (reconnectAttempts >= maxReconnectAttempts) {
          fallback(event)
        }
      }
    }, reconnectDelayMs)
  }

  const connect = () => {
    close('reconnect')
    closedByClient = false
    reconnectAttempts = 0

    const sourceUrl = buildEventSourceUrl(url)
    if (!sourceUrl) {
      throw new Error('EventSource URL is required')
    }

    eventSource = new EventSource(sourceUrl, { withCredentials })

    eventSource.onopen = (event) => {
      reconnectAttempts = 0
      clearReconnectTimer()
      onOpen?.(event)
    }

    eventSource.onmessage = (event) => {
      if (closedByClient) {
        return
      }

      try {
        const payload = parseMessage ? parseMessage(event.data) : event.data
        onMessage?.(payload, event)
      } catch (error) {
        onError?.(error, event)
      }
    }

    eventSource.onerror = (event) => {
      if (closedByClient || !eventSource) {
        return
      }

      onError?.(event)

      if (eventSource.readyState === EventSource.CLOSED) {
        fallback(event)
        return
      }

      scheduleReconnectCheck(event)
    }

    return eventSource
  }

  return {
    connect,
    close,
    getReadyState: () => eventSource?.readyState,
    getUrl: () => eventSource?.url || buildEventSourceUrl(url),
    isConnected: () => !!eventSource && eventSource.readyState === EventSource.OPEN
  }
}
