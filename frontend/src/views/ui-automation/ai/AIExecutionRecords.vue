<template>
  <ListShell
    :title="t('uiAutomation.ai.executionRecords.title')"
    class="execution-records-shell"
  >
    <template #actions>
      <el-button
        type="danger"
        :disabled="selectedRecords.length === 0"
        @click="batchDeleteRecords"
        :loading="isDeleting"
      >
        <el-icon><Delete /></el-icon>
        {{ t('uiAutomation.common.batchDelete') }}
      </el-button>
    </template>

    <div class="filters">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-input
            v-model="searchText"
            :placeholder="t('uiAutomation.ai.executionRecords.inputCaseName') || '请输入用例名称'"
            clearable
            @clear="handleFilterChange"
            @keyup.enter="handleFilterChange"
           style="width: 100%">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="8" class="filters__actions">
          <el-button type="primary" @click="handleFilterChange">
            {{ t('common.search') }}
          </el-button>
          <el-button @click="resetFilters">
            {{ t('common.reset') }}
          </el-button>
        </el-col>
      </el-row>
    </div>

    <div class="table-container">
      <StateLoading v-if="pageState === UI_PAGE_STATE.LOADING" compact />
      <StateForbidden
        v-else-if="pageState === UI_PAGE_STATE.FORBIDDEN"
        compact
        :primary-action-text="t('common.uiState.actions.goHome')"
        @primary-action="router.push('/home')"
      />
      <StateError
        v-else-if="pageState === UI_PAGE_STATE.REQUEST_ERROR"
        compact
        :description="requestErrorMessage || t('common.uiState.error.description')"
        @primary-action="loadRecords"
      />
      <StateSearchEmpty
        v-else-if="pageState === UI_PAGE_STATE.SEARCH_EMPTY"
        compact
        :primary-action-text="t('common.uiState.actions.clearFilters')"
        @primary-action="resetFilters"
      />
      <StateEmpty v-else-if="pageState === UI_PAGE_STATE.EMPTY" compact />

      <UnifiedListTable
        v-else
        ref="tableRef"
        v-model:currentPage="currentPage"
        v-model:pageSize="pageSize"
        :total="total"
        :data="records"
        :loading="loading"
        row-key="id"
        selection-mode="multi"
        :show-index="false"
        :actions="{ view: false, edit: false, delete: false }"
        @selection-change="handleSelectionChange"
        @page-change="handlePageChange"
      >
        <el-table-column :label="t('uiAutomation.ai.executionRecords.serialNumber')" width="80">
          <template #default="{ $index }">
            {{ getSerialNumber($index) }}
          </template>
        </el-table-column>
        <el-table-column prop="case_name" :label="t('uiAutomation.ai.executionRecords.caseName')" min-width="200" show-overflow-tooltip />

        <el-table-column prop="status" :label="t('uiAutomation.ai.executionRecords.status')" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" :label="t('uiAutomation.ai.executionRecords.durationSeconds')" width="120">
          <template #default="{ row }">
            {{ row.duration ? row.duration.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" :label="t('uiAutomation.ai.executionRecords.startTime')" width="180" :formatter="formatDate" />
        <el-table-column prop="executed_by.username" :label="t('uiAutomation.ai.executionRecords.executor')" width="120" />

        <template #actions="{ row }">
          <el-button 
            type="primary" 
            link 
            @click="viewDetail(row)"
          >
            {{ t('uiAutomation.ai.executionRecords.viewDetail') }}
          </el-button>
          <el-button 
            v-if="row.report_id"
            type="success" 
            link 
            @click="viewReport(row)"
          >
            {{ t('uiAutomation.ai.executionRecords.viewReport') }}
          </el-button>
        </template>
      </UnifiedListTable>
    </div>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" :title="t('uiAutomation.ai.executionRecords.executionDetail')" width="800px">
      <div v-if="currentRecord" class="record-detail">
        <div class="detail-item">
          <span class="label">{{ t('uiAutomation.ai.executionRecords.caseName') }}:</span>
          <span class="value">{{ currentRecord.case_name }}</span>
        </div>

        <div class="detail-item">
          <span class="label">{{ t('uiAutomation.ai.executionRecords.status') }}:</span>
          <el-tag :type="getStatusTag(currentRecord.status)">
            {{ getStatusText(currentRecord.status) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <span class="label">{{ t('uiAutomation.ai.executionRecords.startTime') }}:</span>
          <span>{{ formatDate(null, null, currentRecord.start_time) }}</span>
        </div>
        <div class="detail-item">
          <span class="label">{{ t('uiAutomation.ai.executionRecords.duration') }}:</span>
          <span>{{ currentRecord.duration ? currentRecord.duration.toFixed(2) + ' ' + t('uiAutomation.ai.executionRecords.seconds') : t('uiAutomation.ai.executionRecords.unknown') }}</span>
        </div>

        <!-- 任务描述 -->
        <div v-if="currentRecord.task_description" class="detail-item mt-15">
          <span class="label">{{ t('uiAutomation.ai.executionRecords.taskDescription') }}:</span>
        </div>
        <div v-if="currentRecord.task_description" class="task-description-container">
          <div class="task-description-content">{{ currentRecord.task_description }}</div>
        </div>

        <!-- 执行日志 -->
        <div class="detail-item mt-15">
          <span class="label">{{ t('uiAutomation.ai.executionRecords.executionLogs') }}:</span>
        </div>
        <div class="log-container">
          <pre>{{ currentRecord.logs }}</pre>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button type="success" @click="openReportFromDetail">{{ t('uiAutomation.ai.executionRecords.viewReport') }}</el-button>
          <el-button @click="showDetailDialog = false">{{ t('uiAutomation.common.close') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 报告对话框 -->
    <AIExecutionReport
      v-model="showReportDialog"
      :record-id="reportRecordId"
    />
  </ListShell>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Search } from '@element-plus/icons-vue'
import { getAIExecutionRecords, batchDeleteAIExecutionRecords } from '@/api/ui_automation'
import AIExecutionReport from './AIExecutionReport.vue'

// 统一公共组件与状态
import { UnifiedListTable } from '@/components/platform-shared'
import { ListShell } from '@/components/page-shells'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

const { t } = useI18n()
const router = useRouter()

const records = ref([])
const loading = ref(false)
const hasLoaded = ref(false)
const total = ref(0)

const requestState = ref(UI_PAGE_STATE.READY)
const requestErrorMessage = ref('')

const currentPage = ref(1)
const pageSize = ref(20)

const searchText = ref('')
const showDetailDialog = ref(false)
const currentRecord = ref(null)
let pollTimer = null

const selectedRecords = ref([])
const isDeleting = ref(false)
const tableRef = ref(null)

// 报告相关状态
const showReportDialog = ref(false)
const reportRecordId = ref(null)

// 计算页面状态
const pageState = computed(() => {
  let state = String(UI_PAGE_STATE.READY)
  if (loading.value && !hasLoaded.value) {
    state = UI_PAGE_STATE.LOADING
  } else if (requestState.value === UI_PAGE_STATE.FORBIDDEN) {
    state = UI_PAGE_STATE.FORBIDDEN
  } else if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    state = UI_PAGE_STATE.REQUEST_ERROR
  } else if (records.value.length === 0) {
    state = hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return state
})

// 是否激活筛选
const hasActiveFilter = computed(() => {
  return Boolean(searchText.value.trim())
})

// 解析请求错误状态
const resolveRequestState = (error) => {
  if (error?.response?.status === 403) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  return UI_PAGE_STATE.REQUEST_ERROR
}

// 加载记录列表
const loadRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchText.value.trim()) {
      params.search = searchText.value.trim()
    }
    const response = await getAIExecutionRecords(params)

    records.value = response.data.results || []
    total.value = response.data.count || 0
    requestState.value = UI_PAGE_STATE.READY
    requestErrorMessage.value = ''
    hasLoaded.value = true
    
    // 清空勾选
    if (tableRef.value && tableRef.value.clearSelection) {
      tableRef.value.clearSelection()
    }
  } catch (error) {
    console.error('获取执行记录失败:', error)
    ElMessage.error(t('uiAutomation.ai.executionRecords.messages.loadFailed'))
    records.value = []
    total.value = 0
    hasLoaded.value = true
    requestState.value = resolveRequestState(error)
    requestErrorMessage.value = error?.response?.data?.detail || t('uiAutomation.ai.executionRecords.messages.loadFailed')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadRecords()
}

const resetFilters = () => {
  searchText.value = ''
  currentPage.value = 1
  loadRecords()
}

const handlePageChange = ({ currentPage: newPage, pageSize: newSize }) => {
  currentPage.value = newPage
  pageSize.value = newSize
  loadRecords()
}

const viewDetail = (row) => {
  currentRecord.value = row
  showDetailDialog.value = true
}

// 查看报告
const viewReport = (row) => {
  reportRecordId.value = row.id
  showReportDialog.value = true
}

// 从详情页打开报告
const openReportFromDetail = () => {
  if (currentRecord.value) {
    reportRecordId.value = currentRecord.value.id
    showReportDialog.value = true
  }
}

const getStatusTag = (status) => {
  const map = {
    'pending': 'info',
    'running': 'warning',
    'passed': 'success',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'pending': t('uiAutomation.status.pending'),
    'running': t('uiAutomation.status.running'),
    'passed': t('uiAutomation.status.success'),
    'failed': t('uiAutomation.status.failed')
  }
  return map[status] || status
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  return new Date(cellValue).toLocaleString()
}

// 获取序号
const getSerialNumber = (index) => {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedRecords.value = selection
}

// 批量删除
const batchDeleteRecords = async () => {
  if (selectedRecords.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      t('uiAutomation.ai.executionRecords.messages.batchDeleteConfirm', { count: selectedRecords.value.length }),
      t('uiAutomation.ai.executionRecords.messages.batchDeleteTitle'),
      {
        confirmButtonText: t('uiAutomation.common.confirm'),
        cancelButtonText: t('uiAutomation.common.cancel'),
        type: 'warning'
      }
    )

    isDeleting.value = true
    const ids = selectedRecords.value.map(item => item.id)
    await batchDeleteAIExecutionRecords(ids)

    ElMessage.success(t('uiAutomation.ai.executionRecords.messages.deleteSuccess'))

    // 如果当前页数据全部被删除，且不是第一页，则跳转到上一页
    if (records.value.length === ids.length && currentPage.value > 1) {
      currentPage.value--
    }

    loadRecords()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error(t('uiAutomation.ai.executionRecords.messages.batchDeleteFailed'))
    }
  } finally {
    isDeleting.value = false
  }
}

// 轮询更新状态
const startPolling = () => {
  pollTimer = setInterval(() => {
    // 只有在第一页且没有打开详情框且没有正在加载时才轮询
    if (currentPage.value === 1 && !showDetailDialog.value && !loading.value) {
      // 检查当前列表是否有正在运行的任务，如果没有运行中的任务，则不轮询
      const hasActiveTasks = records.value.some(r => r.status === 'running' || r.status === 'pending')
      if (!hasActiveTasks) {
        return
      }

      // 静默刷新，不显示 loading，带上搜索条件
      const params = {
        page: 1,
        page_size: pageSize.value
      }
      if (searchText.value.trim()) {
        params.search = searchText.value.trim()
      }
      getAIExecutionRecords(params).then(response => {
        // 只有当没有选中项时才更新列表，避免干扰用户选择
        if (selectedRecords.value.length === 0) {
          records.value = response.data.results || []
          total.value = response.data.count || 0
        }
      }).catch(console.error)
    }
  }, 5000)
}

onMounted(() => {
  loadRecords()
  startPolling()
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
})
</script>

<style lang="scss" scoped>
.execution-records-shell {
  min-height: 100%;
}

.filters {
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.filters__actions {
  display: flex;
  gap: 12px;
}

.table-container {
  margin-top: 20px;
}

.record-detail {
  .detail-item {
    margin-bottom: 15px;
    .label {
      font-weight: bold;
      margin-right: 10px;
    }
  }

  .log-container {
    background-color: #1e1e1e;
    color: #fff;
    padding: 15px;
    border-radius: 4px;
    max-height: 400px;
    overflow-y: auto;
    font-family: monospace;

    pre {
      margin: 0;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  }

  .task-description-container {
    background-color: #f5f7fa;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    padding: 12px 15px;
    margin-top: 8px;

    .task-description-content {
      color: #606266;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  }
}

.mt-15 {
  margin-top: 15px;
}
</style>
