<template>
  <div class="module-dashboard">
    <StateLoading v-if="pageState === UI_PAGE_STATE.LOADING" title="正在加载 App 自动化概览" />
    <StateForbidden
      v-else-if="pageState === UI_PAGE_STATE.FORBIDDEN"
      primary-action-text="返回首页"
      @primary-action="router.push('/home')"
    />
    <StateError
      v-else-if="pageState === UI_PAGE_STATE.REQUEST_ERROR"
      :description="dashboardErrorMessage || 'App 自动化首页加载失败，请稍后重试。'"
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
              保留 App 自动化的设备、元素、用例和执行入口，不把设备页或场景编辑页拉回首页。
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
            title="最近动态"
            description="真实承接最近执行记录，让模块首页更像子工作台而不是旧式统计看板。"
            :items="recentExecutions"
            :loading="loading && !hasLoaded"
            :error="false"
            empty-title="暂无最近执行"
            empty-description="执行任务后，这里会展示最新的执行动态。"
            @retry="loadDashboardData"
          >
            <template #actions>
              <el-button text type="primary" @click="loadDashboardData">刷新</el-button>
            </template>
            <template #item="{ item: execution }">
              <div class="stream-item">
                <div class="stream-item__icon" :class="`accent-${getExecutionAccent(execution)}`">
                  <el-icon><component :is="getExecutionIcon(execution)" /></el-icon>
                </div>
                <div class="stream-item__body">
                  <div class="stream-item__top">
                    <span class="stream-item__type">最近执行</span>
                    <span class="stream-item__tag">{{ getStatusText(execution.status) }}</span>
                  </div>
                  <div class="stream-item__title">{{ execution.case_name || '未命名用例' }}</div>
                  <p class="stream-item__description">
                    设备 {{ execution.device_name || '未绑定设备' }} · {{ formatTime(execution.created_at) }}
                  </p>
                </div>
                <el-button text type="primary" @click="goToExecutions">查看记录</el-button>
              </div>
            </template>
          </RecentList>
        </el-col>

        <el-col :xs="24" :xl="12">
          <RecentList
            title="风险提醒 / 最近失败"
            description="优先展示最近执行中的真实失败项；若当前没有稳定失败记录，则退回明确占位。"
            :items="riskReminders"
            empty-title="暂无风险提醒"
            empty-description="后续可继续接执行中心和统一报告源。"
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
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  Aim,
  Cellphone,
  CircleCheck,
  Collection,
  DataAnalysis,
  Document,
  Lock,
  Picture,
  VideoPlay,
  Warning
} from '@element-plus/icons-vue'
import router from '@/router'
import { getDashboardStatistics } from '@/api/app-automation'
import { QuickActionCard, RecentList, StatCard } from '@/components/platform-shared'
import { StateError, StateForbidden, StateLoading, UI_PAGE_STATE } from '@/components/ui-states'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'
import { formatRelativeTime, getExecutionStatusText } from '@/utils/app-automation-helpers'

const loading = ref(false)
const hasLoaded = ref(false)
const requestState = ref(UI_PAGE_STATE.READY)
const dashboardErrorMessage = ref('')
const lastLoadedAt = ref('')
const statistics = ref(createDefaultStatistics())

const recentExecutions = computed(() => statistics.value.recent_executions || [])

const hasOverviewData = computed(() => {
  return Boolean(
    statistics.value.devices.total ||
      statistics.value.test_cases.total ||
      statistics.value.executions.total ||
      recentExecutions.value.length
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
    key: 'devices',
    title: '设备总量',
    value: statistics.value.devices.total,
    description: '当前设备池规模',
    icon: Cellphone,
    accent: 'blue'
  },
  {
    key: 'onlineDevices',
    title: '在线设备',
    value: statistics.value.devices.online,
    description: '当前可连接的在线设备数',
    icon: CircleCheck,
    accent: 'green'
  },
  {
    key: 'testCases',
    title: '测试用例',
    value: statistics.value.test_cases.total,
    description: '可继续执行和维护的用例资产',
    icon: Document,
    accent: 'purple'
  },
  {
    key: 'passRate',
    title: '执行通过率',
    value: `${statistics.value.executions.pass_rate || 0}%`,
    description: '真实来源于 Dashboard 统计',
    icon: DataAnalysis,
    accent: 'orange'
  }
]))

const quickActions = computed(() => ([
  {
    key: 'devices',
    title: '设备管理',
    description: '回到设备列表，继续连机、锁定和池化管理。',
    badge: '高频',
    icon: Cellphone,
    accent: 'blue',
    onClick: goToDevices
  },
  {
    key: 'elements',
    title: '元素管理',
    description: '继续维护元素定位和图片资产。',
    badge: '资产',
    icon: Picture,
    accent: 'green',
    onClick: goToElements
  },
  {
    key: 'cases',
    title: '测试用例',
    description: '进入场景与用例列表，继续编辑和调试。',
    badge: '用例',
    icon: Document,
    accent: 'purple',
    onClick: goToTestCases
  },
  {
    key: 'suites',
    title: '测试套件',
    description: '回到套件列表，继续批量组织执行。',
    badge: '执行',
    icon: Collection,
    accent: 'cyan',
    onClick: goToSuites
  },
  {
    key: 'executions',
    title: '执行记录',
    description: '查看最近运行历史和执行结果。',
    badge: '记录',
    icon: Aim,
    accent: 'orange',
    onClick: goToExecutions
  },
  {
    key: 'reports',
    title: '测试报告',
    description: '查看报告列表，为后续风险源继续留口。',
    badge: '报告',
    icon: DataAnalysis,
    accent: 'blue',
    onClick: goToReports
  }
]))

const failedExecutionItems = computed(() => {
  return recentExecutions.value
    .filter((execution) => isFailedExecution(execution))
    .slice(0, 3)
    .map((execution) => ({
      id: `app-dashboard-failed-${execution.id}`,
      type: '真实提醒',
      tag: getStatusText(execution.status),
      title: execution.case_name || '未命名用例执行失败',
      description: `设备 ${execution.device_name || '未绑定设备'} · ${formatTime(execution.created_at)}`,
      icon: Warning,
      accent: 'orange',
      actionText: '查看执行',
      onClick: goToExecutions
    }))
})

const riskReminders = computed(() => {
  const items = []

  if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR && hasLoaded.value) {
    items.push({
      id: 'app-dashboard-partial-error',
      type: '真实提醒',
      tag: '刷新异常',
      title: 'App 自动化概览存在部分数据刷新失败',
      description: dashboardErrorMessage.value || '请先刷新当前模块首页，或进入执行记录与报告页核对数据。',
      icon: Warning,
      accent: 'orange',
      actionText: '重新加载',
      onClick: loadDashboardData
    })
  }

  items.push(...failedExecutionItems.value)

  if (!failedExecutionItems.value.length) {
    items.push({
      id: 'app-dashboard-risk-placeholder',
      type: '占位结构',
      tag: '后续接统一报告源',
      title: '最近失败摘要将在统一执行中心稳定后补齐',
      description: '当前优先展示真实最近执行；当失败流和报告聚合稳定后，再补充更完整的风险提示。',
      icon: Lock,
      accent: 'slate',
      actionText: '查看执行记录',
      onClick: goToExecutions
    })
  }

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
  description: 'App 自动化工作台统一承接模块概览、快捷动作、最近执行和风险提醒，不把设备池和场景编辑页塞回首页。',
  statusTags: [
    {
      label: requestState.value === UI_PAGE_STATE.REQUEST_ERROR ? '部分数据异常' : '模块工作台',
      type: requestState.value === UI_PAGE_STATE.REQUEST_ERROR ? 'warning' : 'success'
    }
  ],
  updateText: lastLoadedAt.value ? `最近刷新 ${formatHeaderTime(lastLoadedAt.value)}` : '',
  helperText: '风险提醒优先展示最近执行中的真实失败项，失败流为空时再退回明确占位。',
  metaItems: [
    { label: '设备池', value: `${statistics.value.devices.total} 台` },
    { label: '最近执行', value: `${recentExecutions.value.length} 条` }
  ],
  actions: [
    {
      key: 'devices',
      label: '设备管理',
      type: 'primary',
      icon: Cellphone,
      onClick: goToDevices
    },
    {
      key: 'executions',
      label: '执行记录',
      plain: true,
      icon: Aim,
      onClick: goToExecutions
    }
  ]
}))

function createDefaultStatistics() {
  return {
    devices: {
      total: 0,
      online: 0,
      locked: 0,
      available: 0
    },
    test_cases: {
      total: 0
    },
    executions: {
      total: 0,
      success: 0,
      failed: 0,
      pass_rate: 0
    },
    recent_executions: []
  }
}

const loadDashboardData = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  dashboardErrorMessage.value = ''

  try {
    const res = await getDashboardStatistics()
    const payload = res.data?.data || res.data

    if (res.data?.success === false || !payload) {
      throw new Error(res.data?.message || '未获取到有效的 Dashboard 数据')
    }

    statistics.value = {
      ...createDefaultStatistics(),
      ...payload,
      devices: {
        ...createDefaultStatistics().devices,
        ...(payload.devices || {})
      },
      test_cases: {
        ...createDefaultStatistics().test_cases,
        ...(payload.test_cases || {})
      },
      executions: {
        ...createDefaultStatistics().executions,
        ...(payload.executions || {})
      },
      recent_executions: payload.recent_executions || []
    }
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
  } catch (error) {
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    dashboardErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
    console.error('加载 App 自动化 Dashboard 失败:', error)
  } finally {
    loading.value = false
  }
}

const getStatusText = (status) => getExecutionStatusText(status)
const formatTime = (timeStr) => formatRelativeTime(timeStr)

const isFailedExecution = (execution) => {
  return ['failed', 'error'].includes(execution?.status) || execution?.result === 'failed'
}

const getExecutionAccent = (execution) => {
  if (isFailedExecution(execution)) {
    return 'orange'
  }

  if (execution?.status === 'completed' || execution?.status === 'success') {
    return 'green'
  }

  if (execution?.status === 'running') {
    return 'blue'
  }

  return 'slate'
}

const getExecutionIcon = (execution) => {
  if (isFailedExecution(execution)) {
    return Warning
  }

  if (execution?.status === 'completed' || execution?.status === 'success') {
    return CircleCheck
  }

  return VideoPlay
}

const goToDevices = () => {
  router.push('/app-automation/devices')
}

const goToElements = () => {
  router.push('/app-automation/elements')
}

const goToTestCases = () => {
  router.push('/app-automation/test-cases')
}

const goToSuites = () => {
  router.push('/app-automation/test-suites')
}

const goToExecutions = () => {
  router.push('/app-automation/executions')
}

const goToReports = () => {
  router.push('/app-automation/reports')
}

let refreshTimer = null

onMounted(() => {
  loadDashboardData()
  refreshTimer = setInterval(loadDashboardData, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
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

.stream-item__icon.accent-orange {
  background: rgba(249, 115, 22, 0.16);
  color: #c2410c;
}

.stream-item__icon.accent-cyan {
  background: rgba(6, 182, 212, 0.16);
  color: #0f766e;
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
