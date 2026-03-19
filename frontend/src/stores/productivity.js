import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { resolveRouteMeta, getModuleLabel, getPageTypeLabel } from '@/router/route-meta'
import { normalizeTargetPath } from '@/router/deeplink'

const PRODUCTIVITY_STORAGE_KEY = 'platform-productivity-v1'
const MAX_RECENT_VISITS = 12
const MAX_FAVORITES = 20

const createEmptyState = () => ({
  recentVisits: [],
  favorites: []
})

const normalizeStoredEntries = (entries = [], type = 'recent') => {
  return (entries || [])
    .map((entry) => {
      const normalizedFullPath = normalizeTargetPath(entry.fullPath || entry.route || '')

      if (!normalizedFullPath) {
        return null
      }

      return {
        ...entry,
        id: type === 'favorite' ? `favorite:${normalizedFullPath}` : `route:${normalizedFullPath}`,
        route: normalizeTargetPath(entry.route || normalizedFullPath) || normalizedFullPath.split('?')[0],
        fullPath: normalizedFullPath
      }
    })
    .filter(Boolean)
}

const readProductivityState = () => {
  try {
    const raw = localStorage.getItem(PRODUCTIVITY_STORAGE_KEY)

    if (!raw) {
      return createEmptyState()
    }

    const parsed = JSON.parse(raw)

    return {
      recentVisits: normalizeStoredEntries(Array.isArray(parsed.recentVisits) ? parsed.recentVisits : [], 'recent'),
      favorites: normalizeStoredEntries(Array.isArray(parsed.favorites) ? parsed.favorites : [], 'favorite')
    }
  } catch (error) {
    console.error('读取平台效率数据失败:', error)
    return createEmptyState()
  }
}

const persistProductivityState = (state) => {
  localStorage.setItem(PRODUCTIVITY_STORAGE_KEY, JSON.stringify(state))
}

const buildRouteEntry = (route) => {
  const meta = resolveRouteMeta(route)
  const title = meta.title || '未命名页面'
  const moduleLabel = getModuleLabel(meta.module)
  const pageTypeLabel = getPageTypeLabel(meta.pageType)
  const normalizedFullPath = normalizeTargetPath(route.fullPath || route.path || '')
  const normalizedRoutePath = normalizeTargetPath(route.path || normalizedFullPath) || normalizedFullPath

  return {
    title,
    route: normalizedRoutePath,
    fullPath: normalizedFullPath,
    module: meta.module || '',
    pageType: meta.pageType || '',
    icon: meta.icon || '',
    summary: [moduleLabel, pageTypeLabel || title].filter(Boolean).join(' / '),
    source: 'local'
  }
}

const createFavoriteEntry = (entry) => ({
  id: `favorite:${entry.fullPath}`,
  title: entry.title,
  route: entry.route,
  fullPath: entry.fullPath,
  module: entry.module || '',
  pageType: entry.pageType || '',
  icon: entry.icon || '',
  summary: entry.summary || '',
  createdAt: new Date().toISOString(),
  source: 'local'
})

const shouldRecordRoute = (route) => {
  const meta = resolveRouteMeta(route)

  if (!route.path) {
    return false
  }

  if (meta.pageType === 'auth') {
    return false
  }

  return Boolean(meta.title)
}

export const useProductivityStore = defineStore('productivity', () => {
  const initialState = readProductivityState()
  const recentVisits = ref(initialState.recentVisits.slice(0, MAX_RECENT_VISITS))
  const favorites = ref(initialState.favorites.slice(0, MAX_FAVORITES))

  const persist = () => {
    persistProductivityState({
      recentVisits: recentVisits.value,
      favorites: favorites.value
    })
  }

  const recordVisit = (route) => {
    if (!shouldRecordRoute(route)) {
      return
    }

    const routeEntry = buildRouteEntry(route)

    if (!routeEntry.fullPath) {
      return
    }

    const entry = {
      id: `route:${routeEntry.fullPath}`,
      ...routeEntry,
      visitedAt: new Date().toISOString()
    }

    recentVisits.value = [
      entry,
      ...recentVisits.value.filter((item) => item.fullPath !== entry.fullPath)
    ].slice(0, MAX_RECENT_VISITS)

    persist()
  }

  const isFavorited = (fullPath) => {
    const normalizedFullPath = normalizeTargetPath(fullPath)
    return favorites.value.some((item) => item.fullPath === normalizedFullPath)
  }

  const toggleFavorite = (route) => {
    const routeEntry = buildRouteEntry(route)
    const entry = createFavoriteEntry(routeEntry)

    const exists = favorites.value.find((item) => item.fullPath === routeEntry.fullPath)

    if (exists) {
      favorites.value = favorites.value.filter((item) => item.fullPath !== routeEntry.fullPath)
    } else {
      favorites.value = [entry, ...favorites.value].slice(0, MAX_FAVORITES)
    }

    persist()
  }

  const toggleFavoriteEntry = (entry) => {
    const normalizedFullPath = normalizeTargetPath(entry?.fullPath || entry?.route || '')

    if (!normalizedFullPath) {
      return
    }

    const nextEntry = createFavoriteEntry({
      ...entry,
      route: normalizeTargetPath(entry?.route || normalizedFullPath) || normalizedFullPath.split('?')[0],
      fullPath: normalizedFullPath
    })
    const exists = favorites.value.find((item) => item.fullPath === normalizedFullPath)

    if (exists) {
      favorites.value = favorites.value.filter((item) => item.fullPath !== normalizedFullPath)
    } else {
      favorites.value = [nextEntry, ...favorites.value].slice(0, MAX_FAVORITES)
    }

    persist()
  }

  const removeFavorite = (fullPath) => {
    const normalizedFullPath = normalizeTargetPath(fullPath)
    favorites.value = favorites.value.filter((item) => item.fullPath !== normalizedFullPath)
    persist()
  }

  const clearRecentVisits = () => {
    recentVisits.value = []
    persist()
  }

  const quickContinueItems = computed(() => {
    return recentVisits.value.slice(0, 6)
  })

  return {
    recentVisits,
    favorites,
    quickContinueItems,
    recordVisit,
    toggleFavorite,
    toggleFavoriteEntry,
    removeFavorite,
    isFavorited,
    clearRecentVisits
  }
})
