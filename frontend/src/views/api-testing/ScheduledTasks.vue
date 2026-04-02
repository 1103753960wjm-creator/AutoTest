<template>
  <div class="scheduled-tasks">
    <ListShell class="scheduled-tasks-shell">
      <template #actions>
        <el-button type="primary" @click="handleCreateClick">
          <el-icon><Plus /></el-icon>
          {{ $t('apiTesting.scheduledTask.createTask') }}
        </el-button>
      </template>

      <div class="filters">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-select v-model="filters.task_type" :placeholder="$t('apiTesting.scheduledTask.taskType')" clearable>
              <el-option :label="$t('apiTesting.scheduledTask.taskTypes.testSuite')" value="TEST_SUITE" />
              <el-option :label="$t('apiTesting.scheduledTask.taskTypes.apiRequest')" value="API_REQUEST" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="filters.trigger_type" :placeholder="$t('apiTesting.scheduledTask.triggerType')" clearable>
              <el-option :label="$t('apiTesting.scheduledTask.triggerTypes.cron')" value="CRON" />
              <el-option :label="$t('apiTesting.scheduledTask.triggerTypes.interval')" value="INTERVAL" />
              <el-option :label="$t('apiTesting.scheduledTask.triggerTypes.once')" value="ONCE" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="filters.status" :placeholder="$t('apiTesting.scheduledTask.taskStatus')" clearable>
              <el-option :label="$t('apiTesting.scheduledTask.status.active')" value="ACTIVE" />
              <el-option :label="$t('apiTesting.scheduledTask.status.paused')" value="PAUSED" />
              <el-option :label="$t('apiTesting.scheduledTask.status.completed')" value="COMPLETED" />
              <el-option :label="$t('apiTesting.scheduledTask.status.failed')" value="FAILED" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-button @click="resetFilters">{{ $t('apiTesting.common.reset') }}</el-button>
            <el-button type="primary" @click="loadTasks">{{ $t('apiTesting.common.search') }}</el-button>
          </el-col>
        </el-row>
      </div>

      <div class="task-list">
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
          @primary-action="loadTasks"
        />
        <StateSearchEmpty
          v-else-if="pageState === UI_PAGE_STATE.SEARCH_EMPTY"
          compact
          :primary-action-text="$t('common.uiState.actions.clearFilters')"
          @primary-action="resetFilters"
        />
        <StateEmpty v-else-if="pageState === UI_PAGE_STATE.EMPTY" compact />
        <div v-else class="table-container">
          <UnifiedListTable
            v-model:currentPage="pagination.current"
            v-model:pageSize="pagination.size"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            :data="tasks"
            :loading="loading"
            row-key="id"
            selection-mode="none"
            :actions="{ view: false, edit: false, delete: false }"
            :action-column-width="200"
            @page-change="loadTasks"
          >
            <el-table-column prop="name" :label="$t('apiTesting.scheduledTask.taskName')" min-width="200" />
            <el-table-column prop="task_type" :label="$t('apiTesting.scheduledTask.taskType')" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.task_type === 'TEST_SUITE' ? 'success' : 'primary'">
                  {{ scope.row.task_type === 'TEST_SUITE' ? $t('apiTesting.scheduledTask.taskTypes.testSuiteShort') : $t('apiTesting.scheduledTask.taskTypes.apiRequestShort') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="trigger_type" :label="$t('apiTesting.scheduledTask.triggerType')" width="120">
              <template #default="scope">
                <el-tag>
                  {{ getTriggerTypeText(scope.row.trigger_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" :label="$t('apiTesting.common.status')" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'ACTIVE' ? 'success' : scope.row.status === 'PAUSED' ? 'warning' : 'info'">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notification_type_display" :label="$t('apiTesting.scheduledTask.notificationType')" width="120">
              <template #default="scope">
                <el-tag
                  :type="getNotificationTypeTag(scope.row.notification_type_display)"
                  size="small"
                >
                  {{ scope.row.notification_type_display || '-' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="next_run_time" :label="$t('apiTesting.scheduledTask.nextRunTime')" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.next_run_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="last_run_time" :label="$t('apiTesting.scheduledTask.lastRunTime')" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.last_run_time) }}
              </template>
            </el-table-column>
            <template #actions="{ row }">
              <el-button size="small" @click="runTaskNow(row)" :loading="row.running">
                {{ $t('apiTesting.scheduledTask.runNow') }}
              </el-button>
              <el-dropdown @command="(command) => handleTaskAction(command, row)">
                <el-button size="small">
                  {{ $t('apiTesting.common.more') }}<el-icon><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">{{ $t('apiTesting.common.edit') }}</el-dropdown-item>
                    <el-dropdown-item command="pause" v-if="row.status === 'ACTIVE'">{{ $t('apiTesting.scheduledTask.pause') }}</el-dropdown-item>
                    <el-dropdown-item command="activate" v-if="row.status === 'PAUSED'">{{ $t('apiTesting.scheduledTask.activate') }}</el-dropdown-item>
                    <el-dropdown-item command="logs">{{ $t('apiTesting.scheduledTask.executionLogs') }}</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>{{ $t('apiTesting.common.delete') }}</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </UnifiedListTable>
        </div>
      </div>
    </ListShell>

    <!-- 鍒嗛〉 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.current"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadTasks"
        @current-change="loadTasks"
      />
    </div>

    <!-- 鍒涘缓/缂栬緫瀵硅瘽妗?-->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTask ? $t('apiTesting.scheduledTask.editTask') : $t('apiTesting.scheduledTask.createTask')"
      width="800px"
      :close-on-click-modal="false"
      @close="resetTaskForm"
    >
      <el-form :model="taskForm" label-width="120px">
        <el-form-item :label="$t('apiTesting.scheduledTask.taskName')" required>
          <el-input v-model="taskForm.name" :placeholder="$t('apiTesting.scheduledTask.inputTaskName')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.taskDescription')">
          <el-input v-model="taskForm.description" type="textarea" :placeholder="$t('apiTesting.scheduledTask.inputTaskDesc')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.taskType')" required>
          <el-radio-group v-model="taskForm.task_type">
            <el-radio label="TEST_SUITE">{{ $t('apiTesting.scheduledTask.taskTypes.testSuite') }}</el-radio>
            <el-radio label="API_REQUEST">{{ $t('apiTesting.scheduledTask.taskTypes.apiRequest') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.triggerType')" required>
          <el-radio-group v-model="taskForm.trigger_type">
            <el-radio label="CRON">{{ $t('apiTesting.scheduledTask.triggerTypes.cron') }}</el-radio>
            <el-radio label="INTERVAL">{{ $t('apiTesting.scheduledTask.triggerTypes.interval') }}</el-radio>
            <el-radio label="ONCE">{{ $t('apiTesting.scheduledTask.triggerTypes.once') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 鏍规嵁瑙﹀彂鍣ㄧ被鍨嬫樉绀轰笉鍚岄厤缃?-->
        <el-form-item v-if="taskForm.trigger_type === 'CRON'" :label="$t('apiTesting.scheduledTask.cronExpression')" required>
          <el-input v-model="taskForm.cron_expression" placeholder="0 0 * * *" />
          <div class="cron-help">
            <el-tooltip
              raw-content
              placement="top"
            >
              <template #content>
                <div style="line-height: 1.6; text-align: left;">
                  <div>{{ $t('apiTesting.scheduledTask.cronHelp.format') }}</div>
                  <div>鈥?{{ $t('apiTesting.scheduledTask.cronHelp.minute') }}</div>
                  <div>鈥?{{ $t('apiTesting.scheduledTask.cronHelp.hour') }}</div>
                  <div>鈥?{{ $t('apiTesting.scheduledTask.cronHelp.day') }}</div>
                  <div>鈥?{{ $t('apiTesting.scheduledTask.cronHelp.month') }}</div>
                  <div>鈥?{{ $t('apiTesting.scheduledTask.cronHelp.week') }}</div>
                  <div style="margin-top: 8px;">{{ $t('apiTesting.scheduledTask.cronHelp.examples') }}</div>
                  <div>鈥?{{ $t('apiTesting.scheduledTask.cronHelp.daily') }}</div>
                  <div>鈥?{{ $t('apiTesting.scheduledTask.cronHelp.hourly') }}</div>
                  <div>鈥?{{ $t('apiTesting.scheduledTask.cronHelp.weekly') }}</div>
                  <div>鈥?{{ $t('apiTesting.scheduledTask.cronHelp.monthly') }}</div>
                </div>
              </template>
              <span style="cursor: pointer; color: #409EFF;">{{ $t('apiTesting.scheduledTask.cronHelpLink') }}</span>
            </el-tooltip>
          </div>
        </el-form-item>

        <el-form-item v-if="taskForm.trigger_type === 'INTERVAL'" :label="$t('apiTesting.scheduledTask.intervalTime')" required>
          <el-input-number v-model="taskForm.interval_seconds" :min="60" :step="60" />
          <span class="unit">{{ $t('apiTesting.scheduledTask.seconds') }}</span>
        </el-form-item>

        <el-form-item v-if="taskForm.trigger_type === 'ONCE'" :label="$t('apiTesting.scheduledTask.executeTime')" required>
          <el-date-picker
            v-model="taskForm.execute_at"
            type="datetime"
            :placeholder="$t('apiTesting.scheduledTask.selectExecuteTime')"
          />
        </el-form-item>

        <!-- 鏍规嵁浠诲姟绫诲瀷鏄剧ず涓嶅悓閰嶇疆 -->
        <el-form-item v-if="taskForm.task_type === 'TEST_SUITE'" :label="$t('apiTesting.automation.testSuite')" required>
          <el-select v-model="taskForm.test_suite" :placeholder="$t('apiTesting.scheduledTask.selectTestSuite')">
            <el-option
              v-for="suite in testSuites"
              :key="suite.id"
              :label="suite.name"
              :value="suite.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item v-if="taskForm.task_type === 'API_REQUEST'" :label="$t('apiTesting.scheduledTask.apiRequest')" required>
          <el-select v-model="taskForm.api_request" :placeholder="$t('apiTesting.scheduledTask.selectApiRequest')">
            <el-option
              v-for="request in apiRequests"
              :key="request.id"
              :label="request.name"
              :value="request.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.executeEnvironment')">
          <el-select v-model="taskForm.environment" :placeholder="$t('apiTesting.scheduledTask.selectEnvironment')">
            <el-option
              v-for="env in environments"
              :key="env.id"
              :label="env.name"
              :value="env.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.scheduledTask.notificationSettings')">
          <el-checkbox v-model="taskForm.notify_on_success">{{ $t('apiTesting.scheduledTask.notifyOnSuccess') }}</el-checkbox>
          <el-checkbox v-model="taskForm.notify_on_failure">{{ $t('apiTesting.scheduledTask.notifyOnFailure') }}</el-checkbox>
        </el-form-item>

        <el-form-item v-if="taskForm.notify_on_success || taskForm.notify_on_failure" :label="$t('apiTesting.scheduledTask.notificationType')">
          <el-select v-model="taskForm.notification_type" :placeholder="$t('apiTesting.scheduledTask.selectNotificationType')">
            <el-option :label="$t('apiTesting.notification.types.email')" value="email" />
            <el-option :label="$t('apiTesting.notification.types.webhook')" value="webhook" />
            <el-option :label="$t('apiTesting.notification.types.both')" value="both" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="(taskForm.notify_on_success || taskForm.notify_on_failure) && taskForm.notification_type !== 'webhook'" :label="$t('apiTesting.scheduledTask.notifyEmails')">
          <el-select
            v-model="taskForm.notify_emails"
            multiple
            filterable
            :placeholder="$t('apiTesting.scheduledTask.selectNotifyEmails')"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.display_name"
              :value="user.email"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="submitTaskForm" :loading="submitting">
          {{ editingTask ? $t('apiTesting.common.update') : $t('apiTesting.common.create') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 鎵ц鏃ュ織瀵硅瘽妗?-->
    <el-dialog v-model="showLogsDialog" :title="$t('apiTesting.scheduledTask.executionLogs')" width="1000px">
      <el-table :data="executionLogs" v-loading="logsLoading">
        <el-table-column prop="start_time" :label="$t('apiTesting.scheduledTask.startTime')" width="180">
          <template #default="scope">
            <div class="time-cell">{{ formatDateTime(scope.row.start_time) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="end_time" :label="$t('apiTesting.scheduledTask.endTime')" width="180">
          <template #default="scope">
            <div class="time-cell">{{ formatDateTime(scope.row.end_time) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('apiTesting.common.status')" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'COMPLETED' ? 'success' : 'danger'">
              {{ scope.row.status === 'COMPLETED' ? $t('apiTesting.common.success') : $t('apiTesting.common.failed') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_message" :label="$t('apiTesting.scheduledTask.errorMessage')" width="300" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Plus, ArrowDown } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { UnifiedListTable } from '@/components/platform-shared'
import { ListShell } from '@/components/page-shells'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'
import {
  getScheduledTasks,
  createScheduledTask,
  updateScheduledTask,
  deleteScheduledTask,
  runScheduledTask,
  getExecutionLogs,
  getTestSuites,
  getApiRequests,
  getEnvironments,
  getUsers
} from '@/api/api-testing.js'

const { t } = useI18n()
const router = useRouter()

const getStatusText = (status) => {
  const statusKey = {
    'ACTIVE': 'active',
    'PAUSED': 'paused',
    'COMPLETED': 'completed',
    'FAILED': 'failed'
  }[status]
  return statusKey ? t(`apiTesting.scheduledTask.status.${statusKey}`) : status
}

const getTriggerTypeText = (type) => {
  const typeKey = {
    'CRON': 'cron',
    'INTERVAL': 'interval',
    'ONCE': 'once'
  }[type]
  return typeKey ? t(`apiTesting.scheduledTask.triggerTypes.${typeKey}`) : type
}

const tasks = ref([])
const executionLogs = ref([])
const testSuites = ref([])
const apiRequests = ref([])
const environments = ref([])
const users = ref([]) // 娣诲姞鐢ㄦ埛鍒楄〃
const loading = ref(false)
const logsLoading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showLogsDialog = ref(false)
const editingTask = ref(null)
const hasLoaded = ref(false)
const requestState = ref(`${UI_PAGE_STATE.READY}`)
const requestErrorMessage = ref('')

const filters = reactive({
  task_type: '',
  trigger_type: '',
  status: ''
})

// 鍒嗛〉閰嶇疆
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

const hasActiveFilter = computed(() => Boolean(
  filters.task_type ||
  filters.trigger_type ||
  filters.status
))

const pageState = computed(() => {
  let state = String(UI_PAGE_STATE.READY)
  if (loading.value && !hasLoaded.value) {
    state = UI_PAGE_STATE.LOADING
  } else if (requestState.value === UI_PAGE_STATE.FORBIDDEN) {
    state = UI_PAGE_STATE.FORBIDDEN
  } else if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    state = UI_PAGE_STATE.REQUEST_ERROR
  } else if (tasks.value.length === 0) {
    state = hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return state
})

// 琛ㄥ崟鏁版嵁
const taskForm = reactive({
  name: '',
  description: '',
  task_type: 'TEST_SUITE',
  trigger_type: 'CRON',
  cron_expression: '0 0 * * *',
  interval_seconds: 3600,
  execute_at: '',
  test_suite: '',
  api_request: '',
  environment: '',
  notify_on_success: false,
  notify_on_failure: false,
  notify_emails: []
})

// 鐢熷懡鍛ㄦ湡
onMounted(() => {
  loadTasks()
  loadTestSuites()
  loadApiRequests()
  loadEnvironments()
  loadUsers() // 鍔犺浇鐢ㄦ埛鍒楄〃
})

// 鍔犺浇浠诲姟鍒楄〃
const loadTasks = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  requestErrorMessage.value = ''
  let shouldRefetch = false
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.size,
      ...filters
    }
    const response = await getScheduledTasks(params)
    tasks.value = response.data.results
    pagination.total = response.data.count
    const maxPage = Math.max(1, Math.ceil((pagination.total || 0) / pagination.size || 1))
    if (pagination.current > maxPage) {
      pagination.current = maxPage
      shouldRefetch = true
      return
    }
    hasLoaded.value = true
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadTasksFailed'))
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
  } finally {
    if (!shouldRefetch) {
      loading.value = false
    }
  }
  if (shouldRefetch) {
    await loadTasks()
  }
}

// 鍔犺浇娴嬭瘯濂椾欢
const loadTestSuites = async () => {
  try {
    const response = await getTestSuites()
    testSuites.value = response.data.results
  } catch (error) {
    console.error('鍔犺浇娴嬭瘯濂椾欢澶辫触:', error)
  }
}

// 鍔犺浇API璇锋眰
const loadApiRequests = async () => {
  try {
    const response = await getApiRequests()
    apiRequests.value = response.data.results
  } catch (error) {
    console.error('鍔犺浇API璇锋眰澶辫触:', error)
  }
}

// 鍔犺浇鐜
const loadEnvironments = async () => {
  try {
    const response = await getEnvironments()
    environments.value = response.data.results
  } catch (error) {
    console.error('鍔犺浇鐜澶辫触:', error)
  }
}

// 鍔犺浇鐢ㄦ埛鍒楄〃
const loadUsers = async () => {
  try {
    const response = await getUsers()
    // 澶勭悊鍒嗛〉鏁版嵁缁撴瀯
    const usersData = response.data.results || response.data
    users.value = usersData.map(user => ({
      ...user,
      display_name: user.first_name ? `${user.first_name}（${user.email}）` : `${user.username}（${user.email}）`
    }))
  } catch (error) {
    console.error('鍔犺浇鐢ㄦ埛鍒楄〃澶辫触:', error)
  }
}

// 鏂板缓鎸夐挳鐐瑰嚮
const handleCreateClick = () => {
  console.log('鏂板缓鎸夐挳鐐瑰嚮')
  editingTask.value = null
  resetTaskForm()
  showCreateDialog.value = true
}

// 閲嶇疆琛ㄥ崟
const resetTaskForm = () => {
  Object.assign(taskForm, {
    name: '',
    description: '',
    task_type: 'TEST_SUITE',
    trigger_type: 'CRON',
    cron_expression: '0 0 * * *',
    interval_seconds: 3600,
    execute_at: '',
    test_suite: '',
    api_request: '',
    environment: '',
    notify_on_success: false,
    notify_on_failure: false,
    notification_type: 'email',
    notify_emails: []
  })
}

const resetFilters = () => {
  Object.assign(filters, {
    task_type: '',
    trigger_type: '',
    status: ''
  })
  pagination.current = 1
  loadTasks()
}

// 鎻愪氦浠诲姟琛ㄥ崟
const submitTaskForm = async () => {
  submitting.value = true
  try {
    const submitData = {
      name: taskForm.name,
      description: taskForm.description,
      task_type: taskForm.task_type,
      trigger_type: taskForm.trigger_type,
      notify_on_success: taskForm.notify_on_success,
      notify_on_failure: taskForm.notify_on_failure,
      notification_type_input: taskForm.notification_type,
      notify_emails: taskForm.notify_emails,
      environment: taskForm.environment
    }

    if (taskForm.trigger_type === 'CRON') {
      submitData.cron_expression = taskForm.cron_expression
    } else if (taskForm.trigger_type === 'INTERVAL') {
      submitData.interval_seconds = taskForm.interval_seconds
    } else if (taskForm.trigger_type === 'ONCE') {
      submitData.execute_at = taskForm.execute_at
    }

    // 鏍规嵁浠诲姟绫诲瀷娣诲姞瀵瑰簲瀛楁
    if (taskForm.task_type === 'TEST_SUITE') {
      submitData.test_suite = taskForm.test_suite
    } else if (taskForm.task_type === 'API_REQUEST') {
      submitData.api_request = taskForm.api_request
    }

    if (editingTask.value) {
      await updateScheduledTask(editingTask.value.id, submitData)
      ElMessage.success(t('apiTesting.messages.success.taskUpdated'))
    } else {
      await createScheduledTask(submitData)
      ElMessage.success(t('apiTesting.messages.success.taskCreated'))
    }
    showCreateDialog.value = false
    loadTasks()
  } catch (error) {
    console.error('Task operation failed:', error)
    ElMessage.error(error.response?.data?.error ||
                   error.response?.data?.detail ||
                   (editingTask.value ? t('apiTesting.messages.error.updateTaskFailed') : t('apiTesting.messages.error.createTaskFailed')))
  } finally {
    submitting.value = false
  }
}

// 绔嬪嵆鎵ц浠诲姟
const runTaskNow = async (task) => {
  try {
    task.running = true
    await runScheduledTask(task.id)
    ElMessage.success(t('apiTesting.messages.success.taskStarted'))
    setTimeout(() => {
      loadTasks()
    }, 2000)
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.executeTaskFailed'))
  } finally {
    task.running = false
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
}

// 鑾峰彇閫氱煡绫诲瀷鏍囩鏍峰紡
const getNotificationTypeTag = (typeDisplay) => {
  const typeMap = {
    '邮箱通知': '',
    'Webhook机器人': 'primary',
    '两种都发送': 'warning'
  }
  return typeMap[typeDisplay] || 'info'
}

// 鏌ョ湅鎵ц鏃ュ織
const viewTaskLogs = async (task) => {
  logsLoading.value = true
  try {
    const response = await getExecutionLogs(task.id)
    executionLogs.value = response.data.results || response.data
    showLogsDialog.value = true
  } catch (error) {
    console.error('Load execution logs failed:', error)
    ElMessage.error(t('apiTesting.messages.error.loadLogsFailed'))
  } finally {
    logsLoading.value = false
  }
}

// 澶勭悊浠诲姟鎿嶄綔
const handleTaskAction = (command, task) => {
  switch (command) {
    case 'pause':
      pauseTask(task)
      break
    case 'activate':
      activateTask(task)
      break
    case 'edit':
      editTask(task)
      break
    case 'logs':
      viewTaskLogs(task)
      break
    case 'delete':
      deleteTask(task)
      break
  }
}

// 缂栬緫浠诲姟
const editTask = (task) => {
  editingTask.value = task
  Object.assign(taskForm, {
    name: task.name,
    description: task.description,
    task_type: task.task_type,
    trigger_type: task.trigger_type,
    cron_expression: task.cron_expression,
    interval_seconds: task.interval_seconds,
    execute_at: task.execute_at,
    test_suite: task.test_suite || null,
    api_request: task.api_request || null,
    environment: task.environment || null,
    notify_on_success: task.notify_on_success,
    notify_on_failure: task.notify_on_failure,
    notification_type: task.notification_type || 'email',
    notify_emails: task.notify_emails || []
  })
  console.log('缂栬緫浠诲姟鏁版嵁鍥炴樉:', {
    test_suite: task.test_suite,
    environment: task.environment,
    taskForm_test_suite: taskForm.test_suite,
    taskForm_environment: taskForm.environment
  })
  showCreateDialog.value = true
}

// 鏆傚仠浠诲姟
const pauseTask = async (task) => {
  try {
    await api.post(`/api-testing/scheduled-tasks/${task.id}/pause/`)
    ElMessage.success(t('apiTesting.messages.success.taskPaused'))
    loadTasks()
  } catch (error) {
    console.error('Pause task failed:', error)
    ElMessage.error(t('apiTesting.messages.error.pauseTaskFailed'))
  }
}

const activateTask = async (task) => {
  try {
    await api.post(`/api-testing/scheduled-tasks/${task.id}/activate/`)
    ElMessage.success(t('apiTesting.messages.success.taskActivated'))
    loadTasks()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.activateTaskFailed'))
  }
}

// 鍒犻櫎浠诲姟
const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.scheduledTask.confirmDeleteTask'),
      t('apiTesting.common.tip'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )
    await deleteScheduledTask(task.id)
    ElMessage.success(t('apiTesting.messages.success.taskDeleted'))
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.deleteTaskFailed'))
    }
  }
}
</script>

<style scoped>
.scheduled-tasks {
  min-height: 100%;
}

.scheduled-tasks-shell {
  min-height: 100%;
}

.filters {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.task-list {
  flex: 1;
  overflow: hidden;
}

.pagination {
  display: none;
}

.table-container {
  overflow: hidden;

  :deep(.unified-list-table) {
    display: flex;
    flex-direction: column;
  }
}

.cron-help {
  margin-top: 8px;
  font-size: 12px;
}

.unit {
  margin-left: 8px;
  color: #606266;
}
</style>
