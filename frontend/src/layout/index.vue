<template>
  <div class="platform-layout">
    <PlatformGlobalHeader
      :logo-src="logoSvg"
      :top-level-items="topLevelItems"
      :current-module-key="currentModuleKey"
      :show-project-context="showProjectContext"
      :language-code="appStore.language"
      :language-label="currentLanguage"
      :user="userStore.user"
      @go-home="router.push('/home')"
      @navigate-module="handleModuleNavigate"
      @open-placeholder="handlePlaceholderAction"
      @open-global-search="openSearchDialog"
      @toggle-productivity-panel="toggleProductivityPanel"
      @open-assistant="router.push('/ai-generation/assistant')"
      @language-change="handleLanguageChange"
      @user-command="handleUserCommand"
    />

    <PlatformSearchDialog
      :model-value="searchStore.isOpen"
      :query="searchStore.query"
      :groups="searchStore.resultGroups"
      :loading="searchStore.loading"
      @open="openSearchDialog"
      @update:modelValue="handleSearchDialogToggle"
      @update:query="searchStore.setQuery"
      @navigate="handleSearchNavigate"
    />

    <div v-if="activeProductivityPanel" class="platform-layout__overlay" @click="activeProductivityPanel = ''">
      <div class="platform-layout__productivity-popover" @click.stop>
        <PlatformProductivityPanel
          v-if="activeProductivityPanel === 'recent-visits'"
          title="最近访问"
          description="第一版本地记录最近打开的页面，可直接继续访问或加入收藏。"
          :items="productivityStore.recentVisits"
          empty-title="暂无最近访问"
          empty-description="访问任意页面后会自动出现在这里。"
          show-clear
          clear-text="清空"
          show-favorite-action
          favorite-action-text="收藏"
          @navigate="handleProductivityNavigate"
          @toggle-favorite="handleToggleFavoriteFromPanel"
          @clear="productivityStore.clearRecentVisits"
        />
        <PlatformProductivityPanel
          v-else
          title="收藏"
          description="第一版只支持当前页或入口级收藏，不扩张到复杂资产收藏体系。"
          :items="productivityStore.favorites"
          empty-title="暂无收藏"
          empty-description="可通过页面头部收藏当前页，或在最近访问面板里收藏入口。"
          show-remove-action
          remove-action-text="取消收藏"
          @navigate="handleProductivityNavigate"
          @remove="handleRemoveFavorite"
        />
      </div>
    </div>

    <div class="platform-layout__shell">
      <PlatformSidebar
        :collapsed="sidebarCollapsed"
        :module-title="currentModuleTitle"
        :items="sidebarItems"
        :active-menu="currentActiveMenu"
        @toggle-collapse="sidebarCollapsed = !sidebarCollapsed"
        @navigate="handleSidebarNavigate"
      />

      <div class="platform-layout__content">
        <PlatformPageHeader
          :breadcrumb-items="breadcrumbItems"
          :module-name="moduleName"
          :page-type-label="pageTypeLabel"
          :page-title="pageTitle"
          :description="pageDescription"
          :resolved-icon="pageIconComponent"
          :status-tags="pageStatusTags"
          :meta-items="pageMetaItems"
          :helper-text="pageHelperText"
          :update-text="pageUpdateText"
          :actions="combinedPageActions"
        />

        <main ref="mainContentRef" class="platform-layout__main">
          <router-view v-slot="{ Component, route: currentRoute }">
            <keep-alive>
              <component
                :is="Component"
                v-if="currentRoute.meta.keepAlive"
                :key="currentRoute.name || currentRoute.path"
              />
            </keep-alive>
            <component
              :is="Component"
              v-if="!currentRoute.meta.keepAlive"
              :key="currentRoute.fullPath"
            />
          </router-view>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Aim,
  AlarmClock,
  Bell,
  ChatDotRound,
  Check,
  Collection,
  Connection,
  Cpu,
  DataAnalysis,
  Document,
  DocumentCopy,
  Edit,
  Flag,
  Folder,
  FolderOpened,
  House,
  Link,
  MagicStick,
  Monitor,
  Odometer,
  Setting,
  Timer,
  User,
  UserFilled,
  VideoPlay,
  Warning,
  MoreFilled
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { useProductivityStore } from '@/stores/productivity'
import { usePlatformSearchStore } from '@/stores/platform-search'
import { useI18n } from 'vue-i18n'
import {
  buildBreadcrumbItems,
  getModuleLabel,
  getPageTypeLabel,
  resolveRouteMeta
} from '@/router/route-meta'
import { buildDeeplinkLocation } from '@/router/deeplink'
import {
  getCurrentModuleDefinition,
  getModuleSidebarItems,
  getTopLevelPlatformNav,
  shouldShowProjectContext
} from './platform-layout'
import {
  createPlatformPageHeaderController,
  providePlatformPageHeader
} from './usePlatformPageHeader'
import PlatformGlobalHeader from './components/PlatformGlobalHeader.vue'
import PlatformProductivityPanel from './components/PlatformProductivityPanel.vue'
import PlatformSearchDialog from './components/PlatformSearchDialog.vue'
import PlatformSidebar from './components/PlatformSidebar.vue'
import PlatformPageHeader from './components/PlatformPageHeader.vue'
import logoSvg from '@/assets/images/logo.svg'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const appStore = useAppStore()
const productivityStore = useProductivityStore()
const searchStore = usePlatformSearchStore()
const { t } = useI18n()

const sidebarCollapsed = ref(false)
const activeProductivityPanel = ref('')
const mainContentRef = ref(null)
const pageHeaderController = createPlatformPageHeaderController()

providePlatformPageHeader(pageHeaderController)
searchStore.initializeStaticIndex(router.getRoutes())

const iconMap = {
  aim: Aim,
  'alarm-clock': AlarmClock,
  bell: Bell,
  chat: ChatDotRound,
  check: Check,
  collection: Collection,
  connection: Connection,
  cpu: Cpu,
  'data-analysis': DataAnalysis,
  document: Document,
  'document-copy': DocumentCopy,
  edit: Edit,
  flag: Flag,
  folder: Folder,
  'folder-opened': FolderOpened,
  house: House,
  link: Link,
  'magic-stick': MagicStick,
  monitor: Monitor,
  odometer: Odometer,
  setting: Setting,
  timer: Timer,
  user: User,
  'user-plus': UserFilled,
  'video-play': VideoPlay,
  sparkles: MagicStick,
  login: UserFilled,
  warning: Warning,
  more: MoreFilled
}

const currentLanguage = computed(() => {
  return appStore.language === 'zh-cn' ? '简体中文' : 'English'
})

const routeMeta = computed(() => resolveRouteMeta(route))
const currentModuleKey = computed(() => {
  return routeMeta.value.module || getCurrentModuleDefinition(route.path)?.key || 'workbench'
})
const currentModule = computed(() => getCurrentModuleDefinition(route.path, currentModuleKey.value))
const topLevelItems = computed(() => getTopLevelPlatformNav())

const currentModuleTitle = computed(() => {
  return getModuleLabel(currentModuleKey.value) || currentModule.value?.title || '平台'
})

const moduleName = computed(() => {
  return getModuleLabel(routeMeta.value.module) || currentModuleTitle.value
})

const pageTitle = computed(() => {
  return pageHeaderController.pageHeader.value.title || routeMeta.value.title || moduleName.value || 'TestHub'
})

const pageTypeLabel = computed(() => getPageTypeLabel(routeMeta.value.pageType))
const currentActiveMenu = computed(() => routeMeta.value.activeMenu || route.path)
const breadcrumbItems = computed(() => buildBreadcrumbItems(route))
const pageDescription = computed(() => {
  return (
    pageHeaderController.pageHeader.value.description ||
    routeMeta.value.description ||
    topLevelItems.value.find((item) => item.key === currentModuleKey.value)?.description ||
    ''
  )
})
const showProjectContext = computed(() => shouldShowProjectContext(currentModuleKey.value))
const pageIconComponent = computed(() => {
  return pageHeaderController.pageHeader.value.resolvedIcon || iconMap[routeMeta.value.icon] || null
})
const pageStatusTags = computed(() => pageHeaderController.pageHeader.value.statusTags || [])
const pageMetaItems = computed(() => pageHeaderController.pageHeader.value.metaItems || [])
const pageHelperText = computed(() => pageHeaderController.pageHeader.value.helperText || '')
const pageUpdateText = computed(() => pageHeaderController.pageHeader.value.updateText || '')
const pageActions = computed(() => pageHeaderController.pageHeader.value.actions || [])
const isCurrentPageFavorited = computed(() => productivityStore.isFavorited(route.fullPath))
const combinedPageActions = computed(() => {
  const favoriteAction = {
    key: 'toggle-favorite',
    label: isCurrentPageFavorited.value ? '取消收藏' : '收藏当前页',
    plain: true,
    icon: Flag,
    onClick: () => {
      const nextState = !isCurrentPageFavorited.value
      productivityStore.toggleFavorite(route)
      ElMessage.success(nextState ? '已加入收藏' : '已取消收藏')
    }
  }

  return [...pageActions.value, favoriteAction]
})

const routeIconMap = computed(() => {
  const result = new Map()
  router.getRoutes().forEach((routeRecord) => {
    if (routeRecord.path && routeRecord.meta?.icon) {
      result.set(routeRecord.path, iconMap[routeRecord.meta.icon] || null)
    }
  })
  return result
})

const sidebarItems = computed(() => {
  return getModuleSidebarItems(currentModuleKey.value, route.path).map((item) => ({
    ...item,
    key: item.path || `${currentModuleKey.value}-${item.title}`,
    iconComponent: routeIconMap.value.get(item.path) || null
  }))
})

const handleLanguageChange = (lang) => {
  appStore.setLanguage(lang)
  ElMessage.success(lang === 'zh-cn' ? '语言已切换为中文' : 'Language switched to English')
}

const handleModuleNavigate = (item) => {
  if (item.route) {
    router.push(item.route)
  }
}

const handleSidebarNavigate = (item) => {
  if (item.path) {
    router.push(item.path)
  }
}

const handlePlaceholderAction = (type) => {
  const messages = {
    'project-context': '项目上下文切换将在阶段 1.2 后补齐，本轮先保留平台壳入口。',
    notifications: '平台级消息中心属于后续能力，本轮先保留入口占位。'
  }

  ElMessage.info(messages[type] || '该入口将在后续阶段补齐。')
}

const toggleProductivityPanel = (type) => {
  searchStore.closeSearch()
  activeProductivityPanel.value = activeProductivityPanel.value === type ? '' : type
}

const openSearchDialog = () => {
  activeProductivityPanel.value = ''
  searchStore.openSearch()
}

const handleSearchDialogToggle = (nextValue) => {
  if (nextValue) {
    openSearchDialog()
    return
  }

  searchStore.closeSearch()
}

const handleProductivityNavigate = (item) => {
  const sourceType = activeProductivityPanel.value === 'favorites' ? 'favorite' : 'recent'
  activeProductivityPanel.value = ''

  if (item?.fullPath) {
    const nextLocation = buildDeeplinkLocation({
      target: item.fullPath,
      currentRoute: route,
      sourceType,
      sourceTitle: sourceType === 'favorite' ? '收藏' : '最近访问'
    })

    if (nextLocation) {
      router.push(nextLocation)
      return
    }

    router.push(item.fullPath)
    return
  }

  if (item?.route) {
    const nextLocation = buildDeeplinkLocation({
      target: item.route,
      currentRoute: route,
      sourceType,
      sourceTitle: sourceType === 'favorite' ? '收藏' : '最近访问'
    })

    if (nextLocation) {
      router.push(nextLocation)
      return
    }

    router.push(item.route)
  }
}

const handleSearchNavigate = (item) => {
  searchStore.closeSearch()

  const target = item?.fullPath || item?.route

  if (target) {
    const nextLocation = buildDeeplinkLocation({
      target,
      currentRoute: route,
      sourceType: 'search',
      sourceTitle: '全局搜索'
    })

    if (nextLocation) {
      router.push(nextLocation)
      return
    }

    router.push(target)
  }
}

const handleToggleFavoriteFromPanel = (item) => {
  const nextState = !productivityStore.isFavorited(item.fullPath)
  productivityStore.toggleFavoriteEntry(item)
  ElMessage.success(nextState ? '已加入收藏' : '已取消收藏')
}

const handleRemoveFavorite = (item) => {
  productivityStore.removeFavorite(item.fullPath)
  ElMessage.success('已取消收藏')
}

const handleUserCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    ElMessage.success(t('nav.logout'))
    return
  }

  if (command === 'profile') {
    router.push('/ai-generation/profile')
  }
}

watch(
  () => route.path,
  async () => {
    await nextTick()

    if (mainContentRef.value) {
      mainContentRef.value.scrollTop = 0
      mainContentRef.value.scrollLeft = 0
    }
  }
)
</script>

<style scoped lang="scss">
.platform-layout {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #eef2f7;
}

.platform-layout__overlay {
  position: fixed;
  top: 76px;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  justify-content: flex-end;
  padding: 0 20px 20px;
  z-index: 1200;
}

.platform-layout__productivity-popover {
  width: 348px;
  height: fit-content;
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 24px 56px rgba(15, 23, 42, 0.16);
}

.platform-layout__shell {
  display: flex;
  flex: 1;
  min-height: 0;
  min-width: 0;
}

.platform-layout__content {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}

.platform-layout__main {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(56, 189, 248, 0.08), transparent 24%),
    linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
}

.platform-layout__main > :deep(*) {
  min-width: 0;
}

.platform-layout__main :deep(.page-container),
.platform-layout__main :deep(.dashboard-container),
.platform-layout__main :deep(.interface-management),
.platform-layout__main :deep(.app-automation-page),
.platform-layout__main :deep(.data-factory-page) {
  min-height: 0;
}

@media (max-width: 960px) {
  .platform-layout__overlay {
    top: 72px;
    right: 0;
    left: 0;
    padding: 0 16px 16px;
  }

  .platform-layout__productivity-popover {
    width: 100%;
  }

  .platform-layout__main {
    padding: 16px;
  }
}
</style>
