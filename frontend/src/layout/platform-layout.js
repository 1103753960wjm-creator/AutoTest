import { NAVIGATION_MODULES, TOP_LEVEL_NAVIGATION, NAV_ENTRY_STATUS, findFrozenModuleByPath } from '@/config/navigation'

const VISIBLE_NAV_STATUSES = new Set([
  NAV_ENTRY_STATUS.KEEP,
  NAV_ENTRY_STATUS.FUTURE_MOVE
])

const MODULES_WITH_PROJECT_CONTEXT = new Set([
  'test-design',
  'api-automation',
  'web-automation',
  'app-automation'
])

const matchByPrefix = (path, prefix) => path === prefix || path.startsWith(`${prefix}/`)

const matchChildPath = (path, childPath) => {
  if (!childPath) {
    return false
  }

  const dynamicIndex = childPath.indexOf('/:')
  if (dynamicIndex !== -1) {
    const basePath = childPath.slice(0, dynamicIndex)
    return matchByPrefix(path, basePath)
  }

  return path === childPath
}

export function getTopLevelPlatformNav() {
  return TOP_LEVEL_NAVIGATION
}

export function getModuleDefinitionByKey(moduleKey) {
  return NAVIGATION_MODULES.find((module) => module.key === moduleKey) || null
}

export function getCurrentModuleDefinition(path, moduleKey) {
  return getModuleDefinitionByKey(moduleKey) || findFrozenModuleByPath(path)
}

export function shouldShowProjectContext(moduleKey) {
  return MODULES_WITH_PROJECT_CONTEXT.has(moduleKey)
}

export function getModuleSidebarItems(moduleKey, currentPath = '') {
  const currentModule = getModuleDefinitionByKey(moduleKey)
  if (!currentModule) {
    return []
  }

  const items = [...(currentModule.children || [])]
  const executionCenter = getModuleDefinitionByKey('execution-center')

  if (executionCenter && currentModule.title) {
    items.push(
      ...(executionCenter.children || []).filter((child) => child.source === currentModule.title)
    )
  }

  const seen = new Set()

  return items.filter((item) => {
    const key = item.path || `${item.title}-${item.status}`
    if (seen.has(key)) {
      return false
    }

    seen.add(key)

    if (!item.path) {
      return currentModule.key === 'system-management' && item.status === NAV_ENTRY_STATUS.RESERVED
    }
    return VISIBLE_NAV_STATUSES.has(item.status)
  })
}

