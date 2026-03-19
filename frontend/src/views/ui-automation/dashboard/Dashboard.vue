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
              统一承接 Web 自动化的高频入口，强调继续工作，不顺手改内部脚本页或列表页。
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
            description="真实承接模块操作记录，保持和 Home 工作台同一类信息密度。"
            :items="operationRecords"
            :loading="loading && !hasLoaded"
            :error="false"
            empty-title="暂无最近动态"
            empty-description="当前模块还没有可展示的操作记录。"
            @retry="loadDashboardData"
          >
            <template #actions>
              <el-button text type="primary" @click="loadDashboardData">刷新</el-button>
            </template>
            <template #item="{ item: record }">
              <div class="stream-item">
                <div class="stream-item__icon" :class="getOperationAccent(record.operation_type)">
                  <el-icon><component :is="getOperationIcon(record.operation_type)" /></el-icon>
                </div>
                <div class="stream-item__body">
                  <div class="stream-item__top">
                    <span class="stream-item__type">最近动态</span>
                    <span class="stream-item__tag">{{ record.resource_type_display || '操作记录' }}</span>
                  </div>
                  <div class="stream-item__title">
                    {{ record.user_name || '系统用户' }} {{ record.operation_type_display || record.operation_type }}
                    {{ record.resource_name ? `「${record.resource_name}」` : '' }}
                  </div>
                  <p class="stream-item__description">{{ formatRelativeTime(record.created_at) }}</p>
                </div>
              </div>
            </template>
          </RecentList>
        </el-col>

        <el-col :xs="24" :xl="12">
          <RecentList
            title="风险提醒 / 最近失败"
            description="若没有稳定失败流接口，则明确保留占位结构，不从脚本页和执行页反向拼接假数据。"
            :items="riskReminders"
            empty-title="暂无风险提醒"
            empty-description="后续可接 Web 执行中心或统一报告源。"
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
  Bell,
  CaretRight,
  Collection,
  DataAnalysis,
  Delete,
  Document,
  Edit,
  Folder,
  Monitor,
  Plus,
  Refresh,
  RefreshRight,
  VideoPlay,
  Warning
} from '@element-plus/icons-vue'
import router from '@/router'
import { getDashboardStats, getOperationRecords } from '@/api/ui_automation'
import { QuickActionCard, RecentList, StatCard } from '@/components/platform-shared'
import { StateError, StateForbidden, StateLoading, UI_PAGE_STATE } from '@/components/ui-states'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'

const { t } = useI18n()

const projectCount = ref(0)
const testCaseCount = ref(0)
const suiteCount = ref(0)
const executionCount = ref(0)
const operationRecords = ref([])

const loading = ref(false)
const hasLoaded = ref(false)
const requestState = ref(UI_PAGE_STATE.READY)
const dashboardErrorMessage = ref('')
const lastLoadedAt = ref('')

const hasOverviewData = computed(() => {
  return Boolean(
    projectCount.value ||
      testCaseCount.value ||
      suiteCount.value ||
      executionCount.value ||
      operationRecords.value.length
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
    title: 'Web 项目',
    value: projectCount.value,
    description: '当前已接入的 Web 自动化项目数量',
    icon: Folder,
    accent: 'blue'
  },
  {
    key: 'testCases',
    title: '测试用例',
    value: testCaseCount.value,
    description: '可继续维护和执行的用例资产规模',
    icon: Document,
    accent: 'green'
  },
  {
    key: 'suites',
    title: '测试套件',
    value: suiteCount.value,
    description: '可复用的执行组合与回归入口',
    icon: Collection,
    accent: 'purple'
  },
  {
    key: 'executions',
    title: '执行记录',
    value: executionCount.value,
    description: '当前模块累计执行规模',
    icon: RefreshRight,
    accent: 'orange'
  }
]))

const quickActions = computed(() => ([
  {
    key: 'projects',
    title: '项目管理',
    description: '回到 Web 项目范围，继续组织自动化工作。',
    badge: '高频',
    icon: Folder,
    accent: 'blue',
    onClick: goToProjects
  },
  {
    key: 'elements',
    title: '元素管理',
    description: '进入增强版元素管理，继续维护定位资产。',
    badge: '资产',
    icon: Monitor,
    accent: 'green',
    onClick: goToElements
  },
  {
    key: 'cases',
    title: '测试用例',
    description: '继续编辑和运行 Web 测试用例。',
    badge: '用例',
    icon: Document,
    accent: 'cyan',
    onClick: goToTestCases
  },
  {
    key: 'scripts',
    title: '脚本生成 / 编辑',
    description: '继续脚本编排，不在 Dashboard 内部承接脚本工作区。',
    badge: '脚本',
    icon: Edit,
    accent: 'purple',
    onClick: goToScripts
  },
  {
    key: 'suites',
    title: '测试套件',
    description: '快速回到套件列表，继续批量执行与回归。',
    badge: '执行',
    icon: Collection,
    accent: 'orange',
    onClick: goToSuites
  },
  {
    key: 'reports',
    title: '测试报告',
    description: '回看执行结果，为后续风险真实来源预留位置。',
    badge: '报告',
    icon: DataAnalysis,
    accent: 'blue',
    onClick: goToReports
  }
]))

const riskReminders = computed(() => {
  const items = []

  if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR && hasLoaded.value) {
    items.push({
      id: 'web-dashboard-partial-error',
      type: '真实提醒',
      tag: '刷新异常',
      title: 'Web 自动化概览存在部分数据加载失败',
      description: dashboardErrorMessage.value || '请先刷新当前模块首页，或进入相关列表页核对数据。',
      icon: Warning,
      accent: 'orange',
      actionText: '重新加载',
      onClick: loadDashboardData
    })
  }

  items.push(
    {
      id: 'web-dashboard-risk-placeholder',
      type: '占位结构',
      tag: '后续接执行中心',
      title: '最近失败执行待接入统一执行中心',
      description: '当前没有稳定失败流接口，本轮不从脚本页、执行页或报告页回拼不稳定数据。',
      icon: Warning,
      accent: 'orange',
      actionText: '查看执行记录',
      onClick: goToExecutions
    },
    {
      id: 'web-dashboard-report-placeholder',
      type: '占位结构',
      tag: '后续接统一报告源',
      title: '风险摘要后续接测试报告聚合源',
      description: '当前模块首页先保留风险落位，后续等统一报告源稳定后再接入真实失败提醒。',
      icon: DataAnalysis,
      accent: 'slate',
      actionText: '进入测试报告',
      onClick: goToReports
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
  description: 'Web 自动化工作台统一承接模块概览、快捷动作、最近动态和风险落位，不把脚本页和执行页混进首页。',
  statusTags: [
    {
      label: requestState.value === UI_PAGE_STATE.REQUEST_ERROR ? '部分数据异常' : '模块工作台',
      type: requestState.value === UI_PAGE_STATE.REQUEST_ERROR ? 'warning' : 'success'
    }
  ],
  updateText: lastLoadedAt.value ? `最近刷新 ${formatHeaderTime(lastLoadedAt.value)}` : '',
  helperText: '风险提醒区当前仅保留稳定结构，后续再接执行中心和统一报告源。',
  metaItems: [
    { label: '概览范围', value: '项目 / 用例 / 套件 / 执行记录' },
    { label: '最近动态', value: `${operationRecords.value.length} 条` }
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
      key: 'scripts',
      label: '脚本编辑',
      plain: true,
      icon: Edit,
      onClick: goToScripts
    }
  ]
}))

const loadDashboardData = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  dashboardErrorMessage.value = ''

  try {
    const [statsRes, recordsRes] = await Promise.all([
      getDashboardStats(),
      getOperationRecords({ limit: 10 })
    ])

    const stats = statsRes.data
    projectCount.value = stats.project_count || 0
    testCaseCount.value = stats.test_case_count || 0
    suiteCount.value = stats.suite_count || 0
    executionCount.value = stats.execution_count || 0
    operationRecords.value = recordsRes.data.results || recordsRes.data || []
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
  } catch (error) {
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    dashboardErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
    console.error('加载 Web 自动化 Dashboard 失败:', error)
  } finally {
    loading.value = false
  }
}

const getOperationIcon = (operationType) => {
  const iconMap = {
    create: Plus,
    edit: Edit,
    delete: Delete,
    run: CaretRight,
    rerun: Refresh,
    save: Document,
    rename: Edit
  }

  return iconMap[operationType] || Bell
}

const getOperationAccent = (operationType) => {
  const classMap = {
    create: 'accent-green',
    edit: 'accent-blue',
    delete: 'accent-red',
    run: 'accent-purple',
    rerun: 'accent-orange',
    save: 'accent-cyan',
    rename: 'accent-blue'
  }

  return classMap[operationType] || 'accent-slate'
}

const formatRelativeTime = (dateString) => {
  if (!dateString) {
    return ''
  }

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMins < 1) {
    return t('uiAutomation.dashboard.justNow')
  }

  if (diffMins < 60) {
    return t('uiAutomation.dashboard.minutesAgo', { n: diffMins })
  }

  if (diffHours < 24) {
    return t('uiAutomation.dashboard.hoursAgo', { n: diffHours })
  }

  return t('uiAutomation.dashboard.daysAgo', { n: diffDays })
}

const goToProjects = () => {
  router.push('/ui-automation/projects')
}

const goToElements = () => {
  router.push('/ui-automation/elements-enhanced')
}

const goToTestCases = () => {
  router.push('/ui-automation/test-cases')
}

const goToScripts = () => {
  router.push('/ui-automation/scripts-enhanced')
}

const goToSuites = () => {
  router.push('/ui-automation/suites')
}

const goToExecutions = () => {
  router.push('/ui-automation/executions')
}

const goToReports = () => {
  router.push('/ui-automation/reports')
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
