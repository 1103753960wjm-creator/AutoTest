<template>
  <div class="module-dashboard">
    <StateLoading v-if="pageState === UI_PAGE_STATE.LOADING" :title="$t('common.uiState.loading.title')" />
    <StateForbidden
      v-else-if="pageState === UI_PAGE_STATE.FORBIDDEN"
      :primary-action-text="$t('common.uiState.actions.goHome')"
      @primary-action="router.push('/home')"
    />
    <StateError
      v-else-if="pageState === UI_PAGE_STATE.REQUEST_ERROR"
      :description="dashboardErrorMessage || $t('common.uiState.error.description')"
      @primary-action="loadDashboardData"
    />
    <template v-else>
      <section class="dashboard-section dashboard-section--stats">
        <el-row :gutter="20">
          <el-col v-for="card in statCards" :key="card.key" :xs="24" :sm="12" :xl="6">
            <StatCard
              :title="card.title"
              :value="card.value"
              :description="card.description"
              :icon="card.icon"
              :accent="card.accent"
              :loading="loading && !hasLoaded"
            />
          </el-col>
        </el-row>
      </section>

      <section class="dashboard-section">
        <div class="dashboard-section__header">
          <div>
            <h3 class="dashboard-section__title">常用入口 / 快捷动作</h3>
            <p class="dashboard-section__description">
              保留模块级高频入口，不把接口管理、请求历史和报告页重新拼成第二套模块导航。
            </p>
          </div>
        </div>
        <div class="dashboard-actions-grid">
          <QuickActionCard
            v-for="action in quickActions"
            :key="action.key"
            :title="action.title"
            :description="action.description"
            :badge="action.badge"
            :icon="action.icon"
            :accent="action.accent"
            variant="compact"
            @click="action.onClick"
          />
        </div>
      </section>

      <el-row :gutter="20" class="dashboard-streams">
        <el-col :xs="24" :xl="12">
          <RecentList
            :title="$t('apiTesting.dashboard.operationLogs')"
            description="真实承接当前模块操作日志，用于模块工作台的最近动态。"
            :items="operationLogs"
            :loading="loading && !hasLoaded"
            :error="false"
            :empty-title="$t('apiTesting.dashboard.noLogs')"
            :empty-description="$t('common.uiState.empty.description')"
            @retry="loadDashboardData"
          >
            <template #actions>
              <el-button text type="primary" @click="loadDashboardData">刷新</el-button>
            </template>
            <template #item="{ item: log }">
              <div class="stream-item">
                <div class="stream-item__icon" :class="getOperationAccent(log.operation_type)">
                  <el-icon><component :is="getOperationIcon(log.operation_type)" /></el-icon>
                </div>
                <div class="stream-item__body">
                  <div class="stream-item__top">
                    <span class="stream-item__type">最近动态</span>
                    <span class="stream-item__tag">{{ log.operation_type || '记录' }}</span>
                  </div>
                  <div class="stream-item__title">{{ log.description }}</div>
                  <p class="stream-item__description">
                    {{ log.user_name || $t('apiTesting.dashboard.system') }} · {{ formatTime(log.created_at) }}
                  </p>
                </div>
              </div>
            </template>
          </RecentList>
        </el-col>

        <el-col :xs="24" :xl="12">
          <RecentList
            title="风险提醒 / 最近失败"
            description="当前仅保留稳定落位；若没有统一失败流接口，不在首页硬拼假数据。"
            :items="riskReminders"
            empty-title="暂无风险提醒"
            empty-description="后续可接执行中心或统一报告源。"
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
                <el-button text type="primary" @click="item.onClick">{{ item.actionText }}</el-button>
              </div>
            </template>
          </RecentList>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Collection,
  Delete,
  Edit,
  Folder,
  Link,
  Operation,
  Plus,
  Setting,
  Timer,
  VideoPlay,
  Warning
} from '@element-plus/icons-vue'
import router from '@/router'
import { getDashboardStats, getOperationLogs } from '@/api/api-testing'
import { QuickActionCard, RecentList, StatCard } from '@/components/platform-shared'
import { StateError, StateForbidden, StateLoading, UI_PAGE_STATE } from '@/components/ui-states'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'

const { t } = useI18n()

const projectCount = ref(0)
const interfaceCount = ref(0)
const suiteCount = ref(0)
const historyCount = ref(0)
const operationLogs = ref([])

const loading = ref(false)
const hasLoaded = ref(false)
const requestState = ref(UI_PAGE_STATE.READY)
const dashboardErrorMessage = ref('')
const lastLoadedAt = ref('')

const hasOverviewData = computed(() => {
  return Boolean(
    projectCount.value ||
      interfaceCount.value ||
      suiteCount.value ||
      historyCount.value ||
      operationLogs.value.length
  )
})

const pageState = computed(() => {
  if (loading.value && !hasLoaded.value) {
    return UI_PAGE_STATE.LOADING
  }

  if (requestState.value === UI_PAGE_STATE.FORBIDDEN && !hasOverviewData.value) {
    return UI_PAGE_STATE.FORBIDDEN
  }

  if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR && !hasOverviewData.value) {
    return UI_PAGE_STATE.REQUEST_ERROR
  }

  return UI_PAGE_STATE.READY
})

const statCards = computed(() => ([
  {
    key: 'projects',
    title: t('apiTesting.dashboard.apiProjects'),
    value: projectCount.value,
    description: '接口测试项目范围',
    icon: Folder,
    accent: 'blue'
  },
  {
    key: 'interfaces',
    title: t('apiTesting.dashboard.interfaceCount'),
    value: interfaceCount.value,
    description: '接口资产规模',
    icon: Link,
    accent: 'green'
  },
  {
    key: 'suites',
    title: t('apiTesting.dashboard.testSuites'),
    value: suiteCount.value,
    description: '可执行套件数量',
    icon: Collection,
    accent: 'purple'
  },
  {
    key: 'history',
    title: t('apiTesting.dashboard.executionRecords'),
    value: historyCount.value,
    description: '历史执行记录累计',
    icon: Timer,
    accent: 'orange'
  }
]))

const quickActions = computed(() => ([
  {
    key: 'projects',
    title: '项目管理',
    description: '回到接口测试项目范围，继续组织用例和协作。',
    badge: '高频',
    icon: Folder,
    accent: 'blue',
    onClick: goToProjects
  },
  {
    key: 'interfaces',
    title: '接口管理',
    description: '维护接口清单和请求定义，继续日常资产维护。',
    badge: '资产',
    icon: Link,
    accent: 'green',
    onClick: goToInterfaces
  },
  {
    key: 'automation',
    title: '自动化测试',
    description: '进入自动化执行工作区，继续回归与调试。',
    badge: '执行',
    icon: VideoPlay,
    accent: 'cyan',
    onClick: goToAutomation
  },
  {
    key: 'history',
    title: '请求历史',
    description: '查看最近请求和调试结果，快速回看上下文。',
    badge: '继续',
    icon: Timer,
    accent: 'purple',
    onClick: goToHistory
  },
  {
    key: 'environments',
    title: '环境管理',
    description: '检查环境配置和变量，降低执行前切换成本。',
    badge: '配置',
    icon: Setting,
    accent: 'orange',
    onClick: goToEnvironments
  },
]))

const riskReminders = computed(() => {
  const items = []

  if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR && hasLoaded.value) {
    items.push({
      id: 'api-dashboard-partial-error',
      type: '真实提醒',
      tag: '刷新异常',
      title: '接口自动化概览存在部分数据刷新失败',
      description: dashboardErrorMessage.value || '当前模块首页存在未完成的请求，请先刷新或进入相关列表页核对。',
      icon: Warning,
      accent: 'orange',
      actionText: '重新加载',
      onClick: loadDashboardData
    })
  }

  items.push(
    {
      id: 'api-dashboard-risk-placeholder',
      type: '占位结构',
      tag: '后续接执行中心',
      title: '最近失败执行待接入统一报告源',
      description: '当前没有稳定失败流接口，本轮只保留风险提醒落位，不从请求历史中硬拼失败视图。',
      icon: Warning,
      accent: 'orange',
      actionText: '查看请求历史',
      onClick: goToHistory
    },
    {
      id: 'api-dashboard-env-placeholder',
      type: '占位结构',
      tag: '后续接环境检查',
      title: '环境变更提醒后续接统一配置核查',
      description: '当环境差异、失效配置有稳定来源后，再回填这里的真实风险提示。',
      icon: Setting,
      accent: 'slate',
      actionText: '进入环境管理',
      onClick: goToEnvironments
    }
  )

  return items
})

const formatHeaderTime = (timeStr) => {
  if (!timeStr) {
    return ''
  }

  const date = new Date(timeStr)

  if (isNaN(date.getTime())) {
    return ''
  }

  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

usePlatformPageHeader(() => ({
  description: '接口自动化工作台统一承接模块概览、快捷动作、最近动态和风险落位，不延伸到内部列表页。',
  statusTags: [
    {
      label: requestState.value === UI_PAGE_STATE.REQUEST_ERROR ? '部分数据异常' : '模块工作台',
      type: requestState.value === UI_PAGE_STATE.REQUEST_ERROR ? 'warning' : 'success'
    }
  ],
  updateText: lastLoadedAt.value ? `最近刷新 ${formatHeaderTime(lastLoadedAt.value)}` : '',
  helperText: '测试报告、定时任务和通知日志后续将向执行中心收口，本轮不再作为当前模块正式入口。',
  metaItems: [
    { label: '概览范围', value: '项目 / 接口 / 套件 / 请求历史' },
    { label: '最近动态', value: `${operationLogs.value.length} 条` }
  ],
  actions: [
    {
      key: 'projects',
      label: '项目管理',
      type: 'primary',
      icon: Folder,
      onClick: goToProjects
    },
    {
      key: 'history',
      label: '请求历史',
      plain: true,
      icon: Timer,
      onClick: goToHistory
    }
  ]
}))

const loadDashboardData = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  dashboardErrorMessage.value = ''

  try {
    const [statsRes, logsRes] = await Promise.all([
      getDashboardStats(),
      getOperationLogs({ page_size: 12, ordering: '-created_at' })
    ])

    const stats = statsRes.data
    projectCount.value = stats.project_count || 0
    interfaceCount.value = stats.interface_count || 0
    suiteCount.value = stats.suite_count || 0
    historyCount.value = stats.history_count || 0
    operationLogs.value = logsRes.data.results || []
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
  } catch (error) {
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    dashboardErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
    console.error('加载接口自动化 Dashboard 失败:', error)
  } finally {
    loading.value = false
  }
}

const goToProjects = () => {
  router.push('/api-testing/projects')
}

const goToInterfaces = () => {
  router.push('/api-testing/interfaces')
}

const goToAutomation = () => {
  router.push('/api-testing/automation')
}

const goToHistory = () => {
  router.push('/api-testing/history')
}

const goToEnvironments = () => {
  router.push('/api-testing/environments')
}

const getOperationIcon = (type) => {
  if (type === 'create') {
    return Plus
  }

  if (type === 'edit') {
    return Edit
  }

  if (type === 'delete') {
    return Delete
  }

  if (type === 'execute') {
    return VideoPlay
  }

  return Operation
}

const getOperationAccent = (type) => {
  if (type === 'create') {
    return 'accent-green'
  }

  if (type === 'edit') {
    return 'accent-blue'
  }

  if (type === 'delete') {
    return 'accent-red'
  }

  if (type === 'execute') {
    return 'accent-purple'
  }

  return 'accent-slate'
}

const formatTime = (timeStr) => {
  if (!timeStr) {
    return ''
  }

  const date = new Date(timeStr)

  if (isNaN(date.getTime())) {
    return ''
  }

  const diff = Date.now() - date.getTime()

  if (diff < 60000) {
    return t('apiTesting.dashboard.timeFormat.justNow')
  }

  if (diff < 3600000) {
    return t('apiTesting.dashboard.timeFormat.minutesAgo', { n: Math.floor(diff / 60000) })
  }

  if (diff < 86400000) {
    return t('apiTesting.dashboard.timeFormat.hoursAgo', { n: Math.floor(diff / 3600000) })
  }

  if (diff < 604800000) {
    return t('apiTesting.dashboard.timeFormat.daysAgo', { n: Math.floor(diff / 86400000) })
  }

  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped lang="scss">
.module-dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

.dashboard-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dashboard-section__header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.dashboard-section__title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
}

.dashboard-section__description {
  margin: 6px 0 0;
  color: #64748b;
  line-height: 1.7;
}

.dashboard-actions-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.dashboard-streams {
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

.stream-item__icon.accent-green {
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
}

.stream-item__icon.accent-purple {
  background: rgba(124, 58, 237, 0.16);
  color: #6d28d9;
}

.stream-item__icon.accent-red {
  background: rgba(239, 68, 68, 0.14);
  color: #b91c1c;
}

.stream-item__icon.accent-orange {
  background: rgba(249, 115, 22, 0.16);
  color: #c2410c;
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
  line-height: 1.6;
}

.stream-item__description {
  margin: 6px 0 0;
  color: #64748b;
  line-height: 1.7;
}

@media (max-width: 1200px) {
  .dashboard-actions-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .module-dashboard {
    gap: 20px;
  }

  .dashboard-actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
