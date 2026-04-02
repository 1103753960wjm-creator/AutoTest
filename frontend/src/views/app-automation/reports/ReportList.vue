
<template>
  <div class="report-list">
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane label="套件报告" name="suite">
        <div class="stats-row">
          <el-card v-for="stat in suiteStatsCards" :key="stat.label" class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-number" :style="{ color: stat.color }">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </el-card>
        </div>

        <div class="filters">
          <el-row :gutter="20">
            <el-col :span="4">
              <el-select v-model="suiteProjectFilter" placeholder="全部项目" clearable filterable @change="handleSuiteFilterChange">
                <el-option v-for="project in projectList" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-input v-model="suiteSearch" placeholder="搜索套件名称" clearable @clear="handleSuiteFilterChange" @keyup.enter="handleSuiteFilterChange">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
            <el-col :span="5">
              <el-select v-model="suiteStatusFilter" placeholder="执行状态" clearable @change="handleSuiteFilterChange">
                <el-option label="已完成" value="completed" />
                <el-option label="执行异常" value="error" />
                <el-option label="执行中" value="running" />
                <el-option label="未执行" value="not_run" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-button type="primary" @click="handleSuiteFilterChange">
                <el-icon><Search /></el-icon>
                查询
              </el-button>
              <el-button @click="resetSuiteFilters">重置</el-button>
            </el-col>
          </el-row>
        </div>

        <div class="table-section">
          <StateLoading v-if="suitePageState === UI_PAGE_STATE.LOADING" compact />
          <StateForbidden
            v-else-if="suitePageState === UI_PAGE_STATE.FORBIDDEN"
            compact
            primary-action-text="返回首页"
            @primary-action="router.push('/home')"
          />
          <StateError
            v-else-if="suitePageState === UI_PAGE_STATE.REQUEST_ERROR"
            compact
            :description="suiteRequestErrorMessage || '加载套件报告失败，请稍后重试。'"
            @primary-action="loadSuiteReports"
          />
          <StateSearchEmpty
            v-else-if="suitePageState === UI_PAGE_STATE.SEARCH_EMPTY"
            compact
            primary-action-text="清空筛选"
            @primary-action="resetSuiteFilters"
          />
          <StateEmpty v-else-if="suitePageState === UI_PAGE_STATE.EMPTY" compact />
          <div v-else class="table-container">
            <UnifiedListTable
              v-model:currentPage="suitePagination.current"
              v-model:pageSize="suitePagination.size"
              :total="suitePagination.total"
              :page-sizes="[10, 20, 50, 100]"
              :data="suiteReports"
              :loading="suiteLoading"
              row-key="id"
              selection-mode="none"
              :actions="{ view: false, edit: false, delete: false }"
              :action-column-width="240"
              @page-change="loadSuiteReports"
            >
              <el-table-column prop="name" label="套件名称" min-width="160" show-overflow-tooltip />
              <el-table-column prop="description" label="描述" min-width="140" show-overflow-tooltip>
                <template #default="{ row }">{{ row.description || '-' }}</template>
              </el-table-column>
              <el-table-column label="执行状态" min-width="100">
                <template #default="{ row }">
                  <el-tag :type="getSuiteDisplayStatus(row).type" size="small">
                    {{ getSuiteDisplayStatus(row).text }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="用例通过率" min-width="150">
                <template #default="{ row }">
                  <el-progress
                    v-if="row.test_case_count > 0"
                    :percentage="getSuitePassRate(row)"
                    :color="getPassRateColor(getSuitePassRate(row))"
                    :stroke-width="16"
                    :text-inside="true"
                  />
                  <span v-else class="muted-text">暂无用例</span>
                </template>
              </el-table-column>
              <el-table-column label="用例统计" min-width="180">
                <template #default="{ row }">
                  <div class="step-stats">
                    <span class="success-text">通过 {{ row.passed_count || 0 }}</span>
                    <el-divider direction="vertical" />
                    <span class="danger-text">失败 {{ row.failed_count || 0 }}</span>
                    <el-divider direction="vertical" />
                    <span>总计 {{ row.test_case_count || 0 }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="创建人" min-width="100">
                <template #default="{ row }">{{ row.created_by_name || '-' }}</template>
              </el-table-column>
              <el-table-column label="最后执行" min-width="180">
                <template #default="{ row }">{{ formatDateTime(row.last_run_at) }}</template>
              </el-table-column>
              <template #actions="{ row }">
                <el-button type="primary" link size="small" @click="viewSuiteDetail(row)">详情</el-button>
                <el-button type="success" link size="small" @click="viewSuiteExecutions(row)">执行记录</el-button>
                <el-button type="success" link size="small" @click="viewSuiteAllureReport(row)">Allure报告</el-button>
                <el-button type="danger" link size="small" @click="deleteSuiteReport(row)">删除</el-button>
              </template>
            </UnifiedListTable>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="用例报告" name="case">
        <div class="stats-row">
          <el-card v-for="stat in caseStatsCards" :key="stat.label" class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-number" :style="{ color: stat.color }">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </el-card>
        </div>

        <div class="filters">
          <el-row :gutter="20">
            <el-col :span="4">
              <el-select v-model="caseProjectFilter" placeholder="全部项目" clearable filterable @change="handleCaseFilterChange">
                <el-option v-for="project in projectList" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-input v-model="caseSearch" placeholder="搜索用例名称或设备" clearable @clear="handleCaseFilterChange" @keyup.enter="handleCaseFilterChange">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
            <el-col :span="4">
              <el-select v-model="caseStatusFilter" placeholder="执行状态" clearable @change="handleCaseFilterChange">
                <el-option label="已完成" value="completed" />
                <el-option label="执行异常" value="error" />
                <el-option label="已停止" value="stopped" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-button type="primary" @click="handleCaseFilterChange">
                <el-icon><Search /></el-icon>
                查询
              </el-button>
              <el-button @click="resetCaseFilters">重置</el-button>
            </el-col>
          </el-row>
        </div>

        <div class="table-section">
          <StateLoading v-if="casePageState === UI_PAGE_STATE.LOADING" compact />
          <StateForbidden
            v-else-if="casePageState === UI_PAGE_STATE.FORBIDDEN"
            compact
            primary-action-text="返回首页"
            @primary-action="router.push('/home')"
          />
          <StateError
            v-else-if="casePageState === UI_PAGE_STATE.REQUEST_ERROR"
            compact
            :description="caseRequestErrorMessage || '加载用例报告失败，请稍后重试。'"
            @primary-action="loadCaseReports"
          />
          <StateSearchEmpty
            v-else-if="casePageState === UI_PAGE_STATE.SEARCH_EMPTY"
            compact
            primary-action-text="清空筛选"
            @primary-action="resetCaseFilters"
          />
          <StateEmpty v-else-if="casePageState === UI_PAGE_STATE.EMPTY" compact />
          <div v-else class="table-container">
            <UnifiedListTable
              v-model:currentPage="casePagination.current"
              v-model:pageSize="casePagination.size"
              :total="casePagination.total"
              :page-sizes="[10, 20, 50, 100]"
              :data="caseReports"
              :loading="caseLoading"
              row-key="id"
              selection-mode="none"
              :actions="{ view: false, edit: false, delete: false }"
              :action-column-width="180"
              @page-change="loadCaseReports"
            >
              <el-table-column label="测试用例" min-width="160" show-overflow-tooltip>
                <template #default="{ row }">{{ row.case_name || '-' }}</template>
              </el-table-column>
              <el-table-column label="设备" min-width="120">
                <template #default="{ row }">{{ row.device_name || '-' }}</template>
              </el-table-column>
              <el-table-column label="状态" min-width="100">
                <template #default="{ row }">
                  <el-tag :type="getDisplayStatus(row.status, row.result).type" size="small">
                    {{ getDisplayStatus(row.status, row.result).text }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="步骤通过率" min-width="150">
                <template #default="{ row }">
                  <el-progress
                    :percentage="row.pass_rate || 0"
                    :color="getPassRateColor(row.pass_rate || 0)"
                    :stroke-width="16"
                    :text-inside="true"
                  />
                </template>
              </el-table-column>
              <el-table-column label="步骤统计" min-width="180">
                <template #default="{ row }">
                  <div class="step-stats">
                    <span class="success-text">通过 {{ row.passed_steps || 0 }}</span>
                    <el-divider direction="vertical" />
                    <span class="danger-text">失败 {{ row.failed_steps || 0 }}</span>
                    <el-divider direction="vertical" />
                    <span>总计 {{ row.total_steps || 0 }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="耗时" min-width="100">
                <template #default="{ row }">{{ formatDuration(row.duration) }}</template>
              </el-table-column>
              <el-table-column label="执行人" min-width="100">
                <template #default="{ row }">{{ row.user_name || '-' }}</template>
              </el-table-column>
              <el-table-column label="执行时间" min-width="180">
                <template #default="{ row }">{{ formatDateTime(row.started_at) }}</template>
              </el-table-column>
              <template #actions="{ row }">
                <el-button type="primary" link size="small" @click="viewCaseDetail(row)">详情</el-button>
                <el-button v-if="row.report_path" type="success" link size="small" @click="viewAllureReport(row)">Allure报告</el-button>
                <el-button type="danger" link size="small" @click="deleteCaseReport(row)">删除</el-button>
              </template>
            </UnifiedListTable>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="suiteDetailVisible" title="套件报告详情" width="750px">
      <div v-if="selectedSuite">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="套件名称">{{ selectedSuite.name }}</el-descriptions-item>
          <el-descriptions-item label="执行状态">
            <el-tag :type="getSuiteDisplayStatus(selectedSuite).type">
              {{ getSuiteDisplayStatus(selectedSuite).text }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建人">{{ selectedSuite.created_by_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="最后执行">{{ formatDateTime(selectedSuite.last_run_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4>用例统计</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-stat success-bg">
                <div class="detail-stat-num">{{ selectedSuite.passed_count || 0 }}</div>
                <div class="detail-stat-label">通过用例</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-stat danger-bg">
                <div class="detail-stat-num">{{ selectedSuite.failed_count || 0 }}</div>
                <div class="detail-stat-label">失败用例</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-stat info-bg">
                <div class="detail-stat-num">{{ selectedSuite.test_case_count || 0 }}</div>
                <div class="detail-stat-label">总用例数</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div class="detail-section">
          <h4>用例通过率</h4>
          <el-progress
            :percentage="getSuitePassRate(selectedSuite)"
            :color="getPassRateColor(getSuitePassRate(selectedSuite))"
            :stroke-width="20"
            :text-inside="true"
            style="margin-top: 10px"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="suiteDetailVisible = false">关闭</el-button>
        <el-button type="primary" @click="suiteDetailVisible = false; viewSuiteExecutions(selectedSuite)">查看执行记录</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="suiteExecVisible" :title="`执行记录 - ${selectedSuite?.name || ''}`" width="900px">
      <el-table :data="suiteExecRecords" v-loading="suiteExecLoading" border stripe max-height="500">
        <el-table-column label="测试用例" min-width="180">
          <template #default="{ row }">{{ row.case_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getDisplayStatus(row.status, row.result).type" size="small">
              {{ getDisplayStatus(row.status, row.result).text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="步骤统计" width="200">
          <template #default="{ row }">
            <div class="step-stats">
              <span class="success-text">通过 {{ row.passed_steps || 0 }}</span>
              <el-divider direction="vertical" />
              <span class="danger-text">失败 {{ row.failed_steps || 0 }}</span>
              <el-divider direction="vertical" />
              <span>总计 {{ row.total_steps || 0 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">{{ formatDuration(row.duration) }}</template>
        </el-table-column>
        <el-table-column label="执行时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.started_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.report_path" type="success" link size="small" @click="viewAllureReport(row)">Allure报告</el-button>
            <el-button v-if="row.error_message" type="danger" link size="small" @click="viewCaseDetail(row)">错误</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="suiteExecVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="caseDetailVisible" title="用例执行报告详情" width="700px">
      <div v-if="selectedCase">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="测试用例">{{ selectedCase.case_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="执行设备">{{ selectedCase.device_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="执行状态">
            <el-tag :type="getDisplayStatus(selectedCase.status, selectedCase.result).type">
              {{ getDisplayStatus(selectedCase.status, selectedCase.result).text }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行人">{{ selectedCase.user_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDateTime(selectedCase.started_at) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDateTime(selectedCase.finished_at) }}</el-descriptions-item>
          <el-descriptions-item label="执行耗时">{{ formatDuration(selectedCase.duration) }}</el-descriptions-item>
          <el-descriptions-item label="步骤通过率">
            <span :style="{ color: getPassRateColor(selectedCase.pass_rate || 0), fontWeight: 'bold' }">
              {{ selectedCase.pass_rate || 0 }}%
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4>步骤统计</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-stat success-bg">
                <div class="detail-stat-num">{{ selectedCase.passed_steps || 0 }}</div>
                <div class="detail-stat-label">通过步骤</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-stat danger-bg">
                <div class="detail-stat-num">{{ selectedCase.failed_steps || 0 }}</div>
                <div class="detail-stat-label">失败步骤</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-stat info-bg">
                <div class="detail-stat-num">{{ selectedCase.total_steps || 0 }}</div>
                <div class="detail-stat-label">总步骤数</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div v-if="selectedCase.error_message" class="detail-section">
          <h4>错误信息</h4>
          <el-alert :title="selectedCase.error_message" type="error" show-icon :closable="false" />
        </div>

        <div v-if="selectedCase.report_path" class="detail-section detail-report-action">
          <el-button type="primary" @click="viewAllureReport(selectedCase)">
            <el-icon><DataAnalysis /></el-icon>
            查看完整 Allure 报告
          </el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="caseDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, DataAnalysis } from '@element-plus/icons-vue'
import {
  deleteExecution,
  deleteTestSuite,
  getAppProjects,
  getExecutionList,
  getTestSuiteExecutions,
  getTestSuiteList
} from '@/api/app-automation.js'
import { getDisplayStatus, formatDateTime } from '@/utils/app-automation-helpers.js'
import { UnifiedListTable } from '@/components/platform-shared'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

const router = useRouter()

const activeTab = ref('suite')
const projectList = ref([])

const suiteLoading = ref(false)
const suiteReports = ref([])
const suiteSearch = ref('')
const suiteStatusFilter = ref('')
const suiteProjectFilter = ref(null)
const suitePagination = reactive({ current: 1, size: 20, total: 0 })
const suiteHasLoaded = ref(false)
const suiteRequestState = ref(`${UI_PAGE_STATE.READY}`)
const suiteRequestErrorMessage = ref('')
const suiteDetailVisible = ref(false)
const suiteExecVisible = ref(false)
const suiteExecLoading = ref(false)
const suiteExecRecords = ref([])
const selectedSuite = ref(null)

const caseLoading = ref(false)
const caseReports = ref([])
const caseSearch = ref('')
const caseStatusFilter = ref('')
const caseProjectFilter = ref(null)
const casePagination = reactive({ current: 1, size: 20, total: 0 })
const caseHasLoaded = ref(false)
const caseRequestState = ref(`${UI_PAGE_STATE.READY}`)
const caseRequestErrorMessage = ref('')
const caseDetailVisible = ref(false)
const selectedCase = ref(null)

const suiteHasActiveFilter = computed(() => Boolean(
  suiteProjectFilter.value || suiteSearch.value || suiteStatusFilter.value
))

const caseHasActiveFilter = computed(() => Boolean(
  caseProjectFilter.value || caseSearch.value || caseStatusFilter.value
))

const suitePageState = computed(() => {
  if (suiteLoading.value && !suiteHasLoaded.value) return UI_PAGE_STATE.LOADING
  if (suiteRequestState.value === UI_PAGE_STATE.FORBIDDEN) return UI_PAGE_STATE.FORBIDDEN
  if (suiteRequestState.value === UI_PAGE_STATE.REQUEST_ERROR) return UI_PAGE_STATE.REQUEST_ERROR
  if (suiteReports.value.length === 0) {
    return suiteHasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return UI_PAGE_STATE.READY
})

const casePageState = computed(() => {
  if (caseLoading.value && !caseHasLoaded.value) return UI_PAGE_STATE.LOADING
  if (caseRequestState.value === UI_PAGE_STATE.FORBIDDEN) return UI_PAGE_STATE.FORBIDDEN
  if (caseRequestState.value === UI_PAGE_STATE.REQUEST_ERROR) return UI_PAGE_STATE.REQUEST_ERROR
  if (caseReports.value.length === 0) {
    return caseHasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return UI_PAGE_STATE.READY
})

const suiteStatsCards = computed(() => {
  const data = suiteReports.value
  const executed = data.filter(item => item.last_run_at)
  const failed = executed.filter(item => item.execution_result === 'failed')
  const avgRate = executed.length
    ? Math.round(executed.reduce((sum, item) => sum + getSuitePassRate(item), 0) / executed.length)
    : 0

  return [
    { label: '套件总数', value: suitePagination.total, color: '#409eff' },
    { label: '本页已执行', value: executed.length, color: '#67c23a' },
    { label: '本页失败', value: failed.length, color: '#f56c6c' },
    { label: '本页平均通过率', value: `${avgRate}%`, color: '#e6a23c' }
  ]
})

const caseStatsCards = computed(() => {
  const data = caseReports.value
  const success = data.filter(item => item.result === 'passed').length
  const failed = data.filter(item => item.result === 'failed').length
  const avgRate = data.length
    ? Math.round(data.reduce((sum, item) => sum + (item.pass_rate || 0), 0) / data.length)
    : 0

  return [
    { label: '报告总数', value: casePagination.total, color: '#409eff' },
    { label: '本页通过', value: success, color: '#67c23a' },
    { label: '本页失败', value: failed, color: '#f56c6c' },
    { label: '本页平均通过率', value: `${avgRate}%`, color: '#e6a23c' }
  ]
})

const loadProjects = async () => {
  try {
    const response = await getAppProjects({ page_size: 100 })
    projectList.value = response.data.results || response.data || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

const onTabChange = async (tabName) => {
  if (tabName === 'suite' && !suiteHasLoaded.value) {
    await loadSuiteReports()
  }
  if (tabName === 'case' && !caseHasLoaded.value) {
    await loadCaseReports()
  }
}

const handleSuiteFilterChange = async () => {
  suitePagination.current = 1
  await loadSuiteReports()
}

const handleCaseFilterChange = async () => {
  casePagination.current = 1
  await loadCaseReports()
}

const resetSuiteFilters = async () => {
  suiteSearch.value = ''
  suiteStatusFilter.value = ''
  suiteProjectFilter.value = null
  suitePagination.current = 1
  await loadSuiteReports()
}

const resetCaseFilters = async () => {
  caseSearch.value = ''
  caseStatusFilter.value = ''
  caseProjectFilter.value = null
  casePagination.current = 1
  await loadCaseReports()
}

const loadSuiteReports = async () => {
  suiteLoading.value = true
  suiteRequestState.value = UI_PAGE_STATE.READY
  suiteRequestErrorMessage.value = ''
  let shouldRefetch = false

  try {
    const params = {
      page: suitePagination.current,
      page_size: suitePagination.size
    }

    if (suiteProjectFilter.value) params.project = suiteProjectFilter.value
    if (suiteSearch.value) params.search = suiteSearch.value
    if (suiteStatusFilter.value) params.execution_status = suiteStatusFilter.value

    const response = await getTestSuiteList(params)
    const list = response.data.results || response.data || []
    suiteReports.value = list
    suitePagination.total = response.data.count || list.length || 0

    const maxPage = Math.max(1, Math.ceil((suitePagination.total || 0) / suitePagination.size || 1))
    if (suitePagination.current > maxPage) {
      suitePagination.current = maxPage
      shouldRefetch = true
      return
    }

    suiteHasLoaded.value = true
  } catch (error) {
    console.error('加载套件报告失败:', error)
    ElMessage.error('加载套件报告失败')
    suiteRequestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    suiteRequestErrorMessage.value = error.response?.data?.detail || error.message || ''
    suiteHasLoaded.value = true
  } finally {
    if (!shouldRefetch) {
      suiteLoading.value = false
    }
  }

  if (shouldRefetch) {
    await loadSuiteReports()
  }
}

const loadCaseReports = async () => {
  caseLoading.value = true
  caseRequestState.value = UI_PAGE_STATE.READY
  caseRequestErrorMessage.value = ''
  let shouldRefetch = false

  try {
    const params = {
      page: casePagination.current,
      page_size: casePagination.size,
      ordering: '-created_at',
      'test_suite__isnull': true
    }

    if (caseProjectFilter.value) params.project = caseProjectFilter.value
    if (caseSearch.value) params.search = caseSearch.value
    if (caseStatusFilter.value) params.status = caseStatusFilter.value

    const response = await getExecutionList(params)
    const list = response.data.results || response.data || []
    caseReports.value = list
    casePagination.total = response.data.count || list.length || 0

    const maxPage = Math.max(1, Math.ceil((casePagination.total || 0) / casePagination.size || 1))
    if (casePagination.current > maxPage) {
      casePagination.current = maxPage
      shouldRefetch = true
      return
    }

    caseHasLoaded.value = true
  } catch (error) {
    console.error('加载用例报告失败:', error)
    ElMessage.error('加载用例报告失败')
    caseRequestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    caseRequestErrorMessage.value = error.response?.data?.detail || error.message || ''
    caseHasLoaded.value = true
  } finally {
    if (!shouldRefetch) {
      caseLoading.value = false
    }
  }

  if (shouldRefetch) {
    await loadCaseReports()
  }
}

const viewSuiteDetail = (suite) => {
  selectedSuite.value = suite
  suiteDetailVisible.value = true
}

const viewSuiteExecutions = async (suite) => {
  selectedSuite.value = suite
  suiteExecVisible.value = true
  suiteExecLoading.value = true
  try {
    const response = await getTestSuiteExecutions(suite.id)
    suiteExecRecords.value = response.data.data || response.data.results || response.data || []
  } catch (error) {
    console.error('加载套件执行记录失败:', error)
    ElMessage.error('加载执行记录失败')
  } finally {
    suiteExecLoading.value = false
  }
}

const viewSuiteAllureReport = async (suite) => {
  try {
    const response = await getTestSuiteExecutions(suite.id)
    const records = response.data.data || response.data.results || response.data || []
    const recordWithReport = records.find(item => item.report_path)

    if (!recordWithReport) {
      ElMessage.warning('该套件暂时没有 Allure 报告')
      return
    }

    window.open(`/api/app-automation/executions/${recordWithReport.id}/report/`, '_blank')
  } catch (error) {
    console.error('获取套件报告失败:', error)
    ElMessage.error('获取报告失败')
  }
}

const deleteSuiteReport = async (suite) => {
  try {
    await ElMessageBox.confirm(`确认删除套件“${suite.name}”？此操作不可恢复。`, '删除确认', { type: 'warning' })
    await deleteTestSuite(suite.id)
    ElMessage.success('已删除')
    await loadSuiteReports()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除套件失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const viewCaseDetail = (row) => {
  selectedCase.value = row
  caseDetailVisible.value = true
}

const viewAllureReport = (row) => {
  if (!row.report_path) {
    ElMessage.warning('该记录没有 Allure 报告')
    return
  }
  window.open(`/api/app-automation/executions/${row.id}/report/`, '_blank')
}

const deleteCaseReport = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该执行报告？', '删除确认', { type: 'warning' })
    await deleteExecution(row.id)
    ElMessage.success('已删除')
    await loadCaseReports()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用例报告失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const getSuitePassRate = (suite) => {
  const total = suite.test_case_count || 0
  if (total === 0) return 0
  return Math.round(((suite.passed_count || 0) / total) * 100)
}

const getSuiteDisplayStatus = (row) => {
  const status = row.execution_status
  const result = row.execution_result

  if (status === 'not_run') return { type: 'info', text: '未执行' }
  if (status === 'running') return { type: 'warning', text: '执行中' }
  if (status === 'error') return { type: 'danger', text: '执行异常' }
  if (result === 'passed') return { type: 'success', text: '通过' }
  if (result === 'failed') return { type: 'danger', text: '失败' }
  if (result === 'skipped') return { type: 'warning', text: '跳过' }
  if (status === 'success') return { type: 'success', text: '通过' }
  if (status === 'failed') return { type: 'danger', text: '失败' }

  return { type: 'info', text: status || '-' }
}

const getPassRateColor = (rate) => {
  if (rate >= 80) return '#67c23a'
  if (rate >= 50) return '#e6a23c'
  return '#f56c6c'
}

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${Math.floor(seconds)}秒`
  const minutes = Math.floor(seconds / 60)
  const remainSeconds = Math.floor(seconds % 60)
  return `${minutes}分${remainSeconds}秒`
}

onMounted(async () => {
  await loadProjects()
  await loadSuiteReports()
})
</script>

<style scoped>
.report-list {
  padding: 20px;
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
}

.stat-content {
  text-align: center;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  line-height: 1.6;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.filters {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.table-section {
  min-height: 260px;
}

.table-container {
  overflow: hidden;
}

.table-container :deep(.unified-list-table) {
  display: flex;
  flex-direction: column;
}

.step-stats {
  display: flex;
  align-items: center;
  font-size: 13px;
}

.detail-section {
  margin-top: 24px;
}

.detail-section h4 {
  margin-bottom: 12px;
  color: #303133;
}

.detail-stat {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
}

.detail-stat-num {
  font-size: 24px;
  font-weight: bold;
}

.detail-stat-label {
  font-size: 13px;
  color: #606266;
  margin-top: 4px;
}

.detail-report-action {
  text-align: center;
}

.muted-text {
  color: #909399;
}

.success-text {
  color: #67c23a;
}

.danger-text {
  color: #f56c6c;
}

.success-bg {
  background: #f0f9eb;
  color: #67c23a;
}

.danger-bg {
  background: #fef0f0;
  color: #f56c6c;
}

.info-bg {
  background: #f4f4f5;
  color: #909399;
}
</style>
