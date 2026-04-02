<template>
  <div class="home-workbench">
    <StateLoading
      v-if="homePageState === UI_PAGE_STATE.LOADING"
      :title="$t('common.uiState.loading.title')"
      :description="$t('common.uiState.loading.description')"
    />
    <StateEmpty
      v-else-if="homePageState === UI_PAGE_STATE.EMPTY"
      :title="$t('common.uiState.empty.title')"
      description="工作台可用入口为空，请先检查导航配置是否已接入。"
    />
    <DashboardShell v-else class="home-shell">
      <template #metrics>
        <section class="welcome-panel">
          <div class="welcome-panel__copy">
            <span class="welcome-panel__eyebrow">{{ greetingText }}</span>
            <h2 class="welcome-panel__headline">{{ welcomeHeadline }}</h2>
            <p class="welcome-panel__summary">
              {{ currentWorkNote }}
            </p>
            <p class="welcome-panel__hint">
              首页只承接平台级继续工作、常用入口和轻量提醒，不复制各模块 dashboard。
            </p>
            <div class="welcome-panel__meta">
              <span class="context-chip">工作说明：{{ workModeText }}</span>
              <span class="context-chip">最近访问：{{ productivityStore.recentVisits.length }} 条</span>
              <span class="context-chip">我的收藏：{{ favoriteItems.length }} 条</span>
            </div>
          </div>

          <div class="welcome-panel__aside">
            <div class="context-card">
              <span class="context-card__label">当前上下文</span>
              <div class="context-card__item">
                <span>当前用户</span>
                <strong>{{ userLabel }}</strong>
              </div>
              <div class="context-card__item">
                <span>当前入口</span>
                <strong>统一工作台首页</strong>
              </div>
              <div class="context-card__item">
                <span>工作模式</span>
                <strong>{{ workModeText }}</strong>
              </div>
            </div>
          </div>
        </section>
      </template>

      <template #overview>
        <section class="stats-section">
          <el-row :gutter="18">
            <el-col v-for="card in overviewCards" :key="card.key" :xs="24" :sm="12" :xl="6">
              <StatCard
                :title="card.title"
                :value="card.value"
                :description="card.description"
                :icon="card.icon"
                :accent="card.accent"
                compact
              />
            </el-col>
          </el-row>
        </section>
      </template>

      <section class="section-block">
        <div class="section-heading">
          <div>
            <h3 class="section-title">我的工作</h3>
            <p class="section-description">优先回到最近工作和常用入口，不再展示假待办和假风险数字。</p>
          </div>
        </div>
        <div class="my-work-grid">
          <QuickActionCard
            v-for="card in myWorkCards"
            :key="card.key"
            :title="card.title"
            :description="card.description"
            :icon="card.icon"
            :accent="card.accent"
            :badge="card.badge"
            variant="compact"
            :clickable="Boolean(card.route)"
            :disabled="!card.route"
            @click="card.route && navigateTo(card.route)"
          >
            <span class="quick-note">{{ card.note }}</span>
          </QuickActionCard>
        </div>
      </section>

      <section class="section-block">
        <RecentList
          title="快捷继续"
          description="这里直接消费真实最近访问记录，方便回到刚刚做过的页面。"
          :items="quickContinueItems"
          empty-title="暂无可继续事项"
          empty-description="访问任意页面后，这里会自动出现最近访问记录。"
        >
          <template #actions>
            <el-button
              v-if="quickContinueItems.length"
              text
              type="primary"
              @click="productivityStore.clearRecentVisits()"
            >
              清空记录
            </el-button>
          </template>
          <template #item="{ item }">
            <div class="stream-item">
              <div class="stream-item__icon" :class="`accent-${item.accent}`">
                <el-icon><component :is="item.icon" /></el-icon>
              </div>
              <div class="stream-item__body">
                <div class="stream-item__top">
                  <span class="stream-item__type">{{ item.type }}</span>
                  <span class="stream-item__tag">{{ item.tag }}</span>
                </div>
                <div class="stream-item__title">{{ item.title }}</div>
                <p class="stream-item__description">{{ item.description }}</p>
              </div>
              <el-button text type="primary" @click="navigateTo(item.route)">继续</el-button>
            </div>
          </template>
        </RecentList>
      </section>

      <section class="section-block">
        <div class="section-heading">
          <div>
            <h3 class="section-title">核心模块入口</h3>
            <p class="section-description">直接复用平台导航真源，不再在首页重复长出一套模块体系。</p>
          </div>
        </div>
        <div class="module-grid">
          <QuickActionCard
            v-for="module in coreModules"
            :key="module.key"
            :title="module.title"
            :description="module.description"
            :icon="module.icon"
            :accent="module.accent"
            :badge="module.badge"
            @click="navigateTo(module.route)"
          />
        </div>
      </section>

      <template #secondary>
        <div class="aside-stack">
          <RecentList
            title="我的收藏"
            description="这里展示已收藏的常用页面，方便直接进入高频入口。"
            :items="favoriteItems"
            empty-title="暂无收藏入口"
            empty-description="在页面右上角收藏常用页面后，这里会自动出现。"
          >
            <template #item="{ item }">
              <div class="stream-item">
                <div class="stream-item__icon" :class="`accent-${item.accent}`">
                  <el-icon><component :is="item.icon" /></el-icon>
                </div>
                <div class="stream-item__body">
                  <div class="stream-item__top">
                    <span class="stream-item__type">{{ item.type }}</span>
                    <span class="stream-item__tag">{{ item.tag }}</span>
                  </div>
                  <div class="stream-item__title">{{ item.title }}</div>
                  <p class="stream-item__description">{{ item.description }}</p>
                </div>
                <div class="stream-item__actions">
                  <el-button text type="primary" @click="navigateTo(item.route)">打开</el-button>
                  <el-button text type="danger" @click="productivityStore.removeFavorite(item.fullPath)">移除</el-button>
                </div>
              </div>
            </template>
          </RecentList>
        </div>
      </template>
    </DashboardShell>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useProductivityStore } from '@/stores/productivity'
import {
  ChatDotRound,
  Clock,
  Collection,
  DataLine,
  FolderOpened,
  Link,
  MagicStick,
  Monitor,
  Setting,
  Cellphone,
  Tools,
  User
} from '@element-plus/icons-vue'
import { TOP_LEVEL_NAVIGATION } from '@/config/navigation'
import { getModuleEntry, getModuleLabel } from '@/router/route-meta'
import { QuickActionCard, RecentList, StatCard } from '@/components/platform-shared'
import { DashboardShell } from '@/components/page-shells'
import { StateEmpty, StateLoading, UI_PAGE_STATE } from '@/components/ui-states'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'
import { buildDeeplinkLocation } from '@/router/deeplink'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const productivityStore = useProductivityStore()

const topLevelNavMap = new Map(TOP_LEVEL_NAVIGATION.map((item) => [item.key, item]))

const coreModuleDefinitions = [
  { key: 'test-design', icon: MagicStick, accent: 'cyan', badge: '设计' },
  { key: 'api-automation', icon: Link, accent: 'blue', badge: '接口' },
  { key: 'web-automation', icon: Monitor, accent: 'green', badge: 'Web' },
  { key: 'app-automation', icon: Cellphone, accent: 'pink', badge: 'App' },
  { key: 'data-factory', icon: DataLine, accent: 'orange', badge: '数据' },
  { key: 'config-center', icon: Setting, accent: 'slate', badge: '配置' },
  { key: 'system-management', icon: User, accent: 'purple', badge: '系统' }
]

const iconAccentMap = {
  house: { icon: FolderOpened, accent: 'cyan' },
  folder: { icon: FolderOpened, accent: 'cyan' },
  'folder-opened': { icon: FolderOpened, accent: 'cyan' },
  link: { icon: Link, accent: 'blue' },
  monitor: { icon: Monitor, accent: 'green' },
  setting: { icon: Setting, accent: 'slate' },
  chat: { icon: ChatDotRound, accent: 'purple' },
  'magic-stick': { icon: MagicStick, accent: 'cyan' },
  'data-analysis': { icon: DataLine, accent: 'orange' },
  user: { icon: User, accent: 'purple' }
}

const userLabel = computed(() => userStore.user?.username || '平台成员')

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 11) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const welcomeHeadline = computed(() => `${greetingText.value}，${userLabel.value}`)

const workModeText = computed(() => {
  return userStore.user ? '继续当前测试平台工作' : '等待用户信息加载'
})

const currentWorkNote = computed(() => {
  if (productivityStore.quickContinueItems.length > 0) {
    return `${userLabel.value}，建议先从“快捷继续”或“我的收藏”进入，再切到具体模块继续处理。`
  }
  return `${userLabel.value}，可以先从核心模块入口进入，再逐步建立自己的最近访问和收藏入口。`
})

const coreModules = computed(() => {
  return coreModuleDefinitions.map((item) => {
    const navMeta = topLevelNavMap.get(item.key)
    return {
      ...item,
      title: navMeta?.title || item.key,
      description: navMeta?.description || '平台工作域入口。',
      route: getModuleEntry(item.key) || navMeta?.route || '/home'
    }
  })
})

const quickContinueItems = computed(() => {
  return productivityStore.quickContinueItems.map((item) => {
    const visual = iconAccentMap[item.icon] || { icon: FolderOpened, accent: 'cyan' }
    return {
      id: item.id,
      type: '最近访问',
      tag: getModuleLabel(item.module) || '本地记录',
      title: item.title,
      description: item.summary || '继续回到最近访问的页面。',
      route: item.fullPath,
      fullPath: item.fullPath,
      icon: visual.icon,
      accent: visual.accent
    }
  })
})

const favoriteItems = computed(() => {
  return productivityStore.favorites.map((item) => {
    const visual = iconAccentMap[item.icon] || { icon: Collection, accent: 'purple' }
    return {
      id: item.id,
      type: '收藏入口',
      tag: getModuleLabel(item.module) || '常用页面',
      title: item.title,
      description: item.summary || '已收藏的常用页面。',
      route: item.fullPath,
      fullPath: item.fullPath,
      icon: visual.icon,
      accent: visual.accent
    }
  })
})

const overviewCards = computed(() => ([
  {
    key: 'recent-visits',
    title: '最近访问',
    value: productivityStore.recentVisits.length,
    description: '真实本地记录，自动收集最近访问页面。',
    icon: Clock,
    accent: 'blue'
  },
  {
    key: 'quick-continue',
    title: '快捷继续',
    value: quickContinueItems.value.length,
    description: '首页直接展示最近可继续的工作入口。',
    icon: Tools,
    accent: 'green'
  },
  {
    key: 'favorites',
    title: '我的收藏',
    value: favoriteItems.value.length,
    description: '来自真实收藏能力，不再展示占位卡片。',
    icon: Collection,
    accent: 'purple'
  },
  {
    key: 'modules',
    title: '已接入工作域',
    value: coreModules.value.length,
    description: '来自平台导航真源的真实模块入口数。',
    icon: DataLine,
    accent: 'orange'
  }
]))

const myWorkCards = computed(() => {
  const latestVisit = quickContinueItems.value[0]
  const latestFavorite = favoriteItems.value[0]

  return [
    {
      key: 'continue-latest',
      title: latestVisit ? '继续最近页面' : '等待最近访问',
      description: latestVisit ? latestVisit.title : '访问任意业务页面后，这里会自动出现可继续入口。',
      badge: latestVisit ? latestVisit.tag : '空',
      icon: latestVisit?.icon || Clock,
      accent: latestVisit?.accent || 'blue',
      route: latestVisit?.route || '',
      note: latestVisit ? '直接回到刚刚工作过的页面' : '当前还没有最近访问记录'
    },
    {
      key: 'open-favorite',
      title: latestFavorite ? '打开常用收藏' : '建立常用收藏',
      description: latestFavorite ? latestFavorite.title : '在常用页面右上角收藏后，这里会自动显示最近收藏入口。',
      badge: latestFavorite ? latestFavorite.tag : '提示',
      icon: latestFavorite?.icon || Collection,
      accent: latestFavorite?.accent || 'purple',
      route: latestFavorite?.route || '',
      note: latestFavorite ? '优先进入高频页面' : '收藏能力已经接入首页展示'
    },
    {
      key: 'continue-design',
      title: '进入测试设计',
      description: '直接回到测试设计主链，继续项目、用例和评审处理。',
      badge: '入口',
      icon: MagicStick,
      accent: 'cyan',
      route: '/ai-generation/projects',
      note: '当前最稳定的继续工作入口'
    }
  ]
})

const homePageState = computed(() => {
  if (Boolean(userStore.accessToken) && !userStore.user) {
    return UI_PAGE_STATE.LOADING
  }
  return coreModules.value.length ? UI_PAGE_STATE.READY : UI_PAGE_STATE.EMPTY
})

usePlatformPageHeader(() => ({
  description: '平台工作台优先承接继续工作、常用入口和轻量信息，不复制各模块 dashboard。',
  statusTags: [
    {
      label: '工作台首页',
      type: 'primary'
    }
  ],
  helperText: '首页已经接入最近访问和收藏能力；项目上下文、平台待办和全局搜索继续保持独立接入边界。',
  metaItems: [
    { label: '当前用户', value: userLabel.value },
    { label: '工作域', value: `${coreModules.value.length} 个` },
    { label: '最近访问', value: `${productivityStore.recentVisits.length} 条` },
    { label: '我的收藏', value: `${favoriteItems.value.length} 条` }
  ],
  actions: [
    {
      key: 'test-design',
      label: '进入测试设计',
      type: 'primary',
      icon: MagicStick,
      onClick: () => navigateTo('/ai-generation/requirement-analysis')
    },
    {
      key: 'assistant',
      label: 'AI 助手',
      plain: true,
      icon: ChatDotRound,
      onClick: () => navigateTo('/ai-generation/assistant')
    }
  ]
}))

const navigateTo = (path) => {
  if (!path) {
    return
  }

  const nextLocation = buildDeeplinkLocation({
    target: path,
    currentRoute: route,
    sourceType: 'home',
    sourceTitle: '工作台'
  })

  if (nextLocation) {
    router.push(nextLocation)
    return
  }

  router.push(path)
}
</script>

<style scoped lang="scss">
.home-workbench {
  min-height: 100%;
}

.home-shell {
  gap: 24px;
}

.welcome-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(260px, 0.9fr);
  gap: 18px;
  padding: 22px 24px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(56, 189, 248, 0.08), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.94) 100%);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
}

.welcome-panel__copy {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.welcome-panel__eyebrow {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 6px 10px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 12px;
  font-weight: 700;
}

.welcome-panel__headline {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.welcome-panel__summary,
.welcome-panel__hint {
  margin: 0;
  max-width: 780px;
  line-height: 1.8;
  color: #475569;
}

.welcome-panel__hint {
  font-size: 14px;
  color: #64748b;
}

.welcome-panel__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.context-chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(226, 232, 240, 0.6);
  color: #475569;
  font-size: 12px;
}

.context-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  height: 100%;
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.context-card__label {
  font-size: 13px;
  font-weight: 700;
  color: #0369a1;
}

.context-card__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  font-size: 14px;
  color: #475569;
}

.context-card__item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.context-card__item strong {
  color: #0f172a;
}

.section-block {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
}

.section-description {
  margin: 6px 0 0;
  color: #64748b;
  line-height: 1.7;
}

.my-work-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
}

.aside-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

:deep(.home-shell .shell-main),
:deep(.home-shell .shell-secondary) {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

:deep(.home-shell .shell-body.has-secondary) {
  grid-template-columns: minmax(0, 1.72fr) minmax(320px, 0.9fr);
  align-items: start;
}

:deep(.home-shell .shell-secondary) {
  position: sticky;
  top: 0;
}

.stream-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.82);
}

.stream-item:last-child {
  border-bottom: none;
}

.stream-item__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  flex-shrink: 0;
  background: rgba(226, 232, 240, 0.7);
  color: #334155;
}

.stream-item__icon.accent-blue {
  background: rgba(59, 130, 246, 0.14);
  color: #1d4ed8;
}

.stream-item__icon.accent-cyan {
  background: rgba(6, 182, 212, 0.16);
  color: #0f766e;
}

.stream-item__icon.accent-purple {
  background: rgba(124, 58, 237, 0.16);
  color: #6d28d9;
}

.stream-item__icon.accent-orange {
  background: rgba(249, 115, 22, 0.16);
  color: #c2410c;
}

.stream-item__icon.accent-green {
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
}

.stream-item__icon.accent-slate {
  background: rgba(100, 116, 139, 0.16);
  color: #334155;
}

.stream-item__body {
  flex: 1;
  min-width: 0;
}

.stream-item__top {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 6px;
}

.stream-item__type {
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
}

.stream-item__tag {
  font-size: 12px;
  color: #64748b;
}

.stream-item__title {
  color: #0f172a;
  font-weight: 700;
}

.stream-item__description {
  margin: 6px 0 0;
  color: #64748b;
  line-height: 1.7;
}

.stream-item__actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.quick-note {
  font-size: 12px;
  color: #64748b;
}

@media (max-width: 1200px) {
  .welcome-panel {
    grid-template-columns: 1fr;
  }

  .my-work-grid {
    grid-template-columns: 1fr;
  }

  :deep(.home-shell .shell-body.has-secondary) {
    grid-template-columns: minmax(0, 1fr);
  }

  :deep(.home-shell .shell-secondary) {
    position: static;
  }
}

@media (max-width: 768px) {
  .welcome-panel {
    padding: 18px;
  }

  .welcome-panel__headline {
    font-size: 24px;
  }

  .module-grid {
    grid-template-columns: 1fr;
  }

  .stream-item {
    flex-wrap: wrap;
  }

  .stream-item__actions {
    width: 100%;
    flex-direction: row;
    justify-content: flex-start;
  }
}
</style>
