<template>
  <div class="request-history">
    <DetailResultShell class="request-history-shell">
      <template #actions>
        <el-button
          type="danger"
          :disabled="selectedIds.length === 0"
          @click="handleBatchDelete"
        >
          {{ $t('apiTesting.history.batchDelete') }}
        </el-button>
        <el-button @click="clearHistory" type="danger" plain :loading="clearingHistory">
          {{ $t('apiTesting.history.clearHistory') }}
        </el-button>
      </template>

      <div class="filters">
        <el-input
          v-model="searchText"
          :placeholder="$t('apiTesting.history.searchRequest')"
          style="width: 200px"
          clearable
          @input="loadHistory"
        />
      </div>

      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane :label="$t('apiTesting.history.httpRequest')" name="HTTP">
          <StateLoading v-if="activeTab === 'HTTP' && pageState === UI_PAGE_STATE.LOADING" compact />
          <StateForbidden
            v-else-if="activeTab === 'HTTP' && pageState === UI_PAGE_STATE.FORBIDDEN"
            compact
            :primary-action-text="$t('common.uiState.actions.goHome')"
            @primary-action="router.push('/home')"
          />
          <StateError
            v-else-if="activeTab === 'HTTP' && pageState === UI_PAGE_STATE.REQUEST_ERROR"
            compact
            :description="requestErrorMessage || $t('common.uiState.error.description')"
            @primary-action="loadHistory"
          />
          <StateSearchEmpty
            v-else-if="activeTab === 'HTTP' && pageState === UI_PAGE_STATE.SEARCH_EMPTY"
            compact
            :primary-action-text="$t('common.uiState.actions.clearFilters')"
            @primary-action="resetHistoryFilters"
          />
          <StateEmpty v-else-if="activeTab === 'HTTP' && pageState === UI_PAGE_STATE.EMPTY" compact />
          <HistoryTable
            v-else
            :data="httpHistory"
            :loading="loading"
            @view-detail="viewDetail"
            @retry-request="retryRequest"
            @selection-change="handleSelectionChange"
            @delete-item="handleDelete"
          />
        </el-tab-pane>
        <el-tab-pane :label="$t('apiTesting.history.websocketRequest')" name="WEBSOCKET">
          <StateLoading v-if="activeTab === 'WEBSOCKET' && pageState === UI_PAGE_STATE.LOADING" compact />
          <StateForbidden
            v-else-if="activeTab === 'WEBSOCKET' && pageState === UI_PAGE_STATE.FORBIDDEN"
            compact
            :primary-action-text="$t('common.uiState.actions.goHome')"
            @primary-action="router.push('/home')"
          />
          <StateError
            v-else-if="activeTab === 'WEBSOCKET' && pageState === UI_PAGE_STATE.REQUEST_ERROR"
            compact
            :description="requestErrorMessage || $t('common.uiState.error.description')"
            @primary-action="loadHistory"
          />
          <StateSearchEmpty
            v-else-if="activeTab === 'WEBSOCKET' && pageState === UI_PAGE_STATE.SEARCH_EMPTY"
            compact
            :primary-action-text="$t('common.uiState.actions.clearFilters')"
            @primary-action="resetHistoryFilters"
          />
          <StateEmpty v-else-if="activeTab === 'WEBSOCKET' && pageState === UI_PAGE_STATE.EMPTY" compact />
          <HistoryTable
            v-else
            :data="websocketHistory"
            :loading="loading"
            @view-detail="viewDetail"
            @retry-request="retryRequest"
            @selection-change="handleSelectionChange"
            @delete-item="handleDelete"
          />
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-pagination
          v-if="pageState === UI_PAGE_STATE.READY"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="pagination"
        />
      </template>
    </DetailResultShell>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="$t('apiTesting.history.requestDetail')"
      width="80%"
      :top="'5vh'"
    >
      <div v-if="selectedHistory" class="history-detail">
        <el-descriptions :title="$t('apiTesting.history.basicInfo')" :column="2" border>
          <el-descriptions-item :label="$t('apiTesting.interface.requestName')">
            {{ selectedHistory.request.name }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.requestMethod')">
            <el-tag :type="getMethodType(selectedHistory.request.method)">
              {{ selectedHistory.request.method }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.statusCode')">
            <el-tag :type="getStatusType(selectedHistory.status_code)">
              {{ selectedHistory.status_code || $t('apiTesting.history.noResponse') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.responseTime')">
            {{ selectedHistory.response_time?.toFixed(0) || 0 }}ms
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.executionTime')">
            {{ formatDate(selectedHistory.executed_at) }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('apiTesting.history.executor')">
            {{ selectedHistory.executed_by.username }}
          </el-descriptions-item>
        </el-descriptions>

        <el-tabs v-model="detailTab" class="detail-tabs">
          <el-tab-pane :label="$t('apiTesting.history.requestInfo')" name="request">
            <div class="detail-section">
              <h4>{{ $t('apiTesting.history.requestUrl') }}</h4>
              <el-input v-model="selectedHistory.request_data.url" readonly />

              <h4>{{ $t('apiTesting.history.requestHeaders') }}</h4>
              <el-table :data="formatHeaders(selectedHistory.request_data.headers)" style="width: 100%">
                <el-table-column prop="key" label="Key" width="200" />
                <el-table-column prop="value" label="Value" />
              </el-table>

              <h4 v-if="selectedHistory.request_data.params && Object.keys(selectedHistory.request_data.params).length > 0">
                {{ $t('apiTesting.history.requestParams') }}
              </h4>
              <el-table
                v-if="selectedHistory.request_data.params && Object.keys(selectedHistory.request_data.params).length > 0"
                :data="formatHeaders(selectedHistory.request_data.params)"
                style="width: 100%"
              >
                <el-table-column prop="key" label="Key" width="200" />
                <el-table-column prop="value" label="Value" />
              </el-table>

              <h4 v-if="selectedHistory.request_data.body">{{ $t('apiTesting.history.requestBody') }}</h4>
              <pre v-if="selectedHistory.request_data.body" class="json-content">
                {{ JSON.stringify(selectedHistory.request_data.body, null, 2) }}
              </pre>
            </div>
          </el-tab-pane>

          <el-tab-pane :label="$t('apiTesting.history.responseInfo')" name="response">
            <div v-if="selectedHistory.response_data" class="detail-section">
              <h4>{{ $t('apiTesting.history.responseHeaders') }}</h4>
              <el-table :data="formatHeaders(selectedHistory.response_data.headers)" style="width: 100%">
                <el-table-column prop="key" label="Key" width="200" />
                <el-table-column prop="value" label="Value" />
              </el-table>

              <h4>{{ $t('apiTesting.history.responseBody') }}</h4>
              <div class="response-actions">
                <el-button size="small" @click="formatResponseBody">{{ $t('apiTesting.interface.format') }}</el-button>
                <el-button size="small" @click="copyResponseBody">{{ $t('apiTesting.common.copy') }}</el-button>
              </div>
              <pre class="json-content">{{ responseBodyText }}</pre>
            </div>

            <div v-else-if="selectedHistory.error_message" class="error-section">
              <h4>{{ $t('apiTesting.automation.status.failed') }}</h4>
              <el-alert
                :title="selectedHistory.error_message"
                type="error"
                :closable="false"
                show-icon
              />
            </div>

            <div v-else class="empty-response">
              <el-empty :description="$t('apiTesting.history.noResponseData')" />
            </div>
          </el-tab-pane>

          <el-tab-pane :label="$t('apiTesting.interface.assertionResults')" name="assertions">
            <div v-if="hasAssertionResults" class="detail-section">
              <div
                v-for="(result, index) in selectedHistory.assertions_results"
                :key="`${result.name || result.type || 'assertion'}-${index}`"
                class="assertion-result-item"
                :class="{ 'is-passed': result.passed, 'is-failed': !result.passed }"
              >
                <div class="assertion-result-header">
                  <span class="assertion-result-title">
                    {{ result.name || `${$t('apiTesting.interface.assertions')} ${index + 1}` }}
                  </span>
                  <el-tag :type="result.passed ? 'success' : 'danger'" size="small">
                    {{ result.passed ? $t('apiTesting.interface.passed') : $t('apiTesting.interface.failed') }}
                  </el-tag>
                </div>
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item :label="$t('apiTesting.interface.selectAssertionType')">
                    {{ formatAssertionType(result.type) }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('apiTesting.interface.expected')">
                    {{ formatAssertionValue(result.expected) }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('apiTesting.interface.actual')">
                    {{ formatAssertionValue(result.actual) }}
                  </el-descriptions-item>
                  <el-descriptions-item v-if="result.error" :label="$t('apiTesting.interface.error')">
                    {{ result.error }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>

            <div v-else class="empty-response">
              <el-empty :description="$t('apiTesting.interface.noAssertions')" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">{{ $t('apiTesting.common.close') }}</el-button>
        <el-button type="primary" @click="retryRequest(selectedHistory)">
          {{ $t('apiTesting.history.retryRequest') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { deleteRequestHistory, batchDeleteRequestHistory, clearRequestHistory, executeApiTestCase, getRequestHistory } from '@/api/api-testing'
import dayjs from 'dayjs'
import HistoryTable from './components/HistoryTable.vue'
import { DetailResultShell } from '@/components/page-shells'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const activeTab = ref('HTTP')
const httpHistory = ref([])
const websocketHistory = ref([])
const loading = ref(false)
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const showDetailDialog = ref(false)
const selectedHistory = ref(null)
const detailTab = ref('request')
const selectedIds = ref([])
const hasLoaded = ref(false)
const requestState = ref(`${UI_PAGE_STATE.READY}`)
const requestErrorMessage = ref('')
const clearingHistory = ref(false)

const currentHistory = computed(() => {
  return activeTab.value === 'HTTP' ? httpHistory.value : websocketHistory.value
})

const hasActiveFilter = computed(() => Boolean(searchText.value))

const pageState = computed(() => {
  let state = String(UI_PAGE_STATE.READY)
  if (loading.value && !hasLoaded.value) {
    state = UI_PAGE_STATE.LOADING
  } else if (requestState.value === UI_PAGE_STATE.FORBIDDEN) {
    state = UI_PAGE_STATE.FORBIDDEN
  } else if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    state = UI_PAGE_STATE.REQUEST_ERROR
  } else if (currentHistory.value.length === 0) {
    state = hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return state
})

const responseBodyText = computed(() => {
  if (!selectedHistory.value?.response_data) return ''
  
  try {
    if (selectedHistory.value.response_data.json) {
      return JSON.stringify(selectedHistory.value.response_data.json, null, 2)
    } else {
      return selectedHistory.value.response_data.body || ''
    }
  } catch (e) {
    return selectedHistory.value.response_data.body || ''
  }
})

const hasAssertionResults = computed(() => {
  return Array.isArray(selectedHistory.value?.assertions_results) && selectedHistory.value.assertions_results.length > 0
})

const getMethodType = (method) => {
  const typeMap = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return typeMap[method] || 'info'
}

const getStatusType = (status) => {
  if (!status) return 'info'
  if (status >= 200 && status < 300) return 'success'
  if (status >= 300 && status < 400) return 'warning'
  if (status >= 400) return 'danger'
  return 'info'
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss')
}

const formatHeaders = (headers) => {
  if (!headers || typeof headers !== 'object') return []
  return Object.keys(headers).map(key => ({
    key,
    value: headers[key]
  }))
}

const formatAssertionValue = (value) => {
  if (value === undefined || value === null || value === '') {
    return t('apiTesting.interface.notSet')
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  return String(value)
}

const formatAssertionType = (type) => {
  const typeMap = {
    status_code: t('apiTesting.interface.assertionTypes.statusCode'),
    response_time: t('apiTesting.interface.assertionTypes.responseTime'),
    contains: t('apiTesting.interface.assertionTypes.contains'),
    json_path: t('apiTesting.interface.assertionTypes.jsonPath'),
    header: t('apiTesting.interface.assertionTypes.header'),
    equals: t('apiTesting.interface.assertionTypes.equals')
  }

  return typeMap[type] || type || t('apiTesting.interface.notSet')
}

const loadHistory = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  requestErrorMessage.value = ''
  let shouldRefetch = false
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      request__request_type: activeTab.value
    }

    if (route.query.requestId) {
      params.request = route.query.requestId
    }

    if (searchText.value) {
      params.search = searchText.value
    }

    const response = await getRequestHistory(params)
    const data = response.data.results || response.data

    if (activeTab.value === 'HTTP') {
      httpHistory.value = data
    } else {
      websocketHistory.value = data
    }

    total.value = response.data.count || data.length
    const maxPage = Math.max(1, Math.ceil((total.value || 0) / pageSize.value || 1))
    if (currentPage.value > maxPage) {
      currentPage.value = maxPage
      shouldRefetch = true
      return
    }
    hasLoaded.value = true
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadHistory'))
    console.error(error)
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
  } finally {
    if (!shouldRefetch) {
      loading.value = false
    }
  }
  if (shouldRefetch) {
    await loadHistory()
  }
}

const onTabChange = () => {
  currentPage.value = 1
  selectedIds.value = []
  loadHistory()
}

const resetHistoryFilters = () => {
  searchText.value = ''
  currentPage.value = 1
  loadHistory()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadHistory()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadHistory()
}

const viewDetail = (history) => {
  selectedHistory.value = history
  detailTab.value = 'request'
  showDetailDialog.value = true
}

const retryRequest = async (history) => {
  try {
    await executeApiTestCase(history.request.id, {
      environment_id: history.environment?.id
    })
    ElMessage.success(t('apiTesting.messages.success.requestRetried'))
    showDetailDialog.value = false
    await loadHistory()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.sendFailed'))
    console.error(error)
  }
}

const clearHistory = async () => {
  let confirmed = false
  try {
    const scopeText = route.query.requestId
      ? '当前接口测试用例的请求历史'
      : `当前 ${activeTab.value} 页签和搜索筛选范围内的请求历史`
    await ElMessageBox.confirm(
      `确定要清空${scopeText}吗？此操作不可恢复。`,
      t('apiTesting.messages.confirm.clearTitle'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )
    confirmed = true

    clearingHistory.value = true
    const params = {
      request__request_type: activeTab.value
    }

    if (route.query.requestId) {
      params.request = route.query.requestId
    }
    if (searchText.value) {
      params.search = searchText.value
    }

    const response = await clearRequestHistory(params)
    ElMessage.success(response.data?.message || '请求历史已清空')
    selectedIds.value = []
    currentPage.value = 1
    await loadHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || error.response?.data?.detail || '清空请求历史失败')
      console.error(error)
    }
  } finally {
    if (confirmed) {
      clearingHistory.value = false
    }
  }
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(t('apiTesting.history.confirmDelete'), t('apiTesting.common.tip'), {
    confirmButtonText: t('apiTesting.common.confirm'),
    cancelButtonText: t('apiTesting.common.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await deleteRequestHistory(row.id)
      ElMessage.success(t('apiTesting.messages.success.delete'))
      loadHistory()
    } catch (error) {
      console.error('Delete failed:', error)
      ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
    }
  })
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return

  ElMessageBox.confirm(t('apiTesting.history.confirmBatchDelete', { n: selectedIds.value.length }), t('apiTesting.common.tip'), {
    confirmButtonText: t('apiTesting.common.confirm'),
    cancelButtonText: t('apiTesting.common.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await batchDeleteRequestHistory(selectedIds.value)
      ElMessage.success(t('apiTesting.messages.success.batchDeleteSuccess'))
      selectedIds.value = []
      loadHistory()
    } catch (error) {
      console.error('Batch delete failed:', error)
      ElMessage.error(t('apiTesting.messages.error.batchDeleteFailed'))
    }
  })
}

const formatResponseBody = () => {
  if (selectedHistory.value?.response_data?.json) {
    // 已经格式化了
  }
}

const copyResponseBody = () => {
  if (responseBodyText.value) {
    navigator.clipboard.writeText(responseBodyText.value)
    ElMessage.success(t('apiTesting.messages.success.copiedToClipboard'))
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.request-history {
  min-height: 100%;
}

.request-history-shell {
  min-height: 100%;
}

.filters {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 4px;
}

.pagination {
  display: flex;
  justify-content: center;
}

.history-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-tabs {
  margin-top: 20px;
}

.detail-section {
  padding: 10px 0;
}

.detail-section h4 {
  margin: 20px 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.json-content {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  max-height: 400px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  border: 1px solid #e4e7ed;
}

.response-actions {
  margin-bottom: 10px;
}

.error-section {
  padding: 20px 0;
}

.empty-response {
  padding: 40px 0;
  text-align: center;
}
</style>
