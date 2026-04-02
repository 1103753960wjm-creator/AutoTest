<template>
  <div class="ui-flow-case-list">
    <div class="page-header">
      <h3>APP测试用例</h3>
      <div class="header-actions">
        <el-button
          type="primary"
          size="small"
          :icon="Refresh"
          :loading="loading"
          @click="loadTestCases"
        >
          刷新
        </el-button>
      </div>
    </div>

    <el-card class="device-card">
      <el-form :model="form" label-width="100px" size="small">
        <el-row :gutter="16">
          <el-col :span="5">
            <el-form-item label="所属项目">
              <el-select
                v-model="form.projectId"
                placeholder="全部项目"
                clearable
                filterable
                style="width: 100%"
                @change="handleListFilterChange"
              >
                <el-option
                  v-for="proj in projectList"
                  :key="proj.id"
                  :label="proj.name"
                  :value="proj.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="选择设备" required>
              <el-select
                v-model="form.deviceId"
                placeholder="请选择设备"
                filterable
                style="width: 100%"
                :loading="devicesLoading"
              >
                <el-option
                  v-for="device in availableDevices"
                  :key="device.id"
                  :label="`${device.name} (${device.device_id})`"
                  :value="device.id"
                  :disabled="device.status !== 'available' && device.status !== 'online'"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="选择应用">
              <el-select
                v-model="form.packageId"
                placeholder="请选择应用（可选）"
                clearable
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="pkg in appPackages"
                  :key="pkg.id"
                  :label="`${pkg.name} (${pkg.package_name})`"
                  :value="pkg.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="9">
            <el-form-item label="搜索用例">
              <el-input
                v-model="searchQuery"
                placeholder="搜索测试用例名称"
                clearable
                @clear="handleListFilterChange"
                @keyup.enter="handleListFilterChange"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
                <template #append>
                  <el-button :icon="Search" @click="handleListFilterChange">搜索</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <div v-if="selectedCases.length > 0 && pageState === UI_PAGE_STATE.READY" class="batch-bar">
      <span>已选择 <strong>{{ selectedCases.length }}</strong> 个用例</span>
      <el-button type="success" size="small" @click="batchRun">
        批量执行
      </el-button>
      <el-button size="small" @click="clearSelection">
        取消选择
      </el-button>
    </div>

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
        :description="requestErrorMessage || '加载测试用例失败，请稍后重试。'"
        @primary-action="loadTestCases"
      />
      <StateSearchEmpty
        v-else-if="pageState === UI_PAGE_STATE.SEARCH_EMPTY"
        compact
        primary-action-text="清空筛选"
        @primary-action="resetListFilters"
      />
      <StateEmpty v-else-if="pageState === UI_PAGE_STATE.EMPTY" compact />
      <div v-else class="table-container">
        <UnifiedListTable
          :key="tableRenderKey"
          v-model:currentPage="caseCurrentPage"
          v-model:pageSize="casePageSize"
          :total="caseTotal"
          :page-sizes="[10, 20, 50, 100]"
          :data="testCases"
          :loading="loading"
          row-key="id"
          selection-mode="multi"
          :toggle-on-row-click="false"
          :actions="{ view: false, edit: false, delete: false }"
          :action-column-width="220"
          @selection-change="handleSelectionChange"
          @page-change="loadTestCases"
        >
          <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
          <el-table-column label="场景描述" min-width="250" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.description || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.updated_at) }}
            </template>
          </el-table-column>
          <template #actions="{ row }">
            <el-button link type="success" size="small" @click="runCase(row)">
              运行
            </el-button>
            <el-button link type="primary" size="small" @click="editCase(row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="deleteCase(row)">
              删除
            </el-button>
          </template>
        </UnifiedListTable>
      </div>
    </div>

    <el-card class="execution-card">
      <template #header>
        <div class="card-header">
          <span>最近测试执行记录</span>
          <div class="card-actions">
            <el-button link type="primary" @click="refreshExecutions">
              刷新
            </el-button>
            <el-button link type="primary" @click="viewAllExecutions">
              查看全部
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="executionsLoading"
        :data="executionData.results"
        style="width: 100%"
      >
        <el-table-column prop="case_name" label="测试用例" width="200" />
        <el-table-column prop="device_name" label="设备" width="150" />
        <el-table-column prop="user_name" label="测试人员" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getDisplayStatus(row.status, row.result).type" size="small">
              {{ getDisplayStatus(row.status, row.result).text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="执行进度" width="280">
          <template #default="{ row }">
            <div class="progress-wrapper">
              <el-progress
                :percentage="calculateProgress(row)"
                :status="getProgressStatus(row)"
                :stroke-width="8"
                :show-text="false"
                style="flex: 1"
              />
              <span class="progress-text">{{ calculateProgress(row) }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="finished_at" label="结束时间" width="180">
          <template #default="{ row }">
            {{ row.finished_at ? formatDateTime(row.finished_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
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
            <el-button
              v-if="row.status === 'running'"
              link
              type="danger"
              size="small"
              @click="stopTest(row)"
            >
              停止
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
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
  getTestCaseList,
  deleteTestCase as apiDeleteTestCase,
  executeTestCase as apiExecuteTestCase,
  getExecutionList,
  getExecutionDetail,
  stopExecution as apiStopExecution,
  getPackageList,
  getAppProjects,
  getWsStatus,
  getDeviceList
} from '@/api/app-automation'
import { getDisplayStatus, formatDateTime } from '@/utils/app-automation-helpers'

const router = useRouter()

const loading = ref(false)
const devicesLoading = ref(false)
const executionsLoading = ref(false)
const availableDevices = ref([])
const appPackages = ref([])
const searchQuery = ref('')
const requestState = ref(UI_PAGE_STATE.READY)
const requestErrorMessage = ref('')
const hasLoaded = ref(false)

const projectList = ref([])
const form = ref({
  projectId: null,
  deviceId: null,
  packageId: null
})

const testCases = ref([])
const caseCurrentPage = ref(1)
const casePageSize = ref(20)
const caseTotal = ref(0)
const tableRenderKey = ref(0)

const selectedCases = ref([])

const executionData = ref({
  count: 0,
  results: []
})
const websockets = ref({})
const lastStatusMessages = ref({})

let refreshTimer = null

const hasActiveFilter = computed(() => Boolean(form.value.projectId || searchQuery.value.trim()))

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
  if (testCases.value.length === 0) {
    return hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return UI_PAGE_STATE.READY
})

const loadProjectList = async () => {
  try {
    const res = await getAppProjects({ page_size: 100 })
    projectList.value = res.data.results || res.data || []
  } catch {
    projectList.value = []
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

const resolveRequestState = (error) => {
  if (error?.response?.status === 403) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  return UI_PAGE_STATE.REQUEST_ERROR
}

const loadTestCases = async () => {
  loading.value = true
  try {
    const params = {
      page: caseCurrentPage.value,
      page_size: casePageSize.value
    }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    if (form.value.projectId) {
      params.project = form.value.projectId
    }

    const res = await getTestCaseList(params)
    const data = res.data

    if (data.success !== undefined) {
      testCases.value = data.data?.results || data.data || []
      caseTotal.value = data.data?.count || 0
    } else {
      testCases.value = data.results || data || []
      caseTotal.value = data.count || 0
    }

    requestState.value = UI_PAGE_STATE.READY
    requestErrorMessage.value = ''
    hasLoaded.value = true

    const maxPage = Math.max(1, Math.ceil((caseTotal.value || 0) / casePageSize.value))
    if (caseTotal.value > 0 && caseCurrentPage.value > maxPage) {
      caseCurrentPage.value = maxPage
      await loadTestCases()
    }
  } catch (error) {
    console.error('加载测试用例失败:', error)
    testCases.value = []
    caseTotal.value = 0
    hasLoaded.value = true
    requestState.value = resolveRequestState(error)
    requestErrorMessage.value = error?.response?.data?.detail || error?.message || '加载测试用例失败'
  } finally {
    loading.value = false
  }
}

const handleListFilterChange = () => {
  caseCurrentPage.value = 1
  loadTestCases()
}

const resetListFilters = () => {
  form.value.projectId = null
  searchQuery.value = ''
  caseCurrentPage.value = 1
  loadTestCases()
}

const loadExecutions = async () => {
  executionsLoading.value = true
  try {
    const params = {
      page: 1,
      page_size: 5,
      ordering: '-start_time'
    }
    const res = await getExecutionList(params)
    const data = res.data

    if (data.success !== undefined) {
      executionData.value = {
        count: data.data?.count || 0,
        results: data.data?.results || data.data || []
      }
    } else {
      executionData.value = {
        count: data.count || 0,
        results: data.results || data || []
      }
    }

    executionData.value.results.forEach((execution) => {
      if ((execution.status === 'pending' || execution.status === 'running') && execution.id) {
        trackExecution(execution.id)
      }
    })
  } catch (error) {
    console.error('加载执行记录失败:', error)
    executionData.value = { count: 0, results: [] }
  } finally {
    executionsLoading.value = false
  }
}

const refreshExecutions = () => {
  loadExecutions()
}

const viewAllExecutions = () => {
  router.push({ path: '/app-automation/executions' })
}

const viewReport = (execution) => {
  if (!execution.report_path) {
    ElMessage.info('报告路径不存在')
    return
  }
  const reportUrl = `/api/app-automation/executions/${execution.id}/report/`
  window.open(reportUrl, '_blank')
}

const stopTest = async (execution) => {
  try {
    await ElMessageBox.confirm(
      '确定要停止这个测试吗？',
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await apiStopExecution(execution.id)
    if (res.data.success) {
      ElMessage.success('已停止执行')
      loadExecutions()
    } else {
      ElMessage.error(res.data.message || '停止失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停止测试失败:', error)
    }
  }
}

const runCase = async (testCase) => {
  if (!form.value.deviceId) {
    ElMessage.warning('请先选择设备')
    return
  }

  try {
    const params = {
      device_id: availableDevices.value.find((device) => device.id === form.value.deviceId)?.device_id
    }

    if (form.value.packageId) {
      const selected = appPackages.value.find((pkg) => pkg.id === form.value.packageId)
      if (selected) {
        params.package_name = selected.package_name
      }
    }

    const res = await apiExecuteTestCase(testCase.id, params)
    const data = res.data

    if (data.success || data.execution_id) {
      ElMessage.success('测试已提交执行')
      const executionId = data.execution?.id || data.execution_id
      if (executionId) {
        trackExecution(executionId)
        checkExecutionStatus(executionId)
      }
      setTimeout(() => {
        loadExecutions()
      }, 1000)
    } else {
      ElMessage.error('执行失败: ' + (data.message || '未知错误'))
    }
  } catch (error) {
    ElMessage.error('执行失败: ' + (error.message || '未知错误'))
  }
}

const checkExecutionStatus = (executionId) => {
  setTimeout(async () => {
    try {
      const res = await getExecutionDetail(executionId)
      const data = res.data
      const status = data.status || data.data?.status
      if (status === 'pending') {
        ElMessage.warning('任务未开始，请确认 Celery worker/Redis 已启动')
      }
    } catch (error) {
      console.error('检查执行状态失败:', error)
    }
  }, 3000)
}

const editCase = (testCase) => {
  router.push({
    path: '/app-automation/scene-builder',
    query: { case_id: testCase.id }
  })
}

const deleteCase = async (testCase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例 "${testCase.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await apiDeleteTestCase(testCase.id)
    ElMessage.success('删除成功')
    await loadTestCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

const updateExecutionData = (updates) => {
  if (!updates || !updates.execution_id) {
    return
  }
  const target = executionData.value.results.find((item) => item.id === updates.execution_id)
  if (!target) {
    loadExecutions()
    return
  }
  if (updates.status) target.status = updates.status
  if (updates.result !== undefined) target.result = updates.result
  if (updates.progress !== null && updates.progress !== undefined) target.progress = updates.progress
  if (updates.report_path !== undefined) target.report_path = updates.report_path
  if (updates.finished_at) target.finished_at = updates.finished_at
}

const wsDisabled = ref(false)
const pollingTimers = ref({})
const wsRetryCount = ref({})
const WS_MAX_RETRY = 3

const startPolling = (executionId) => {
  if (pollingTimers.value[executionId]) return
  pollingTimers.value[executionId] = setInterval(async () => {
    try {
      const res = await getExecutionDetail(executionId)
      if (res.data) {
        updateExecutionData({
          execution_id: res.data.id,
          status: res.data.status,
          result: res.data.result,
          progress: res.data.progress,
          report_path: res.data.report_path,
          finished_at: res.data.finished_at
        })
        if (['completed', 'error', 'stopped'].includes(res.data.status)) {
          stopPolling(executionId)
          if (res.data.result === 'passed') ElMessage.success('测试执行通过')
          else if (res.data.result === 'failed') ElMessage.error('测试用例失败')
          else if (res.data.status === 'error') ElMessage.error('执行异常')
        }
      }
    } catch (error) {
      console.error('轮询执行状态失败:', error)
    }
  }, 3000)
}

const stopPolling = (executionId) => {
  if (pollingTimers.value[executionId]) {
    clearInterval(pollingTimers.value[executionId])
    delete pollingTimers.value[executionId]
  }
}

const stopAllPolling = () => {
  Object.keys(pollingTimers.value).forEach((id) => stopPolling(id))
}

const connectWebSocket = (executionId) => {
  if (websockets.value[executionId]) return

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const wsUrl = `${protocol}://${window.location.host}/ws/app-automation/executions/${executionId}/`

  const ws = new WebSocket(wsUrl)
  websockets.value[executionId] = ws

  ws.onopen = () => {
    wsRetryCount.value[executionId] = 0
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      updateExecutionData(data)
      if (data.status && lastStatusMessages.value[executionId] !== data.status) {
        lastStatusMessages.value[executionId] = data.status
        if (data.result === 'passed') ElMessage.success('测试执行通过')
        else if (data.result === 'failed') ElMessage.error('测试用例失败')
        else if (data.status === 'error') ElMessage.error('执行异常')
      }
      if (['completed', 'error', 'stopped'].includes(data.status)) {
        closeWebSocket(executionId)
      }
    } catch (error) {
      console.error('处理 WebSocket 消息失败:', error)
    }
  }

  ws.onclose = () => {
    delete websockets.value[executionId]
  }

  ws.onerror = () => {
    closeWebSocket(executionId)
    const retries = (wsRetryCount.value[executionId] || 0) + 1
    wsRetryCount.value[executionId] = retries
    if (retries <= WS_MAX_RETRY) {
      setTimeout(() => {
        const target = executionData.value.results.find((item) => item.id === executionId)
        if (target && ['pending', 'running'].includes(target.status)) {
          connectWebSocket(executionId)
        }
      }, retries * 1000)
    } else {
      delete wsRetryCount.value[executionId]
      startPolling(executionId)
    }
  }
}

const trackExecution = (executionId) => {
  if (wsDisabled.value) {
    startPolling(executionId)
  } else {
    connectWebSocket(executionId)
  }
}

const closeWebSocket = (executionId) => {
  const ws = websockets.value[executionId]
  if (ws) {
    ws.close()
    delete websockets.value[executionId]
  }
}

const closeAllWebSockets = () => {
  Object.keys(websockets.value).forEach((id) => closeWebSocket(id))
}

const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

const clearSelection = () => {
  selectedCases.value = []
  tableRenderKey.value += 1
}

const batchRun = async () => {
  if (!form.value.deviceId) {
    ElMessage.warning('请先选择设备')
    return
  }
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请至少选择一个用例')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要批量执行选中的 ${selectedCases.value.length} 个用例吗？`,
      '确认批量执行',
      { confirmButtonText: '执行', cancelButtonText: '取消', type: 'info' }
    )

    const deviceIdStr = availableDevices.value.find((device) => device.id === form.value.deviceId)?.device_id
    let packageName = null
    if (form.value.packageId) {
      const selected = appPackages.value.find((pkg) => pkg.id === form.value.packageId)
      if (selected) {
        packageName = selected.package_name
      }
    }

    let submitted = 0
    for (const testCase of selectedCases.value) {
      try {
        const params = { device_id: deviceIdStr }
        if (packageName) {
          params.package_name = packageName
        }
        await apiExecuteTestCase(testCase.id, params)
        submitted += 1
      } catch (error) {
        console.error(`执行用例 ${testCase.name} 失败:`, error)
      }
    }

    ElMessage.success(`已提交 ${submitted} 个用例执行`)
    clearSelection()
    setTimeout(() => loadExecutions(), 1500)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量执行失败:', error)
    }
  }
}

const calculateProgress = (execution) => {
  if (execution.status === 'completed') return 100
  if (execution.status === 'error' || execution.status === 'stopped') return execution.progress || 0
  if (execution.status === 'running') return execution.progress || 0
  return 0
}

const getProgressStatus = (row) => {
  if (row.status === 'completed') {
    return row.result === 'failed' ? 'exception' : 'success'
  }
  if (row.status === 'error') return 'exception'
  return undefined
}

onMounted(async () => {
  try {
    const res = await getWsStatus()
    wsDisabled.value = !(res.data?.websocket)
  } catch {
    wsDisabled.value = true
  }

  loadProjectList()
  loadDevices()
  loadPackages()
  loadTestCases()
  loadExecutions()

  if (!wsDisabled.value) {
    refreshTimer = setInterval(() => {
      const hasRunning = executionData.value.results.some((item) => item.status === 'running')
      if (hasRunning) {
        loadExecutions()
      }
    }, 10000)
  }
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  closeAllWebSockets()
  stopAllPolling()
})
</script>

<style scoped lang="scss">
.ui-flow-case-list {
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

.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin-top: 12px;
  background: #ecf5ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  font-size: 14px;

  strong {
    color: #409eff;
  }
}

.table-section {
  margin-top: 16px;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.table-container {
  min-height: 240px;
}

.execution-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  min-width: 40px;
  font-size: 12px;
  color: #606266;
}
</style>
