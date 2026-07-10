const DEFAULT_RECONNECT_DELAY_MS = 3000

function buildWebSocketUrl(url) {
  if (!url) {
    return ''
  }

  if (/^wss?:\/\//i.test(url)) {
    return url
  }

  const path = url.startsWith('/') ? url : `/${url}`
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}${path}`
}

export function createManagedWebSocket(options = {}) {
  const {
    url,
    protocols,
    reconnectDelayMs = DEFAULT_RECONNECT_DELAY_MS,
    maxReconnectAttempts = 2,
    parseMessage = JSON.parse,
    onOpen,
    onMessage,
    onError,
    onClose,
    onReconnectFailed
  } = options

  let socket = null
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
    const currentSocket = socket
    socket = null
    if (currentSocket) {
      currentSocket.close()
    }
  }

  const connect = () => {
    const socketUrl = buildWebSocketUrl(url)
    if (!socketUrl) {
      throw new Error('WebSocket URL is required')
    }

    clearReconnectTimer()
    closedByClient = false
    const currentSocket = protocols ? new WebSocket(socketUrl, protocols) : new WebSocket(socketUrl)
    socket = currentSocket

    currentSocket.onopen = (event) => {
      reconnectAttempts = 0
      onOpen?.(event)
    }

    currentSocket.onmessage = (event) => {
      try {
        const payload = parseMessage ? parseMessage(event.data) : event.data
        onMessage?.(payload, event)
      } catch (error) {
        onError?.(error, event)
      }
    }

    currentSocket.onerror = (event) => {
      onError?.(event)
    }

    currentSocket.onclose = (event) => {
      if (socket === currentSocket) {
        socket = null
      }
      onClose?.(event)

      if (closedByClient) {
        return
      }

      reconnectAttempts += 1
      if (reconnectAttempts > maxReconnectAttempts) {
        onReconnectFailed?.(event)
        return
      }

      clearReconnectTimer()
      reconnectTimer = window.setTimeout(connect, reconnectDelayMs)
    }

    return socket
  }

  const send = (data) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return false
    }

    socket.send(typeof data === 'string' ? data : JSON.stringify(data))
    return true
  }

  return {
    connect,
    close,
    send,
    getReadyState: () => socket?.readyState,
    getUrl: () => socket?.url || buildWebSocketUrl(url),
    isConnected: () => !!socket && socket.readyState === WebSocket.OPEN
  }
}
