function firstText(value) {
  if (!value) return ''

  if (typeof value === 'string') return value

  if (Array.isArray(value)) {
    return value.map(firstText).find(Boolean) || ''
  }

  if (typeof value === 'object') {
    for (const key of ['message', 'error', 'detail']) {
      const text = firstText(value[key])
      if (text) return text
    }

    for (const [key, item] of Object.entries(value)) {
      const text = firstText(item)
      if (text) return `${key}: ${text}`
    }
  }

  return ''
}

export function getErrorPayload(error) {
  return error?.response?.data || error?.data || error || {}
}

export function getErrorMessage(error, fallback = '操作失败') {
  const payload = getErrorPayload(error)

  const directMessage = firstText(payload?.message)
    || firstText(payload?.error)
    || firstText(payload?.detail)
    || firstText(payload?.details)
    || firstText(payload?.errors)

  if (directMessage) {
    return directMessage
  }

  return error?.message || fallback
}

export function getErrorCode(error) {
  return getErrorPayload(error)?.code || ''
}

export function getErrorRequestId(error) {
  return getErrorPayload(error)?.request_id || ''
}
