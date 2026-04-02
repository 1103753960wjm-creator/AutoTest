<template>
  <div class="report-view">
    <div class="header">
      <h3>{{ $t('uiAutomation.report.title') }}</h3>
      <div class="actions">
        <el-select v-model="selectedProject" :placeholder="$t('uiAutomation.common.selectProject')" style="width: 200px; margin-right: 15px" @change="onProjectChange">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
        <el-button type="primary" @click="refreshReports">
          <el-icon><Refresh /></el-icon>
          {{ $t('uiAutomation.report.refreshReport') }}
        </el-button>
      </div>
    </div>

    <div class="content">
      <StateLoading v-if="pageState === UI_PAGE_STATE.LOADING" compact />
      <StateForbidden
        v-else-if="pageState === UI_PAGE_STATE.FORBIDDEN"
        compact
        :primary-action-text="$t('common.uiState.actions.goHome')"
        @primary-action="router.push('/home')"
      />
      <StateError
        v-else-if="pageState === UI_PAGE_STATE.REQUEST_ERROR"
        compact
        :description="requestErrorMessage || $t('common.uiState.error.description')"
        @primary-action="loadReports"
      />
      <StateSearchEmpty
        v-else-if="pageState === UI_PAGE_STATE.SEARCH_EMPTY"
        compact
        :primary-action-text="$t('common.uiState.actions.clearFilters')"
        @primary-action="clearProjectFilter"
      />
      <StateEmpty v-else-if="pageState === UI_PAGE_STATE.EMPTY" compact />

      <div v-else class="table-container">
      <UnifiedListTable
        v-model:currentPage="pagination.currentPage"
        v-model:pageSize="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        :data="reports"
        :loading="loading"
        row-key="id"
        selection-mode="none"
        :actions="{ view: false, edit: false, delete: false }"
        :action-column-width="200"
        @page-change="loadReports">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="test_suite_name" :label="$t('uiAutomation.report.testSuite')" min-width="200" />
        <el-table-column prop="status" :label="$t('uiAutomation.common.status')" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.report.testEngine')" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ getEngineText(row.engine) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.report.browser')" width="100">
          <template #default="{ row }">
            {{ getBrowserText(row.browser) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_cases" :label="$t('uiAutomation.report.totalCases')" width="100" />
        <el-table-column prop="passed_cases" :label="$t('uiAutomation.report.passedCases')" width="100">
          <template #default="{ row }">
            <span style="color: #67c23a; font-weight: bold;">{{ row.passed_cases }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="failed_cases" :label="$t('uiAutomation.report.failedCases')" width="100">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">{{ row.failed_cases }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.report.passRate')" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="row.pass_rate"
              :color="getProgressColor(row.pass_rate)"
              :stroke-width="16"
            />
          </template>
        </el-table-column>
        <el-table-column :label="$t('uiAutomation.report.duration')" width="120">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="executed_by_name" :label="$t('uiAutomation.report.executor')" width="120" />
        <el-table-column prop="created_at" :label="$t('uiAutomation.report.executionTime')" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <template #actions="{ row }">
            <el-button link type="primary" size="small" @click="viewReportDetail(row)">
              <el-icon><Document /></el-icon>
              {{ $t('uiAutomation.report.viewDetail') }}
            </el-button>
            <el-button link type="danger" size="small" @click="deleteReport(row)">
              <el-icon><Delete /></el-icon>
              {{ $t('uiAutomation.common.delete') }}
            </el-button>
        </template>
      </UnifiedListTable>
      </div>
    </div>

    <!-- 鎶ュ憡璇︽儏瀵硅瘽妗?-->
    <el-dialog
      v-model="showDetailDialog"
      :title="$t('uiAutomation.report.reportDetail')"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="currentReport" class="report-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('uiAutomation.report.reportId')">{{ currentReport.id }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.testSuite')">{{ currentReport.test_suite_name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.executionStatus')">
            <el-tag :type="getStatusType(currentReport.status)">
              {{ getStatusText(currentReport.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.executor')">{{ currentReport.executed_by_name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.testEngine')">{{ getEngineText(currentReport.engine) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.browser')">{{ getBrowserText(currentReport.browser) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.executionMode')">{{ currentReport.headless ? $t('uiAutomation.report.headlessMode') : $t('uiAutomation.report.headedMode') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.duration')">{{ formatDuration(currentReport.duration) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.startTime')">{{ formatDate(currentReport.started_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.report.endTime')">{{ formatDate(currentReport.finished_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="statistics-section">
          <h4>{{ $t('uiAutomation.report.testStatistics') }}</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-label">{{ $t('uiAutomation.report.totalCases') }}</div>
                <div class="stat-value">{{ currentReport.total_cases }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card success">
                <div class="stat-label">{{ $t('uiAutomation.report.passedCases') }}</div>
                <div class="stat-value">{{ currentReport.passed_cases }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card danger">
                <div class="stat-label">{{ $t('uiAutomation.report.failedCases') }}</div>
                <div class="stat-value">{{ currentReport.failed_cases }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card warning">
                <div class="stat-label">{{ $t('uiAutomation.report.skippedCases') }}</div>
                <div class="stat-value">{{ currentReport.skipped_cases }}</div>
              </div>
            </el-col>
          </el-row>

          <div class="pass-rate-chart">
            <h5>{{ $t('uiAutomation.report.passRate') }}: {{ currentReport.pass_rate }}%</h5>
            <el-progress
              :percentage="currentReport.pass_rate"
              :color="getProgressColor(currentReport.pass_rate)"
              :stroke-width="20"
            />
          </div>
        </div>

        <div class="result-section">
          <h4>{{ $t('uiAutomation.report.executionResultDetail') }}</h4>
          <el-table
            :data="getCaseExecutionList(currentReport)"
            border
            style="margin-top: 15px;"
          >
            <el-table-column type="index" :label="$t('uiAutomation.report.sequence')" width="60" />
            <el-table-column prop="test_case_name" :label="$t('uiAutomation.report.testCase')" min-width="200" />
            <el-table-column :label="$t('uiAutomation.report.executionStatus')" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'passed' ? 'success' : 'danger'">
                  {{ row.status === 'passed' ? $t('uiAutomation.report.casePassed') : $t('uiAutomation.report.caseFailed') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('uiAutomation.report.stepCount')" width="100" align="center">
              <template #default="{ row }">
                {{ row.steps ? row.steps.length : 0 }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('uiAutomation.common.operation')" width="120" align="center">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  link
                  @click="viewCaseDetail(row)"
                >
                  {{ $t('uiAutomation.report.viewDetail') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="error-section" v-if="currentReport.error_message">
          <h4>{{ $t('uiAutomation.report.errorInfo') }}</h4>
          <div class="errors-container">
            <div class="error-item">
              <div class="error-content">
                <pre class="error-text">{{ currentReport.error_message }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">{{ $t('uiAutomation.common.close') }}</el-button>
      </template>
    </el-dialog>

    <!-- 鐢ㄤ緥璇︽儏瀵硅瘽妗?-->
    <el-dialog
      v-model="showCaseDetailDialog"
      :title="`${$t('uiAutomation.report.caseDetail')} - ${currentCase?.test_case_name || ''}`"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="currentCase" class="case-detail">
        <!-- 鐢ㄤ緥鎵ц鎴愬姛 - 鍙樉绀烘墽琛屾棩蹇?-->
        <div v-if="currentCase.status === 'passed'">
          <h4>{{ $t('uiAutomation.report.executionLogs') }}</h4>
          <div class="log-container">
            <div v-for="(step, index) in currentCase.steps" :key="index" class="log-item">
              <div class="log-header">
                <el-tag :type="step.success ? 'success' : 'danger'" size="small">
                  {{ $t('uiAutomation.report.step') }} {{ step.step_number }}
                </el-tag>
                <span class="log-action">{{ getActionText(step.action_type) }}</span>
                <span class="log-desc">{{ step.description }}</span>
              </div>
              <div v-if="step.error" class="log-error">
                <el-icon><WarningFilled /></el-icon>
                {{ step.error }}
              </div>
            </div>
          </div>
        </div>

        <!-- 鐢ㄤ緥鎵ц澶辫触 - 鏄剧ず鎵ц鏃ュ織銆佸け璐ユ埅鍥俱€侀敊璇俊鎭笁涓猼ab -->
        <div v-else>
          <el-tabs v-model="activeTab" type="border-card">
            <!-- 鎵ц鏃ュ織 Tab -->
            <el-tab-pane :label="$t('uiAutomation.report.executionLogs')" name="logs">
              <div class="log-container">
                <div v-for="(step, index) in currentCase.steps" :key="index" class="log-item">
                  <div class="log-header">
                    <el-tag :type="step.success ? 'success' : 'danger'" size="small">
                      {{ $t('uiAutomation.report.step') }} {{ step.step_number }}
                    </el-tag>
                    <span class="log-action">{{ getActionText(step.action_type) }}</span>
                    <span class="log-desc">{{ step.description }}</span>
                  </div>
                  <div v-if="step.error" class="log-error">
                    <el-icon><WarningFilled /></el-icon>
                    {{ step.error }}
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- 澶辫触鎴浘 Tab -->
            <el-tab-pane :label="$t('uiAutomation.report.failedScreenshots')" name="screenshots">
              <div v-if="currentCase.screenshots && currentCase.screenshots.length > 0" class="screenshot-container">
                <div v-for="(screenshot, index) in currentCase.screenshots" :key="index" class="screenshot-item">
                  <h5>{{ screenshot.description || `${$t('uiAutomation.report.screenshot')} ${index + 1}` }}</h5>
                  <img :src="screenshot.url" :alt="screenshot.description" class="screenshot-img" />
                  <p class="screenshot-time">{{ screenshot.timestamp }}</p>
                </div>
              </div>
              <el-empty v-else :description="$t('uiAutomation.report.noScreenshots')" />
            </el-tab-pane>

            <!-- 閿欒淇℃伅 Tab -->
            <el-tab-pane :label="$t('uiAutomation.report.errorInfo')" name="error">
              <div class="errors-container">
                <div v-if="currentCase.error" class="error-item">
                  <div class="error-content">
                    <pre class="error-text">{{ currentCase.error }}</pre>
                  </div>
                </div>
                <el-empty v-else :description="$t('uiAutomation.report.noError')" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
      <template #footer>
        <el-button @click="showCaseDetailDialog = false">{{ $t('uiAutomation.common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Document, Delete, WarningFilled } from '@element-plus/icons-vue'
import {
  getUiProjects,
  getTestExecutions,
  deleteTestExecution
} from '@/api/ui_automation'
import { UnifiedListTable } from '@/components/platform-shared'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

const { t } = useI18n()
const router = useRouter()

const reports = ref([])
const projects = ref([])
const selectedProject = ref('')
const loading = ref(false)
const total = ref(0)
const hasLoaded = ref(false)
const requestState = ref(`${UI_PAGE_STATE.READY}`)
const requestErrorMessage = ref('')
const pagination = reactive({
  currentPage: 1,
  pageSize: 20
})

const hasActiveFilter = computed(() => Boolean(selectedProject.value))

const pageState = computed(() => {
  let state = String(UI_PAGE_STATE.READY)
  if (loading.value && !hasLoaded.value) {
    state = UI_PAGE_STATE.LOADING
  } else if (requestState.value === UI_PAGE_STATE.FORBIDDEN) {
    state = UI_PAGE_STATE.FORBIDDEN
  } else if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    state = UI_PAGE_STATE.REQUEST_ERROR
  } else if (reports.value.length === 0) {
    state = hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return state
})

// 璇︽儏瀵硅瘽妗?const showDetailDialog = ref(false)
const showDetailDialog = ref(false)
const currentReport = ref(null)

// 鐢ㄤ緥璇︽儏瀵硅瘽妗?const showCaseDetailDialog = ref(false)
const showCaseDetailDialog = ref(false)
const currentCase = ref(null)
const activeTab = ref('logs')

// 鍔犺浇椤圭洰鍒楄〃
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load projects:', error)
    ElMessage.error(t('uiAutomation.report.messages.loadProjectsFailed'))
  }
}

// 鍔犺浇鎶ュ憡鍒楄〃
const loadReports = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  requestErrorMessage.value = ''
  let shouldRefetch = false
  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }

    if (selectedProject.value) {
      params.project = selectedProject.value
    }

    const response = await getTestExecutions(params)

    if (response.data.results) {
      reports.value = response.data.results
      total.value = response.data.count || 0
    } else {
      reports.value = response.data
      total.value = response.data.length
    }
    const maxPage = Math.max(1, Math.ceil((total.value || 0) / pagination.pageSize || 1))
    if (pagination.currentPage > maxPage) {
      pagination.currentPage = maxPage
      shouldRefetch = true
      return
    }
    hasLoaded.value = true
  } catch (error) {
    console.error('Failed to load test reports:', error)
    ElMessage.error(t('uiAutomation.report.messages.loadFailed'))
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
  } finally {
    if (!shouldRefetch) {
      loading.value = false
    }
  }
  if (shouldRefetch) {
    await loadReports()
  }
}

// 椤圭洰鍒囨崲
const onProjectChange = async () => {
  pagination.currentPage = 1
  await loadReports()
}

// 鍒锋柊鎶ュ憡
const refreshReports = async () => {
  await loadReports()
  ElMessage.success(t('uiAutomation.report.messages.refreshed'))
}

const clearProjectFilter = async () => {
  selectedProject.value = ''
  pagination.currentPage = 1
  await loadReports()
}

// 鏌ョ湅鎶ュ憡璇︽儏
const viewReportDetail = (report) => {
  currentReport.value = report
  showDetailDialog.value = true
}

// 鑾峰彇鐢ㄤ緥鎵ц鍒楄〃
const getCaseExecutionList = (report) => {
  if (!report || !report.result_data || !report.result_data.test_cases) {
    return []
  }
  return report.result_data.test_cases
}

// 鏌ョ湅鐢ㄤ緥璇︽儏
const viewCaseDetail = (caseData) => {
  currentCase.value = caseData
  activeTab.value = 'logs'
  showCaseDetailDialog.value = true
}

// 鑾峰彇鎿嶄綔绫诲瀷鏂囨湰
const getActionText = (actionType) => {
  const actionMap = {
    'click': t('uiAutomation.actionTypes.click'),
    'fill': t('uiAutomation.actionTypes.fill'),
    'getText': t('uiAutomation.actionTypes.getText'),
    'waitFor': t('uiAutomation.actionTypes.waitFor'),
    'hover': t('uiAutomation.actionTypes.hover'),
    'scroll': t('uiAutomation.actionTypes.scroll'),
    'screenshot': t('uiAutomation.actionTypes.screenshot'),
    'assert': t('uiAutomation.actionTypes.assert'),
    'wait': t('uiAutomation.actionTypes.wait')
  }
  return actionMap[actionType] || actionType
}

// 鍒犻櫎鎶ュ憡
const deleteReport = async (report) => {
  try {
    await ElMessageBox.confirm(
      t('uiAutomation.report.messages.deleteConfirm', { name: report.test_suite_name }),
      t('uiAutomation.report.messages.confirmDelete'),
      {
        confirmButtonText: t('uiAutomation.common.confirm'),
        cancelButtonText: t('uiAutomation.common.cancel'),
        type: 'warning'
      }
    )

    await deleteTestExecution(report.id)
    ElMessage.success(t('uiAutomation.report.messages.deleteSuccess'))
    await loadReports()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete report:', error)
      ElMessage.error(t('uiAutomation.report.messages.deleteFailed'))
    }
  }
}

// 杈呭姪鏂规硶
const getStatusType = (status) => {
  const typeMap = {
    'PENDING': 'info',
    'RUNNING': 'warning',
    'SUCCESS': 'success',
    'FAILED': 'danger',
    'ABORTED': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'PENDING': t('uiAutomation.report.statusPending'),
    'RUNNING': t('uiAutomation.report.statusRunning'),
    'SUCCESS': t('uiAutomation.report.statusSuccess'),
    'FAILED': t('uiAutomation.report.statusFailed'),
    'ABORTED': t('uiAutomation.report.statusAborted')
  }
  return textMap[status] || status
}

const getEngineText = (engine) => {
  const engineMap = {
    'playwright': 'Playwright',
    'selenium': 'Selenium'
  }
  return engineMap[engine] || engine || 'Playwright'
}

const getBrowserText = (browser) => {
  const browserMap = {
    'chrome': 'Chrome',
    'firefox': 'Firefox',
    'safari': 'Safari',
    'edge': 'Edge'
  }
  return browserMap[browser] || browser || 'Chrome'
}

const getProgressColor = (percentage) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

const formatDuration = (seconds) => {
  if (!seconds) return `0${t('uiAutomation.report.seconds')}`
  if (seconds < 60) return `${seconds.toFixed(1)}${t('uiAutomation.report.seconds')}`
  const minutes = Math.floor(seconds / 60)
  const secs = (seconds % 60).toFixed(0)
  return `${minutes}${t('uiAutomation.report.minutes')}${secs}${t('uiAutomation.report.seconds')}`
}

onMounted(async () => {
  await loadProjects()
  if (projects.value.length > 0) {
    selectedProject.value = projects.value[0].id
  }
  await loadReports()
})
</script>

<style scoped lang="scss">
.report-view {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 4px;

  h3 {
    margin: 0;
    color: #303133;
    font-size: 24px;
  }

  .actions {
    display: flex;
    align-items: center;
  }
}

.content {
  flex: 1;
  overflow: auto;
  background: white;
  padding: 20px;
  border-radius: 4px;
}

.pagination-container {
  display: none;
}

.table-container {
  overflow: hidden;

  :deep(.unified-list-table) {
    display: flex;
    flex-direction: column;
  }
}

// 鎶ュ憡璇︽儏鏍峰紡
.report-detail {
  .statistics-section {
    margin-top: 30px;

    h4 {
      margin: 0 0 20px 0;
      color: #303133;
    }

    .stat-card {
      background: #f5f7fa;
      padding: 20px;
      border-radius: 4px;
      text-align: center;

      &.success {
        background: #f0f9ff;
        border: 1px solid #b3e5fc;
      }

      &.danger {
        background: #fef0f0;
        border: 1px solid #fde2e2;
      }

      &.warning {
        background: #fdf6ec;
        border: 1px solid #faecd8;
      }

      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 10px;
      }

      .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #303133;
      }
    }

    .pass-rate-chart {
      margin-top: 30px;

      h5 {
        margin: 0 0 15px 0;
        color: #303133;
        font-size: 16px;
      }
    }
  }

  .result-section {
    margin-top: 30px;

    h4 {
      margin: 0 0 15px 0;
      color: #303133;
    }

    .result-data {
      background: #f5f7fa;
      padding: 15px;
      border-radius: 4px;
      max-height: 400px;
      overflow: auto;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 12px;
      line-height: 1.5;
    }
  }

  .error-section {
    margin-top: 30px;

    h4 {
      margin: 0 0 15px 0;
      color: #303133;
    }
  }
}

.errors-container {
  padding: 10px;
  height: 100%;
  overflow-y: auto;
}

.error-item {
  background: #fff;
  border: 2px solid #f56c6c;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
}

.error-item:last-child {
  margin-bottom: 0;
}

.error-content {
  display: flex;
  flex-direction: column;
}

.error-text {
  margin: 0;
  padding: 15px;
  background: #2d2d2d;
  color: #ff6b6b;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-x: auto;
}

.error-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f5f5f5;
}

.error-header .el-tag {
  font-size: 16px;
  padding: 10px 15px;
  font-weight: 600;
}

// 鐢ㄤ緥璇︽儏鏍峰紡
.case-detail {
  h4 {
    margin: 0 0 20px 0;
    color: #303133;
    font-size: 16px;
  }

  .log-container {
    max-height: 500px;
    overflow-y: auto;
    background: #f5f7fa;
    padding: 15px;
    border-radius: 4px;

    .log-item {
      margin-bottom: 15px;
      padding: 12px;
      background: white;
      border-radius: 4px;
      border-left: 3px solid #409eff;

      &:last-child {
        margin-bottom: 0;
      }

      .log-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;

        .log-action {
          font-weight: 500;
          color: #606266;
        }

        .log-desc {
          color: #909399;
          font-size: 14px;
        }
      }

      .log-error {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #f56c6c;
        background: #fef0f0;
        padding: 8px 12px;
        border-radius: 4px;
        margin-top: 8px;
        font-size: 14px;
      }
    }
  }

  .screenshot-container {
    max-height: 600px;
    overflow-y: auto;
    padding: 10px;

    .screenshot-item {
      margin-bottom: 30px;
      text-align: center;

      h5 {
        margin: 0 0 15px 0;
        color: #303133;
        font-size: 14px;
      }

      .screenshot-img {
        max-width: 100%;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }

      .screenshot-time {
        margin: 10px 0 0 0;
        color: #909399;
        font-size: 12px;
      }
    }
  }
}
</style>
