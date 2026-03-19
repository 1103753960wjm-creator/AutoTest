import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api'
import { TOP_LEVEL_NAVIGATION } from '@/config/navigation'
import { createRouteMeta, getModuleLabel, getPageTypeLabel } from '@/router/route-meta'
import { useProductivityStore } from '@/stores/productivity'

const MIN_ASSET_QUERY_LENGTH = 2
const SEARCH_DEBOUNCE_MS = 180
const MAX_PAGE_RESULTS = 8
const MAX_RECENT_RESULTS = 6
const MAX_MATCHED_RECENT_RESULTS = 3
const MAX_ASSET_RESULTS = 6

const normalizeText = (value) => String(value || '').trim().toLowerCase()

const buildKeywordPool = (...parts) => {
  return parts
    .flat()
    .filter(Boolean)
    .map((item) => String(item).trim())
    .filter(Boolean)
}

const sortByWeight = (left, right) => {
  if (right._weight !== left._weight) {
    return right._weight - left._weight
  }

  return left.title.localeCompare(right.title, 'zh-CN')
}

const buildNavigationEntries = () => {
  return TOP_LEVEL_NAVIGATION
    .filter((item) => item.route)
    .map((item, index) => ({
      id: `nav:${item.key}`,
      group: 'pages',
      groupLabel: '页面 / 菜单 / 入口',
      type: 'module',
      title: item.title,
      description: item.description || '平台模块入口',
      route: item.route,
      module: item.key,
      moduleLabel: item.title,
      pageType: 'dashboard',
      pageTypeLabel: '模块入口',
      icon: '',
      keywords: buildKeywordPool(item.title, item.description, item.key, item.route),
      source: 'navigation',
      basePriority: 220 - index
    }))
}

const buildRouteEntries = (routeRecords = []) => {
  return routeRecords
    .filter((record) => record.path && !record.path.includes('/:'))
    .map((record) => {
      const meta = createRouteMeta(record.meta || {})

      if (!meta.title || meta.hidden || meta.pageType === 'auth') {
        return null
      }

      const moduleLabel = getModuleLabel(meta.module)
      const pageTypeLabel = getPageTypeLabel(meta.pageType)

      return {
        id: `route:${record.path}`,
        group: 'pages',
        groupLabel: '页面 / 菜单 / 入口',
        type: 'page',
        title: meta.title,
        description: [moduleLabel, pageTypeLabel].filter(Boolean).join(' / ') || record.path,
        route: record.path,
        module: meta.module || '',
        moduleLabel,
        pageType: meta.pageType || '',
        pageTypeLabel,
        icon: meta.icon || '',
        keywords: buildKeywordPool(
          meta.title,
          meta.description,
          meta.parentTitle,
          moduleLabel,
          pageTypeLabel,
          record.name,
          record.path
        ),
        source: 'route-meta',
        basePriority: meta.pageType === 'dashboard' ? 180 : meta.pageType === 'workspace' ? 160 : 140
      }
    })
    .filter(Boolean)
}

const mergeStaticEntries = (entries) => {
  const entryMap = new Map()

  entries.forEach((entry) => {
    const key = entry.route || entry.id
    const existing = entryMap.get(key)

    if (!existing) {
      entryMap.set(key, entry)
      return
    }

    entryMap.set(key, {
      ...existing,
      ...entry,
      keywords: Array.from(new Set([...(existing.keywords || []), ...(entry.keywords || [])])),
      basePriority: Math.max(existing.basePriority || 0, entry.basePriority || 0)
    })
  })

  return Array.from(entryMap.values())
}

const computeStaticWeight = (entry, query) => {
  if (!query) {
    return entry.basePriority || 0
  }

  const title = normalizeText(entry.title)
  const moduleLabel = normalizeText(entry.moduleLabel)
  const route = normalizeText(entry.route)
  const description = normalizeText(entry.description)
  const keywords = (entry.keywords || []).map((item) => normalizeText(item))

  let weight = entry.basePriority || 0

  if (title === query) {
    weight += 1200
  } else if (title.startsWith(query)) {
    weight += 980
  } else if (title.includes(query)) {
    weight += 860
  } else if (moduleLabel.includes(query)) {
    weight += 700
  } else if (keywords.some((item) => item === query)) {
    weight += 560
  } else if (route.includes(query) || keywords.some((item) => item.includes(query))) {
    weight += 420
  } else if (description.includes(query)) {
    weight += 280
  } else {
    return -1
  }

  weight -= title.length * 0.2
  return weight
}

const buildAssetEntry = (type, item) => {
  if (type === 'project') {
    return {
      id: `project:${item.id}`,
      group: 'assets',
      groupLabel: '轻资产',
      type: 'project',
      title: item.name,
      description: item.description || '测试设计项目',
      route: `/ai-generation/projects/${item.id}`,
      module: 'test-design',
      moduleLabel: '测试设计',
      pageType: 'detail-result',
      pageTypeLabel: '项目详情',
      icon: 'folder-opened',
      summary: '测试设计项目',
      source: 'dynamic'
    }
  }

  return {
    id: `testcase:${item.id}`,
    group: 'assets',
    groupLabel: '轻资产',
    type: 'testcase',
    title: item.title || item.name || `测试用例 ${item.id}`,
    description: item.description || item.steps || '测试用例',
    route: `/ai-generation/testcases/${item.id}`,
    module: 'test-design',
    moduleLabel: '测试设计',
    pageType: 'detail-result',
    pageTypeLabel: '测试用例详情',
    icon: 'document',
    summary: item.project?.name ? `关联项目：${item.project.name}` : '测试设计用例',
    source: 'dynamic'
  }
}

export const usePlatformSearchStore = defineStore('platform-search', () => {
  const productivityStore = useProductivityStore()

  const isOpen = ref(false)
  const query = ref('')
  const loading = ref(false)
  const staticEntries = ref([])
  const assetEntries = ref([])
  const hasInitialized = ref(false)

  let searchTimer = null
  let latestSearchToken = 0

  const recentResults = computed(() => {
    const normalizedQuery = normalizeText(query.value)
    const limit = normalizedQuery ? MAX_MATCHED_RECENT_RESULTS : MAX_RECENT_RESULTS

    return productivityStore.recentVisits
      .filter((item) => {
        if (!normalizedQuery) {
          return true
        }

        const haystack = buildKeywordPool(
          item.title,
          item.summary,
          item.route,
          getModuleLabel(item.module),
          getPageTypeLabel(item.pageType)
        )
          .map((entry) => normalizeText(entry))
          .join(' ')

        return haystack.includes(normalizedQuery)
      })
      .slice(0, limit)
      .map((item) => ({
        ...item,
        group: 'recent',
        groupLabel: '最近访问',
        type: 'recent',
        description: item.summary || [getModuleLabel(item.module), getPageTypeLabel(item.pageType)].filter(Boolean).join(' / ')
      }))
  })

  const pageResults = computed(() => {
    const normalizedQuery = normalizeText(query.value)

    return staticEntries.value
      .map((entry) => ({
        ...entry,
        _weight: computeStaticWeight(entry, normalizedQuery)
      }))
      .filter((entry) => entry._weight >= 0)
      .sort(sortByWeight)
      .slice(0, MAX_PAGE_RESULTS)
      .map(({ _weight, ...entry }) => entry)
  })

  const resultGroups = computed(() => {
    const groups = []

    if (pageResults.value.length) {
      groups.push({
        key: 'pages',
        label: '页面 / 菜单 / 入口',
        items: pageResults.value
      })
    }

    if (recentResults.value.length) {
      groups.push({
        key: 'recent',
        label: '最近访问',
        items: recentResults.value
      })
    }

    if (assetEntries.value.length) {
      groups.push({
        key: 'assets',
        label: '轻资产',
        items: assetEntries.value
      })
    }

    return groups
  })

  const initializeStaticIndex = (routeRecords = []) => {
    if (hasInitialized.value) {
      return
    }

    const navigationEntries = buildNavigationEntries()
    const routeEntries = buildRouteEntries(routeRecords)

    staticEntries.value = mergeStaticEntries([...navigationEntries, ...routeEntries])
    hasInitialized.value = true
  }

  const openSearch = () => {
    isOpen.value = true
  }

  const closeSearch = () => {
    isOpen.value = false
    clearSearch()
  }

  const clearSearch = () => {
    if (searchTimer) {
      clearTimeout(searchTimer)
      searchTimer = null
    }

    latestSearchToken += 1
    query.value = ''
    assetEntries.value = []
    loading.value = false
  }

  const searchAssets = async (keyword) => {
    if (keyword.length < MIN_ASSET_QUERY_LENGTH) {
      assetEntries.value = []
      loading.value = false
      return
    }

    const currentToken = ++latestSearchToken
    loading.value = true

    try {
      const [projectResponse, testcaseResponse] = await Promise.all([
        api.get('/projects/', {
          params: {
            page: 1,
            page_size: 3,
            search: keyword
          }
        }),
        api.get('/testcases/', {
          params: {
            page: 1,
            page_size: 3,
            search: keyword
          }
        })
      ])

      if (currentToken !== latestSearchToken) {
        return
      }

      const projectItems = (projectResponse.data?.results || []).map((item) => buildAssetEntry('project', item))
      const testcaseItems = (testcaseResponse.data?.results || []).map((item) => buildAssetEntry('testcase', item))

      assetEntries.value = [...projectItems, ...testcaseItems].slice(0, MAX_ASSET_RESULTS)
    } catch (error) {
      if (currentToken === latestSearchToken) {
        assetEntries.value = []
      }
    } finally {
      if (currentToken === latestSearchToken) {
        loading.value = false
      }
    }
  }

  const scheduleSearch = () => {
    if (searchTimer) {
      clearTimeout(searchTimer)
      searchTimer = null
    }

    const keyword = normalizeText(query.value)

    if (!keyword) {
      assetEntries.value = []
      loading.value = false
      return
    }

    searchTimer = setTimeout(() => {
      searchAssets(keyword)
    }, SEARCH_DEBOUNCE_MS)
  }

  const setQuery = (nextQuery) => {
    query.value = nextQuery
    scheduleSearch()
  }

  return {
    isOpen,
    query,
    loading,
    resultGroups,
    initializeStaticIndex,
    openSearch,
    closeSearch,
    clearSearch,
    setQuery
  }
})
