import {
  inject,
  markRaw,
  onActivated,
  onBeforeUnmount,
  onDeactivated,
  onMounted,
  provide,
  readonly,
  shallowRef,
  unref,
  watchEffect
} from 'vue'

const PLATFORM_PAGE_HEADER_KEY = Symbol('platform-page-header')

const createEmptyHeaderState = () => ({
  title: '',
  description: '',
  resolvedIcon: null,
  statusTags: [],
  metaItems: [],
  helperText: '',
  updateText: '',
  actions: []
})

const normalizeHeaderConfig = (config = {}) => {
  const nextConfig = {
    ...createEmptyHeaderState(),
    ...(config || {})
  }

  if (nextConfig.resolvedIcon) {
    nextConfig.resolvedIcon = markRaw(nextConfig.resolvedIcon)
  }

  nextConfig.actions = (nextConfig.actions || []).map((action) => ({
    ...action,
    icon: action?.icon ? markRaw(action.icon) : action?.icon || null
  }))

  return nextConfig
}

const resolveHeaderSource = (source) => {
  if (!source) {
    return createEmptyHeaderState()
  }

  const resolved = typeof source === 'function' ? source() : unref(source)
  return normalizeHeaderConfig(resolved)
}

export function createPlatformPageHeaderController() {
  const pageHeader = shallowRef(createEmptyHeaderState())

  const setPageHeader = (config = {}) => {
    pageHeader.value = normalizeHeaderConfig(config)
  }

  const resetPageHeader = () => {
    pageHeader.value = createEmptyHeaderState()
  }

  return {
    pageHeader: readonly(pageHeader),
    setPageHeader,
    resetPageHeader
  }
}

export function providePlatformPageHeader(controller) {
  provide(PLATFORM_PAGE_HEADER_KEY, controller)
}

export function usePlatformPageHeader(source) {
  const controller = inject(PLATFORM_PAGE_HEADER_KEY, null)

  if (!controller) {
    return {
      setPageHeader: () => {},
      resetPageHeader: () => {}
    }
  }

  if (!source) {
    return controller
  }

  let stopSync = null

  const startSync = () => {
    if (stopSync) {
      return
    }

    stopSync = watchEffect(() => {
      controller.setPageHeader(resolveHeaderSource(source))
    })
  }

  const stopAndReset = () => {
    if (stopSync) {
      stopSync()
      stopSync = null
    }

    controller.resetPageHeader()
  }

  onMounted(startSync)
  onActivated(startSync)
  onDeactivated(stopAndReset)
  onBeforeUnmount(stopAndReset)

  return controller
}
