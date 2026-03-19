import { resolveRouteMeta } from './route-meta'

export const SOURCE_QUERY_KEYS = Object.freeze(['from', 'fromPath', 'fromTitle', 'fromModule'])

export const DEEPLINK_SOURCE_TYPES = Object.freeze([
  'list',
  'home',
  'search',
  'recent',
  'favorite',
  'dashboard',
  'detail'
])

const SOURCE_TYPE_SET = new Set(DEEPLINK_SOURCE_TYPES)

const SUPPORTED_DEEPLINK_PATTERNS = [
  /^\/ai-generation\/projects\/[^/]+$/,
  /^\/ai-generation\/testcases\/[^/]+$/,
  /^\/ai-generation\/testcases\/[^/]+\/edit$/,
  /^\/ai-generation\/executions\/[^/]+$/
]

const INVALID_PROTOCOL_PATTERN = /^[a-zA-Z][a-zA-Z\d+\-.]*:/

const normalizeQueryValue = (value) => {
  if (Array.isArray(value)) {
    return value[0] || ''
  }

  return value || ''
}

const sanitizeText = (value, maxLength = 60) => {
  const normalized = String(normalizeQueryValue(value) || '').trim()

  if (!normalized) {
    return ''
  }

  return normalized.slice(0, maxLength)
}

export const sanitizeInternalPath = (value) => {
  const normalized = String(normalizeQueryValue(value) || '').trim()

  if (!normalized) {
    return ''
  }

  if (!normalized.startsWith('/')) {
    return ''
  }

  if (normalized.startsWith('//') || INVALID_PROTOCOL_PATTERN.test(normalized)) {
    return ''
  }

  return normalized
}

export const parseInternalTarget = (target) => {
  const normalized = sanitizeInternalPath(target)

  if (!normalized) {
    return null
  }

  const [pathAndQuery, hashPart = ''] = normalized.split('#')
  const [path, search = ''] = pathAndQuery.split('?')
  const params = new URLSearchParams(search)
  const query = {}

  params.forEach((value, key) => {
    query[key] = value
  })

  return {
    path,
    query,
    hash: hashPart ? `#${hashPart}` : ''
  }
}

export const omitSourceContextQuery = (query = {}) => {
  const nextQuery = { ...(query || {}) }

  SOURCE_QUERY_KEYS.forEach((key) => {
    delete nextQuery[key]
  })

  return nextQuery
}

export const stringifyInternalTarget = ({ path, query = {}, hash = '' }) => {
  const safePath = sanitizeInternalPath(path)

  if (!safePath) {
    return ''
  }

  const searchParams = new URLSearchParams()

  Object.entries(query || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') {
      return
    }

    searchParams.set(key, value)
  })

  const search = searchParams.toString()

  return `${safePath}${search ? `?${search}` : ''}${hash || ''}`
}

export const normalizeTargetPath = (target) => {
  const parsed = parseInternalTarget(target)

  if (!parsed) {
    return ''
  }

  return stringifyInternalTarget({
    path: parsed.path,
    query: omitSourceContextQuery(parsed.query),
    hash: parsed.hash
  })
}

export const sanitizeSourceContext = (query = {}) => {
  const from = sanitizeText(query.from, 20)
  const fromType = SOURCE_TYPE_SET.has(from) ? from : ''

  return {
    from: fromType,
    fromPath: sanitizeInternalPath(query.fromPath),
    fromTitle: sanitizeText(query.fromTitle, 40),
    fromModule: sanitizeText(query.fromModule, 32)
  }
}

export const buildSourceContext = (context = {}) => {
  return sanitizeSourceContext(context)
}

export const buildSourceContextFromRoute = (route, sourceType, fallbackTitle = '') => {
  if (!route || !sourceType) {
    return buildSourceContext({})
  }

  const meta = resolveRouteMeta(route)

  return buildSourceContext({
    from: sourceType,
    fromPath: route.fullPath || route.path || '',
    fromTitle: fallbackTitle || meta.title || '',
    fromModule: meta.module || ''
  })
}

export const isSupportedDeeplinkPath = (path) => {
  const safePath = sanitizeInternalPath(path)

  if (!safePath) {
    return false
  }

  return SUPPORTED_DEEPLINK_PATTERNS.some((pattern) => pattern.test(safePath))
}

export const buildDeeplinkLocation = ({
  target,
  currentRoute = null,
  sourceType = '',
  sourceTitle = '',
  sourceContext = null,
  extraQuery = {}
}) => {
  const parsed = parseInternalTarget(target)

  if (!parsed) {
    return null
  }

  const baseQuery = omitSourceContextQuery(parsed.query)
  const mergedQuery = { ...baseQuery, ...(extraQuery || {}) }

  if (isSupportedDeeplinkPath(parsed.path)) {
    const resolvedSource = sourceContext
      ? buildSourceContext(sourceContext)
      : buildSourceContextFromRoute(currentRoute, sourceType, sourceTitle)

    Object.assign(mergedQuery, resolvedSource)
  }

  const nextQuery = Object.fromEntries(
    Object.entries(mergedQuery).filter(([, value]) => value !== undefined && value !== null && value !== '')
  )

  return {
    path: parsed.path,
    query: Object.keys(nextQuery).length ? nextQuery : undefined,
    hash: parsed.hash || undefined
  }
}

export const resolveReturnTarget = ({ route, fallbackPath = '', fallbackTitle = '' }) => {
  const sourceContext = sanitizeSourceContext(route?.query || {})

  if (sourceContext.fromPath) {
    return {
      path: sourceContext.fromPath,
      label: sourceContext.fromTitle ? `返回${sourceContext.fromTitle}` : '返回来源'
    }
  }

  const normalizedFallback = normalizeTargetPath(fallbackPath)

  if (normalizedFallback) {
    return {
      path: normalizedFallback,
      label: fallbackTitle ? `返回${fallbackTitle}` : '返回列表'
    }
  }

  return null
}

export const pickAllowedTab = (value, allowedTabs = [], fallbackTab = '') => {
  const nextValue = sanitizeText(value, 20)

  if (allowedTabs.includes(nextValue)) {
    return nextValue
  }

  return fallbackTab
}
