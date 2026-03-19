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
    <template v-else>
      <section class="welcome-panel">
        <div class="welcome-panel__copy">
          <span class="welcome-panel__eyebrow">{{ greetingText }}</span>
          <h2 class="welcome-panel__headline">{{ welcomeHeadline }}</h2>
          <p class="welcome-panel__summary">
            {{ currentWorkNote }}
          </p>
          <p class="welcome-panel__hint">
            当前首页优先承接继续工作、模块入口和轻提醒，不复制各模块 dashboard，也不提前打开最近访问、收藏或全局搜索的真实能力。
          </p>
          <div class="welcome-panel__meta">
            <span class="context-chip">项目上下文：阶段 1 占位展示，后续由统一项目上下文能力接入</span>
            <span class="context-chip">工作说明：{{ workModeText }}</span>
            <span class="context-chip">数据边界：真数据 + 占位结构</span>
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
              <span>项目上下文</span>
              <strong>阶段 1 占位</strong>
            </div>
          </div>
        </div>
      </section>

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

      <section class="section-block">
        <div class="section-heading">
          <div>
            <h3 class="section-title">我的工作</h3>
            <p class="section-description">先告诉用户现在可以继续什么，而不是只展示模块目录。</p>
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
            @click="card.route && navigateTo(card.route)"
          >
            <span class="quick-note">{{ card.note }}</span>
          </QuickActionCard>
        </div>
      </section>

      <section class="section-block">
        <div class="section-heading">
          <div>
            <h3 class="section-title">核心模块入口</h3>
            <p class="section-description">复用平台导航真源，不再重新做一套首页模块体系。</p>
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

      <el-row :gutter="18" class="workspace-streams">
        <el-col :xs="24" :xl="12">
          <RecentList
            title="快捷继续"
            description="当前直接消费真实最近访问记录；收藏保留独立心智，不混入快捷继续。"
            :items="quickContinueItems"
            empty-title="暂无可继续事项"
            empty-description="访问任意页面后，这里会自动出现最近访问记录。"
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
                <el-button text type="primary" @click="navigateTo(item.route)">继续</el-button>
              </div>
            </template>
          </RecentList>
        </el-col>

        <el-col :xs="24" :xl="12">
          <RecentList
            title="风险提醒 / 最近动态"
            description="失败执行、异常和平台动态当前以轻量占位结构展示，不提前做平台级聚合中心。"
            :items="riskFeedItems"
            empty-title="暂无风险提醒"
            empty-description="当前没有可展示的轻量提醒。"
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
                <el-button text type="primary" @click="navigateTo(item.route)">查看</el-button>
              </div>
            </template>
          </RecentList>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useProductivityStore } from '@/stores/productivity'
import {
  Bell,
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
  Warning,
  Tools,
  User
} from '@element-plus/icons-vue'
import { TOP_LEVEL_NAVIGATION } from '@/config/navigation'
import { getModuleEntry, getModuleLabel } from '@/router/route-meta'
import { QuickActionCard, RecentList, StatCard } from '@/components/platform-shared'
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

const userLabel = computed(() => userStore.user?.username || '平台成员')

const greetingText = computed(() => {
  const hour = new Date().getHours()

  if (hour < 11) {
    return '早上好'
  }

  if (hour < 14) {
    return '中午好'
  }

  if (hour < 18) {
    return '下午好'
  }

  return '晚上好'
})

const welcomeHeadline = computed(() => `${greetingText.value}，${userLabel.value}`)

const workModeText = computed(() => {
  return userStore.user ? '继续当前测试平台工作' : '等待用户信息加载'
})

const currentWorkNote = computed(() => {
  return `${userLabel.value}，建议优先从待处理事项或最近继续入口开始，再进入具体模块。`
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

const iconAccentMap = {
  house: { icon: FolderOpened, accent: 'cyan' },
  folder: { icon: FolderOpened, accent: 'cyan' },
  'folder-opened': { icon: FolderOpened, accent: 'cyan' },
  link: { icon: Link, accent: 'blue' },
  monitor: { icon: Monitor, accent: 'green' },
  setting: { icon: Setting, accent: 'slate' },
  chat: { icon: ChatDotRound, accent: 'purple' },
  bell: { icon: Bell, accent: 'blue' },
  warning: { icon: Warning, accent: 'orange' },
  'magic-stick': { icon: MagicStick, accent: 'cyan' },
  'data-analysis': { icon: DataLine, accent: 'orange' },
  user: { icon: User, accent: 'purple' }
}

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
      icon: visual.icon,
      accent: visual.accent
    }
  })
})

const riskFeedItems = computed(() => ([
  {
    id: 'risk-failed-execution',
    type: '风险提醒',
    tag: '占位',
    title: '最近失败执行待回看',
    description: '后续可接执行中心或模块结果页真实失败记录，本轮仅提供稳定落位。',
    route: '/api-testing/history',
    icon: Warning,
    accent: 'orange'
  },
  {
    id: 'risk-follow-up',
    type: '待跟进',
    tag: '占位',
    title: '评审列表存在待处理项',
    description: '后续可自然接入测试设计域的待处理汇总，本轮先提供工作台提醒结构。',
    route: '/ai-generation/reviews',
    icon: Bell,
    accent: 'cyan'
  },
  {
    id: 'risk-platform-dynamic',
    type: '最近动态',
    tag: '说明',
    title: '工作台已接入统一共享组件',
    description: '首页继续复用 QuickActionCard、StatCard 和 RecentList，不再生长新的首页专用体系。',
    route: '/home',
    icon: Collection,
    accent: 'green'
  }
]))

const overviewCards = computed(() => ([
  {
    key: 'todo',
    title: '我的待处理',
    value: 3,
    description: '阶段 1 占位数据，后续对接真实待办与待处理流。',
    icon: Bell,
    accent: 'blue'
  },
  {
    key: 'risk',
    title: '最近失败 / 风险',
    value: 2,
    description: '当前按工作台占位结构展示，不提前建设平台级运营看板。',
    icon: Warning,
    accent: 'orange'
  },
  {
    key: 'activity',
    title: '最近活动量',
    value: riskFeedItems.value.length,
    description: '当前展示工作台轻量动态条目数。',
    icon: Clock,
    accent: 'purple'
  },
  {
    key: 'modules',
    title: '已接入工作域',
    value: coreModules.value.length,
    description: '该数据来自平台导航真源，属于当前真实接入数。',
    icon: DataLine,
    accent: 'green'
  }
]))

const myWorkCards = computed(() => ([
  {
    key: 'pending',
    title: '待处理事项',
    description: '优先回到项目、用例或评审继续推进当前工作。',
    badge: '3',
    icon: Bell,
    accent: 'blue',
    route: '',
    note: '阶段 1 占位待办'
  },
  {
    key: 'follow-up',
    title: '待跟进',
    description: '平台级工作台先提示需要继续确认和回看的事项。',
    badge: '2',
    icon: Warning,
    accent: 'orange',
    route: '',
    note: '阶段 1 占位跟进项'
  },
  {
    key: 'continue-design',
    title: '继续当前工作',
    description: '直接回到测试设计模块，继续项目、用例和评审处理。',
    badge: '入口',
    icon: Tools,
    accent: 'green',
    route: '/ai-generation/projects',
    note: '当前可直接继续的入口'
  }
]))

const homePageState = computed(() => {
  if (Boolean(userStore.accessToken) && !userStore.user) {
    return UI_PAGE_STATE.LOADING
  }

  return coreModules.value.length ? UI_PAGE_STATE.READY : UI_PAGE_STATE.EMPTY
})

usePlatformPageHeader(() => ({
  description: '平台工作台优先承接继续工作、模块入口和轻量提醒，不复制各模块 dashboard。',
  statusTags: [
    {
      label: '工作台首页',
      type: 'primary'
    }
  ],
  helperText: '首页主体只做平台级工作台；最近访问与收藏已接入第一版本地能力，全局搜索和项目上下文仍保留后续接入边界。',
  metaItems: [
    { label: '当前用户', value: userLabel.value },
    { label: '工作域', value: `${coreModules.value.length} 个` },
    { label: '快捷继续', value: `${productivityStore.quickContinueItems.length} 条最近访问` }
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
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: 100%;
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

.welcome-panel__aside {
  min-width: 0;
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

.workspace-streams {
  margin-bottom: 8px;
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
}

@media (max-width: 768px) {
  .home-workbench {
    gap: 20px;
  }

  .welcome-panel {
    padding: 18px;
  }

  .welcome-panel__headline {
    font-size: 24px;
  }

  .module-grid {
    grid-template-columns: 1fr;
  }
}
</style>
