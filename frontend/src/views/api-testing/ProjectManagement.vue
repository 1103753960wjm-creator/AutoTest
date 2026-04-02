<template>
  <div class="project-management">
    <ListShell class="project-management-shell">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          {{ $t('apiTesting.project.createProject') }}
        </el-button>
      </template>

      <div class="filters">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-input
              v-model="searchText"
              :placeholder="$t('apiTesting.project.inputProjectName')"
              clearable
              @clear="handleFilterChange"
              @keyup.enter="handleFilterChange"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="5">
            <el-select
              v-model="statusFilter"
              clearable
              :placeholder="$t('apiTesting.project.selectStatus')"
              @change="handleFilterChange"
            >
              <el-option :label="$t('apiTesting.project.status.notStarted')" value="NOT_STARTED" />
              <el-option :label="$t('apiTesting.project.status.inProgress')" value="IN_PROGRESS" />
              <el-option :label="$t('apiTesting.project.status.completed')" value="COMPLETED" />
            </el-select>
          </el-col>
          <el-col :span="5">
            <el-select
              v-model="projectTypeFilter"
              clearable
              :placeholder="$t('apiTesting.project.projectType')"
              @change="handleFilterChange"
            >
              <el-option label="HTTP" value="HTTP" />
              <el-option label="WebSocket" value="WEBSOCKET" />
            </el-select>
          </el-col>
          <el-col :span="6" class="filters__actions">
            <el-button type="primary" @click="handleFilterChange">
              {{ $t('apiTesting.common.search') }}
            </el-button>
            <el-button @click="resetFilters">
              {{ $t('apiTesting.common.reset') }}
            </el-button>
          </el-col>
        </el-row>
      </div>

      <div class="table-section">
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
          @primary-action="loadProjects"
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
            v-model:currentPage="currentPage"
            v-model:pageSize="pageSize"
            :total="total"
            :data="projects"
            :loading="loading"
            row-key="id"
            selection-mode="none"
            :actions="{ view: false, edit: false, delete: false }"
            :action-column-width="220"
            @page-change="loadProjects"
          >
            <el-table-column prop="name" :label="$t('apiTesting.project.projectName')" min-width="200" show-overflow-tooltip />
            <el-table-column prop="project_type" :label="$t('apiTesting.project.projectType')" width="120">
              <template #default="{ row }">
                <el-tag :type="row.project_type === 'HTTP' ? 'primary' : 'success'">
                  {{ row.project_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" :label="$t('apiTesting.project.projectStatus')" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="owner.username" :label="$t('apiTesting.project.owner')" width="150" />
            <el-table-column prop="start_date" :label="$t('apiTesting.project.startDate')" width="120" />
            <el-table-column prop="end_date" :label="$t('apiTesting.project.endDate')" width="120" />
            <el-table-column prop="created_at" :label="$t('apiTesting.project.createdAt')" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <template #actions="{ row }">
              <el-button link type="primary" @click="editProject(row)">
                {{ $t('apiTesting.common.edit') }}
              </el-button>
              <el-button link type="primary" @click="viewProject(row)">
                {{ $t('apiTesting.common.view') }}
              </el-button>
              <el-button link type="danger" @click="deleteProject(row)">
                {{ $t('apiTesting.common.delete') }}
              </el-button>
            </template>
          </UnifiedListTable>
        </div>
      </div>
    </ListShell>

    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? $t('apiTesting.project.editProject') : $t('apiTesting.project.createProject')"
      width="600px"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item :label="$t('apiTesting.project.projectName')" prop="name">
          <el-input v-model="form.name" :placeholder="$t('apiTesting.project.inputProjectName')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.projectDescription')" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            :placeholder="$t('apiTesting.project.inputProjectDesc')"
          />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.projectType')" prop="project_type">
          <el-radio-group v-model="form.project_type">
            <el-radio value="HTTP">HTTP</el-radio>
            <el-radio value="WEBSOCKET">WebSocket</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.projectStatus')" prop="status">
          <el-select v-model="form.status" :placeholder="$t('apiTesting.project.selectStatus')">
            <el-option :label="$t('apiTesting.project.status.notStarted')" value="NOT_STARTED" />
            <el-option :label="$t('apiTesting.project.status.inProgress')" value="IN_PROGRESS" />
            <el-option :label="$t('apiTesting.project.status.completed')" value="COMPLETED" />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.owner')" prop="owner">
          <el-select v-model="form.owner" :placeholder="$t('apiTesting.project.selectOwner')" filterable>
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.teamMembers')" prop="member_ids">
          <el-select
            v-model="form.member_ids"
            multiple
            :placeholder="$t('apiTesting.project.selectMembers')"
            filterable
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.startDate')" prop="start_date">
          <el-date-picker
            v-model="form.start_date"
            type="date"
            :placeholder="$t('apiTesting.project.selectStartDate')"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.project.endDate')" prop="end_date">
          <el-date-picker
            v-model="form.end_date"
            type="date"
            :placeholder="$t('apiTesting.project.selectEndDate')"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          {{ editingProject ? $t('apiTesting.common.update') : $t('apiTesting.common.create') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showViewDialog"
      :title="$t('apiTesting.project.viewProject')"
      width="600px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item :label="$t('apiTesting.project.projectName')">{{ viewedProject?.name }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.projectDescription')">{{ viewedProject?.description || $t('apiTesting.project.none') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.projectType')">
          <el-tag :type="viewedProject?.project_type === 'HTTP' ? 'primary' : 'success'">
            {{ viewedProject?.project_type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.projectStatus')">
          <el-tag :type="getStatusType(viewedProject?.status)">
            {{ getStatusText(viewedProject?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.owner')">{{ viewedProject?.owner?.username }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.teamMembers')">
          <div v-if="viewedProject?.members?.length">
            <el-tag
              v-for="member in viewedProject.members"
              :key="member.id"
              size="small"
              class="member-tag"
            >
              {{ member.username }}
            </el-tag>
          </div>
          <span v-else>{{ $t('apiTesting.project.none') }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.startDate')">{{ viewedProject?.start_date || $t('apiTesting.project.notSet') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.endDate')">{{ viewedProject?.end_date || $t('apiTesting.project.notSet') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.createdAt')">{{ formatDate(viewedProject?.created_at) }}</el-descriptions-item>
        <el-descriptions-item :label="$t('apiTesting.project.updatedAt')">{{ formatDate(viewedProject?.updated_at) }}</el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="showViewDialog = false">{{ $t('apiTesting.common.close') }}</el-button>
        <el-button type="primary" @click="editProject(viewedProject)">{{ $t('apiTesting.common.edit') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Plus, Search } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import api from '@/utils/api'
import { getApiProjects, getUsers } from '@/api/api-testing'
import { UnifiedListTable } from '@/components/platform-shared'
import { ListShell } from '@/components/page-shells'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

const router = useRouter()
const { t } = useI18n()

const loading = ref(false)
const projects = ref([])
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const statusFilter = ref('')
const projectTypeFilter = ref('')
const hasLoaded = ref(false)
const requestState = ref(`${UI_PAGE_STATE.READY}`)
const requestErrorMessage = ref('')

const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const editingProject = ref(null)
const viewedProject = ref(null)
const submitting = ref(false)
const formRef = ref()

const form = reactive({
  name: '',
  description: '',
  project_type: 'HTTP',
  status: 'NOT_STARTED',
  owner: null,
  member_ids: [],
  start_date: '',
  end_date: ''
})

const hasActiveFilter = computed(() => {
  return Boolean(searchText.value.trim() || statusFilter.value || projectTypeFilter.value)
})

const pageState = computed(() => {
  let state = String(UI_PAGE_STATE.READY)
  if (loading.value && !hasLoaded.value) {
    state = UI_PAGE_STATE.LOADING
  } else if (requestState.value === UI_PAGE_STATE.FORBIDDEN) {
    state = UI_PAGE_STATE.FORBIDDEN
  } else if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    state = UI_PAGE_STATE.REQUEST_ERROR
  } else if (projects.value.length === 0) {
    state = hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return state
})

const rules = computed(() => ({
  name: [
    { required: true, message: t('apiTesting.project.inputProjectName'), trigger: 'blur' }
  ],
  project_type: [
    { required: true, message: t('apiTesting.common.pleaseSelect'), trigger: 'change' }
  ],
  status: [
    { required: true, message: t('apiTesting.project.selectStatus'), trigger: 'change' }
  ],
  owner: [
    { required: true, message: t('apiTesting.project.selectOwner'), trigger: 'change' }
  ]
}))

const getStatusType = (status) => {
  const typeMap = {
    NOT_STARTED: 'info',
    IN_PROGRESS: 'warning',
    COMPLETED: 'success'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusKey = {
    NOT_STARTED: 'notStarted',
    IN_PROGRESS: 'inProgress',
    COMPLETED: 'completed'
  }[status]
  return statusKey ? t(`apiTesting.project.status.${statusKey}`) : status
}

const formatDate = (dateString) => {
  return dateString ? dayjs(dateString).format('YYYY-MM-DD HH:mm') : '-'
}

const resolveRequestState = (error) => {
  if (error?.response?.status === 403) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  return UI_PAGE_STATE.REQUEST_ERROR
}

const loadProjects = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchText.value.trim()) {
      params.search = searchText.value.trim()
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    if (projectTypeFilter.value) {
      params.project_type = projectTypeFilter.value
    }

    const response = await getApiProjects(params)
    projects.value = response.data.results || []
    total.value = response.data.count || 0
    requestState.value = UI_PAGE_STATE.READY
    requestErrorMessage.value = ''
    hasLoaded.value = true

    const maxPage = Math.max(1, Math.ceil((total.value || 0) / pageSize.value))
    if (total.value > 0 && currentPage.value > maxPage) {
      currentPage.value = maxPage
      await loadProjects()
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadProjects'))
    console.error(error)
    projects.value = []
    total.value = 0
    hasLoaded.value = true
    requestState.value = resolveRequestState(error)
    requestErrorMessage.value = error?.response?.data?.detail || t('apiTesting.messages.error.loadProjects')
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const response = await getUsers()
    users.value = response.data.results || response.data || []
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.loadUsers'))
    console.error(error)
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadProjects()
}

const resetFilters = () => {
  searchText.value = ''
  statusFilter.value = ''
  projectTypeFilter.value = ''
  currentPage.value = 1
  loadProjects()
}

const editProject = (project) => {
  editingProject.value = project
  form.name = project.name
  form.description = project.description
  form.project_type = project.project_type
  form.status = project.status
  form.owner = project.owner?.id || null
  form.member_ids = (project.members || []).map((member) => member.id)
  form.start_date = project.start_date
  form.end_date = project.end_date
  showCreateDialog.value = true
}

const viewProject = (project) => {
  viewedProject.value = project
  showViewDialog.value = true
}

const deleteProject = async (project) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.project.confirmDelete', { name: project.name }),
      t('apiTesting.messages.confirm.deleteTitle'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )

    await api.delete(`/api-testing/projects/${project.id}/`)
    ElMessage.success(t('apiTesting.messages.success.delete'))
    await loadProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
      console.error(error)
    }
  }
}

const submitForm = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = { ...form }
    if (data.start_date) {
      data.start_date = dayjs(data.start_date).format('YYYY-MM-DD')
    }
    if (data.end_date) {
      data.end_date = dayjs(data.end_date).format('YYYY-MM-DD')
    }

    if (editingProject.value) {
      await api.put(`/api-testing/projects/${editingProject.value.id}/`, data)
      ElMessage.success(t('apiTesting.messages.success.projectUpdated'))
    } else {
      await api.post('/api-testing/projects/', data)
      ElMessage.success(t('apiTesting.messages.success.projectCreated'))
      currentPage.value = 1
    }

    showCreateDialog.value = false
    await loadProjects()
  } catch (error) {
    ElMessage.error(editingProject.value ? t('apiTesting.messages.error.updateFailed') : t('apiTesting.messages.error.createFailed'))
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingProject.value = null
  Object.assign(form, {
    name: '',
    description: '',
    project_type: 'HTTP',
    status: 'NOT_STARTED',
    owner: null,
    member_ids: [],
    start_date: '',
    end_date: ''
  })
  formRef.value?.resetFields()
}

onMounted(async () => {
  await Promise.all([loadProjects(), loadUsers()])
})
</script>

<style scoped>
.project-management {
  min-height: 100%;
}

.project-management-shell {
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

.table-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.table-container {
  min-height: 240px;
}

.member-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}
</style>
