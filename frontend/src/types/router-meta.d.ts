/// <reference types="vite/client" />

import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    description?: string
    module?: string
    pageType?: string
    icon?: string
    keepAlive?: boolean
    hidden?: boolean
    parentTitle?: string
    activeMenu?: string
    requiresAuth?: boolean
    requiresGuest?: boolean
  }
}

export {}
