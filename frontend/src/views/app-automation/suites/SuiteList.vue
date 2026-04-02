<template>
  <div class="suite-list">
    <div class="page-header">
      <h3>测试套件</h3>
      <div class="header-actions">
        <el-button type="primary" size="small" :icon="Plus" @click="showCreateDialog">
          新建套件
        </el-button>
        <el-button size="small" :icon="Refresh" :loading="loading" @click="loadSuites">
          刷新
        </el-button>
      </div>
    </div>

    <el-card class="config-card">
      <el-form :model="runConfig" label-width="100px" size="small">
        <el-row :gutter="16">
          <el-col :span="5">
            <el-form-item label="所属项目">
              <el-select
                v-model="projectFilter"
                placeholder="全部项目"
                clearable
                filterable
                style="width: 100%"
                @change="handleFilterChange"
              >
                <el-option v-for="project in projectList" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="7">
            <el-form-item label="选择设备" required>
              <el-select
                v-model="runConfig.deviceId"
                placeholder="请选择设备"
                filterable
                style="width: 100%"
                :loading="devicesLoading"
              >
                <el-option
                  v-for="device in availableDevices"
                  :key="device.id"
                  :label="`${device.name || device.device_id} (${device.device_id})`"
                  :value="device.device_id"
                  :disabled="device.status !== 'available' && device.status !== 'online'"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="选择应用">
              <el-select
                v-model="runConfig.packageName"
                placeholder="请选择应用（可选）"
                clearable
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="pkg in appPackages"
                  :key="pkg.id"
                  :label="`${pkg.name} (${pkg.package_name})`"
                  :value="pkg.package_name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="搜索套件">
              <el-input
                v-model="searchQuery"
                placeholder="搜索套件名称"
                clearable
                @clear="handleFilterChange"
                @keyup.enter="handleFilterChange"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <div class="table-section">
      <StateLoading v-if="pageState === UI_PAGE_STATE.LOADING" compact />
      <StateForbidden
        v-else-if="pageState === UI_PAGE_STATE.FORBIDDEN"
        compact
        primary-action-text="返回首页"
        @primary-action="router.push('/home')"
      />
      <StateError
        v-else-if="pageState === UI_PAGE_STATE.REQUEST_ERROR"
        compact
        :description="requestErrorMessage || '加载测试套件失败，请稍后重试。'"
        @primary-action="loadSuites"
      />
      <StateSearchEmpty
        v-else-if="pageState === UI_PAGE_STATE.SEARCH_EMPTY"
        compact
        primary-action-text="清空筛选"
        @primary-action="resetFilters"
      />
      <StateEmpty v-else-if="pageState === UI_PAGE_STATE.EMPTY" compact />
      <div v-else class="table-container">
        <UnifiedListTable
          v-model:currentPage="currentPage"
          v-model:pageSize="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          :data="suites"
          :loading="loading"
          row-key="id"
          selection-mode="none"
          :actions="{ view: false, edit: false, delete: false }"
          :action-column-width="260"
          @page-change="loadSuites"
        >
          <el-table-column prop="name" label="套件名称" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <el-link type="primary" @click="showEditDialog(row)">
                {{ row.name }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.description || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="用例数" width="90" align="center">
            <template #default="{ row }">
              <el-tag size="small">{{ row.test_case_count }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="执行状态" width="110" align="center">
            <template #default="{ row }">
              <el-tag :type="getSuiteDisplayStatus(row).type" size="small">
                {{ getSuiteDisplayStatus(row).text }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="通过/失败" width="110" align="center">
            <template #default="{ row }">
              <span v-if="row.execution_status !== 'not_run'" class="pass-fail">
                <span class="pass">{{ row.passed_count }}</span> /
                <span class="fail">{{ row.failed_count }}</span>
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="最后执行" width="170">
            <template #default="{ row }">
              {{ row.last_run_at ? formatDateTime(row.last_run_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="170">
            <template #default="{ row }">
              {{ formatDateTime(row.updated_at) }}
            </template>
          </el-table-column>
          <template #actions="{ row }">
            <el-button link type="success" size="small" @click="runSuite(row)">
              执行
            </el-button>
            <el-button link type="primary" size="small" @click="showEditDialog(row)">
              编辑
            </el-button>
            <el-button link type="warning" size="small" @click="showSuiteExecutions(row)">
              历史
            </el-button>
            <el-button link type="danger" size="small" @click="deleteSuite(row)">
              删除
            </el-button>
          </template>
        </UnifiedListTable>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑测试套件' : '新建测试套件'"
      width="900px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form :model="suiteForm" label-width="80px" size="default">
        <el-form-item label="套件名称" required>
          <el-input v-model="suiteForm.name" placeholder="请输入套件名称" />
        </el-form-item>
        <el-form-item label="所属项目">
          <el-select v-model="suiteForm.project" placeholder="请选择项目" clearable filterable style="width: 100%">
            <el-option v-for="project in projectList" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="suiteForm.description" type="textarea" :rows="2" placeholder="请输入套件描述" />
        </el-form-item>
      </el-form>

      <div class="case-selector">
        <div class="selector-panel available-panel">
          <div class="panel-header">
            <span>可选用例</span>
            <el-input
              v-model="caseSearchQuery"
              placeholder="搜索用例"
              size="small"
              clearable
              style="width: 200px"
              @input="filterAvailableCases"
            />
          </div>
          <div class="panel-body">
            <div
              v-for="testCase in filteredAvailableCases"
              :key="testCase.id"
              class="case-item"
              :class="{ disabled: selectedCaseIds.has(testCase.id) }"
              @click="addCase(testCase)"
            >
              <span class="case-name">{{ testCase.name }}</span>
              <span class="case-pkg">{{ testCase.app_package_name || '' }}</span>
              <el-icon v-if="!selectedCaseIds.has(testCase.id)" class="add-icon"><Plus /></el-icon>
              <el-icon v-else class="added-icon"><Check /></el-icon>
            </div>
            <el-empty v-if="filteredAvailableCases.length === 0" description="暂无可选用例" :image-size="60" />
          </div>
        </div>

        <div class="selector-panel selected-panel">
          <div class="panel-header">
            <span>已选用例 ({{ selectedCases.length }})</span>
            <el-button v-if="selectedCases.length" link type="danger" size="small" @click="clearAllCases">
              清空
            </el-button>
          </div>
          <div class="panel-body">
            <draggable
              v-model="selectedCases"
              item-key="id"
              handle=".drag-handle"
              animation="200"
            >
              <template #item="{ element, index }">
                <div class="case-item selected">
                  <el-icon class="drag-handle"><Rank /></el-icon>
                  <span class="case-order">{{ index + 1 }}</span>
                  <span class="case-name">{{ element.name }}</span>
                  <el-icon class="remove-icon" @click="removeCase(index)"><Close /></el-icon>
                </div>
              </template>
            </draggable>
            <el-empty v-if="selectedCases.length === 0" description="请从左侧添加用例" :image-size="60" />
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveSuite">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="historyVisible"
      :title="`执行历史 - ${currentSuiteName}`"
      width="900px"
      destroy-on-close
    >
      <el-table :data="suiteExecutions" v-loading="historyLoading" empty-text="暂无执行记录">
        <el-table-column prop="case_name" label="测试用例" min-width="180" />
        <el-table-column prop="device_name" label="设备" width="150" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getDisplayStatus(row.status, row.result).type" size="small">
              {{ getDisplayStatus(row.status, row.result).text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress || 0"
              :status="getProgressStatus(row)"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="170">
          <template #default="{ row }">
            {{ row.started_at ? formatDateTime(row.started_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed' || row.status === 'error'"
              link
              type="primary"
              size="small"
              @click="viewReport(row)"
            >
              查看报告
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, Check, Close, Rank } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import { UnifiedListTable } from '@/components/platform-shared'
import {
  StateEmpty,
  StateError,
  StateForbidden,
  StateLoading,
  StateSearchEmpty,
  UI_PAGE_STATE
} from '@/components/ui-states'
import {
  getTestSuiteList,
  getTestSuiteDetail,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite as apiDeleteSuite,
  addTestCasesToSuite,
  removeTestCaseFromSuite,
  updateSuiteTestCaseOrder,
  runTestSuite,
  getTestSuiteExecutions,
  getTestCaseList,
  getDeviceList,
  getPackageList,
  getAppProjects
} from '@/api/app-automation'
import { getDisplayStatus, formatDateTime } from '@/utils/app-automation-helpers'

const router = useRouter()

const loading = ref(false)
const devicesLoading = ref(false)
const saving = ref(false)
const historyLoading = ref(false)
const searchQuery = ref('')
const projectFilter = ref(null)
const projectList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const hasLoaded = ref(false)
const requestState = ref(UI_PAGE_STATE.READY)
const requestErrorMessage = ref('')

const suites = ref([])
const availableDevices = ref([])
const appPackages = ref([])
const allTestCases = ref([])

const runConfig = ref({
  deviceId: null,
  packageName: null
})

const dialogVisible = ref(false)
const historyVisible = ref(false)
const isEdit = ref(false)
const editingSuiteId = ref(null)
const currentSuiteName = ref('')

const suiteForm = ref({
  name: '',
  description: '',
  project: null
})

const caseSearchQuery = ref('')
const selectedCases = ref([])
const suiteExecutions = ref([])

const hasActiveFilter = computed(() => Boolean(projectFilter.value || searchQuery.value.trim()))
const selectedCaseIds = computed(() => new Set(selectedCases.value.map((item) => item.id)))

const pageState = computed(() => {
  if (loading.value && !hasLoaded.value) {
    return UI_PAGE_STATE.LOADING
  }
  if (requestState.value === UI_PAGE_STATE.FORBIDDEN) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    return UI_PAGE_STATE.REQUEST_ERROR
  }
  if (suites.value.length === 0) {
    return hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return UI_PAGE_STATE.READY
})

const filteredAvailableCases = computed(() => {
  const keyword = caseSearchQuery.value.trim().toLowerCase()
  if (!keyword) {
    return allTestCases.value
  }
  return allTestCases.value.filter((testCase) => {
    return (
      testCase.name.toLowerCase().includes(keyword) ||
      (testCase.app_package_name && testCase.app_package_name.toLowerCase().includes(keyword))
    )
  })
})

const normalizeListPayload = (data) => {
  const payload = data?.success !== undefined ? data.data : data
  return {
    results: Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : [],
    count: Number(payload?.count || 0)
  }
}

const resolveRequestState = (error) => {
  if (error?.response?.status === 403) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  return UI_PAGE_STATE.REQUEST_ERROR
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadSuites()
}

const resetFilters = () => {
  searchQuery.value = ''
  projectFilter.value = null
  currentPage.value = 1
  loadSuites()
}

const loadSuites = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    if (projectFilter.value) {
      params.project = projectFilter.value
    }
    const res = await getTestSuiteList(params)
    const payload = normalizeListPayload(res.data)
    suites.value = payload.results
    total.value = payload.count || suites.value.length || 0
    requestState.value = UI_PAGE_STATE.READY
    requestErrorMessage.value = ''
    hasLoaded.value = true

    const maxPage = Math.max(1, Math.ceil((total.value || 0) / pageSize.value))
    if (total.value > 0 && currentPage.value > maxPage) {
      currentPage.value = maxPage
      await loadSuites()
    }
  } catch (error) {
    console.error('加载套件列表失败:', error)
    suites.value = []
    total.value = 0
    hasLoaded.value = true
    requestState.value = resolveRequestState(error)
    requestErrorMessage.value = error?.response?.data?.detail || error?.message || '加载套件列表失败'
  } finally {
    loading.value = false
  }
}

const loadDevices = async () => {
  devicesLoading.value = true
  try {
    const res = await getDeviceList({ page_size: 100 })
    const data = res.data
    if (data.success !== undefined) {
      availableDevices.value = data.data?.results || data.data || []
    } else {
      availableDevices.value = data.results || data || []
    }
  } catch (error) {
    console.error('加载设备失败:', error)
    availableDevices.value = []
  } finally {
    devicesLoading.value = false
  }
}

const loadPackages = async () => {
  try {
    const res = await getPackageList({ page_size: 200 })
    const data = res.data
    if (data.success !== undefined) {
      appPackages.value = data.data?.results || data.data || []
    } else {
      appPackages.value = data.results || data || []
    }
  } catch (error) {
    console.error('加载应用包名失败:', error)
    appPackages.value = []
  }
}

const loadAllTestCases = async () => {
  try {
    const res = await getTestCaseList({ page_size: 500 })
    const data = res.data
    const cases = data.success !== undefined ? (data.data?.results || data.data || []) : (data.results || data || [])
    allTestCases.value = cases.map((testCase) => ({
      id: testCase.id,
      name: testCase.name,
      description: testCase.description || '',
      app_package_name: testCase.app_package_name || ''
    }))
  } catch (error) {
    console.error('加载测试用例失败:', error)
    allTestCases.value = []
  }
}

const showCreateDialog = async () => {
  isEdit.value = false
  editingSuiteId.value = null
  suiteForm.value = { name: '', description: '', project: null }
  selectedCases.value = []
  caseSearchQuery.value = ''
  dialogVisible.value = true
  await loadAllTestCases()
}

const showEditDialog = async (suite) => {
  isEdit.value = true
  editingSuiteId.value = suite.id
  suiteForm.value = {
    name: suite.name,
    description: suite.description || '',
    project: suite.project || null
  }
  caseSearchQuery.value = ''
  dialogVisible.value = true

  await loadAllTestCases()

  try {
    const res = await getTestSuiteDetail(suite.id)
    const suiteCases = res.data?.suite_cases || []
    selectedCases.value = suiteCases
      .sort((a, b) => a.order - b.order)
      .map((item) => ({
        id: item.test_case.id,
        name: item.test_case.name,
        description: item.test_case.description || '',
        app_package_name: item.test_case.app_package_name || ''
      }))
  } catch (error) {
    console.error('加载套件用例失败:', error)
    selectedCases.value = []
  }
}

const saveSuite = async () => {
  if (!suiteForm.value.name.trim()) {
    ElMessage.warning('请输入套件名称')
    return
  }

  saving.value = true
  try {
    if (isEdit.value) {
      await updateTestSuite(editingSuiteId.value, {
        name: suiteForm.value.name,
        description: suiteForm.value.description,
        project: suiteForm.value.project || null
      })

      const detailRes = await getTestSuiteDetail(editingSuiteId.value)
      const currentCases = (detailRes.data?.suite_cases || []).map((item) => item.test_case.id)
      const newCaseIds = selectedCases.value.map((item) => item.id)

      for (const caseId of currentCases) {
        if (!newCaseIds.includes(caseId)) {
          await removeTestCaseFromSuite(editingSuiteId.value, { test_case_id: caseId })
        }
      }

      const toAdd = newCaseIds.filter((id) => !currentCases.includes(id))
      if (toAdd.length) {
        await addTestCasesToSuite(editingSuiteId.value, { test_case_ids: toAdd })
      }

      const orderData = selectedCases.value.map((item, index) => ({
        test_case_id: item.id,
        order: index
      }))
      await updateSuiteTestCaseOrder(editingSuiteId.value, { test_case_orders: orderData })
      ElMessage.success('套件更新成功')
    } else {
      await createTestSuite({
        name: suiteForm.value.name,
        description: suiteForm.value.description,
        project: suiteForm.value.project || null,
        test_case_ids: selectedCases.value.map((item) => item.id)
      })
      ElMessage.success('套件创建成功')
      currentPage.value = 1
    }

    dialogVisible.value = false
    await loadSuites()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.message || error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

const deleteSuite = async (suite) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试套件 "${suite.name}" 吗？`,
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await apiDeleteSuite(suite.id)
    ElMessage.success('删除成功')
    await loadSuites()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

const addCase = (testCase) => {
  if (selectedCaseIds.value.has(testCase.id)) {
    return
  }
  selectedCases.value.push({ ...testCase })
}

const removeCase = (index) => {
  selectedCases.value.splice(index, 1)
}

const clearAllCases = () => {
  selectedCases.value = []
}

const filterAvailableCases = () => {}

const runSuite = async (suite) => {
  if (!runConfig.value.deviceId) {
    ElMessage.warning('请先选择设备')
    return
  }
  if (suite.test_case_count === 0) {
    ElMessage.warning('该套件未包含任何测试用例')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要执行测试套件 "${suite.name}" 吗？\n共 ${suite.test_case_count} 个用例`,
      '确认执行',
      { confirmButtonText: '执行', cancelButtonText: '取消', type: 'info' }
    )

    const params = { device_id: runConfig.value.deviceId }
    if (runConfig.value.packageName) {
      params.package_name = runConfig.value.packageName
    }

    const res = await runTestSuite(suite.id, params)
    const data = res.data

    if (data.success) {
      ElMessage.success(data.message || '套件已提交执行')
      setTimeout(() => loadSuites(), 2000)
    } else {
      ElMessage.error(data.message || '执行失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败: ' + (error.response?.data?.message || error.message || '未知错误'))
    }
  }
}

const showSuiteExecutions = async (suite) => {
  currentSuiteName.value = suite.name
  historyVisible.value = true
  historyLoading.value = true

  try {
    const res = await getTestSuiteExecutions(suite.id)
    suiteExecutions.value = res.data.data || res.data || []
  } catch (error) {
    console.error('加载套件执行历史失败:', error)
    suiteExecutions.value = []
  } finally {
    historyLoading.value = false
  }
}

const viewReport = (execution) => {
  if (!execution.report_path) {
    ElMessage.info('报告路径不存在')
    return
  }
  window.open(`/api/app-automation/executions/${execution.id}/report/`, '_blank')
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
  return { type: 'info', text: status || '未知' }
}

const getProgressStatus = (row) => {
  if (row.status === 'completed') {
    return row.result === 'failed' ? 'exception' : 'success'
  }
  if (row.status === 'error') {
    return 'exception'
  }
  return undefined
}

onMounted(() => {
  getAppProjects({ page_size: 100 }).then((res) => {
    projectList.value = res.data.results || res.data || []
  }).catch(() => {})
  loadSuites()
  loadDevices()
  loadPackages()
})
</script>

<style scoped lang="scss">
.suite-list {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    margin: 0;
    font-size: 20px;
    color: #303133;
  }
}

.header-actions {
  display: flex;
  gap: 12px;
}

.config-card {
  margin-bottom: 16px;

  :deep(.el-card__body) {
    padding: 20px;
  }

  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

.table-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.table-container {
  min-height: 240px;
}

.pass-fail {
  .pass {
    color: #67c23a;
    font-weight: 600;
  }

  .fail {
    color: #f56c6c;
    font-weight: 600;
  }
}

.case-selector {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  height: 400px;
}

.selector-panel {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    background: #f5f7fa;
    border-bottom: 1px solid #e4e7ed;
    font-weight: 600;
    font-size: 14px;
    color: #303133;
  }

  .panel-body {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }
}

.case-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 13px;

  &:hover {
    background: #ecf5ff;
  }

  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: #f5f7fa;
  }

  &.selected {
    background: #f0f9eb;
    cursor: grab;

    &:hover {
      background: #e1f3d8;
    }
  }

  .case-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .case-pkg {
    color: #909399;
    font-size: 12px;
    margin-left: 8px;
    flex-shrink: 0;
  }

  .case-order {
    color: #909399;
    font-size: 12px;
    margin: 0 8px;
    min-width: 20px;
    text-align: center;
  }

  .add-icon {
    color: #409eff;
    flex-shrink: 0;
  }

  .added-icon {
    color: #67c23a;
    flex-shrink: 0;
  }
}

.drag-handle {
  cursor: grab;
  color: #909399;
}

.remove-icon {
  cursor: pointer;
  color: #f56c6c;
  flex-shrink: 0;
}
</style>
