export const MODULE_META = Object.freeze({
  workbench: {
    label: '工作台',
    entry: '/home'
  },
  'test-design': {
    label: '测试设计',
    entry: '/ai-generation/requirement-analysis'
  },
  'api-automation': {
    label: '接口自动化',
    entry: '/api-testing/dashboard'
  },
  'web-automation': {
    label: 'Web 自动化',
    entry: '/ui-automation/dashboard'
  },
  'app-automation': {
    label: 'App 自动化',
    entry: '/app-automation/dashboard'
  },
  'data-factory': {
    label: '数据工厂',
    entry: '/data-factory'
  },
  'config-center': {
    label: '配置中心',
    entry: '/configuration/ai-model'
  },
  'system-management': {
    label: '系统管理',
    entry: '/ai-generation/profile'
  }
})

export const PAGE_TYPE_META = Object.freeze({
  dashboard: '概览页',
  list: '列表页',
  workspace: '工作台',
  'detail-result': '详情结果页',
  config: '配置页',
  auth: '认证页'
})

export const ROUTE_META_DEFAULTS = Object.freeze({
  title: '',
  description: '',
  module: '',
  pageType: '',
  icon: '',
  keepAlive: false,
  hidden: false,
  parentTitle: '',
  activeMenu: ''
})

export function createRouteMeta(options = {}) {
  return {
    ...ROUTE_META_DEFAULTS,
    ...options
  }
}

export function resolveRouteMeta(route) {
  return route.matched.reduce((accumulator, record) => {
    return {
      ...accumulator,
      ...(record.meta || {})
    }
  }, createRouteMeta())
}

export function getModuleLabel(moduleKey) {
  return MODULE_META[moduleKey]?.label || ''
}

export function getModuleEntry(moduleKey) {
  return MODULE_META[moduleKey]?.entry || ''
}

export function getPageTypeLabel(pageType) {
  return PAGE_TYPE_META[pageType] || ''
}

export function buildBreadcrumbItems(route) {
  const meta = resolveRouteMeta(route)
  const items = [
    {
      title: '首页',
      to: '/home'
    }
  ]

  const moduleLabel = getModuleLabel(meta.module)
  const moduleEntry = getModuleEntry(meta.module)

  if (moduleLabel && route.path !== '/home') {
    items.push({
      title: moduleLabel,
      to: meta.module === 'workbench' ? '/home' : moduleEntry || ''
    })
  }

  if (meta.parentTitle && meta.parentTitle !== moduleLabel) {
    items.push({
      title: meta.parentTitle,
      to: meta.activeMenu || ''
    })
  }

  if (meta.title && meta.title !== items[items.length - 1]?.title) {
    items.push({
      title: meta.title,
      to: route.fullPath,
      current: true
    })
  }

  return items
}

export function getDocumentTitle(route) {
  const meta = resolveRouteMeta(route)
  return meta.title ? `${meta.title} - TestHub` : 'TestHub'
}
