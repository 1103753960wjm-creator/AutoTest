<template>
  <div class="list-page">
    <div class="list-page__panel">
      <FilterBar>
        <div class="project-filter-grid">
          <el-input
            v-model="searchText"
            :placeholder="$t('uiAutomation.project.searchPlaceholder')"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="statusFilter"
            :placeholder="$t('uiAutomation.project.statusFilter')"
            clearable
            @change="handleFilter"
          >
            <el-option :label="$t('uiAutomation.status.notStarted')" value="NOT_STARTED" />
            <el-option :label="$t('uiAutomation.status.inProgress')" value="IN_PROGRESS" />
            <el-option :label="$t('uiAutomation.status.completed')" value="COMPLETED" />
          </el-select>
        </div>
        <template #actions>
          <el-button @click="resetFilters">{{ $t('common.reset') }}</el-button>
        </template>
      </FilterBar>

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
      <StateEmpty
        v-else-if="pageState === UI_PAGE_STATE.EMPTY"
        compact
        :primary-action-text="$t('uiAutomation.project.newProject')"
        @primary-action="openCreateDialog"
      />
      <template v-else>
        <div class="list-page__toolbar">
          <div class="list-page__summary">
            <span class="list-page__summary-main">共 {{ total }} 个项目</span>
            <span class="list-page__summary-sub">
              {{ hasActiveFilter ? '当前为筛选结果' : '当前为全部项目' }}
            </span>
          </div>
        </div>

        <el-table :data="projects" v-loading="loading" style="width: 100%">
          <el-table-column prop="name" :label="$t('uiAutomation.project.projectName')" min-width="200">
            <template #default="{ row }">
              <el-link type="primary" @click="goToProjectDetail(row.id)">
                {{ row.name }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="$t('uiAutomation.common.description')" min-width="300" show-overflow-tooltip />
          <el-table-column prop="status" :label="$t('uiAutomation.common.status')" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="base_url" :label="$t('uiAutomation.project.baseUrl')" min-width="200" show-overflow-tooltip />
          <el-table-column prop="owner.username" :label="$t('uiAutomation.project.owner')" width="100" />
          <el-table-column prop="created_at" :label="$t('uiAutomation.common.createTime')" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" :label="$t('uiAutomation.common.updateTime')" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('uiAutomation.common.operation')" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="goToProjectDetail(row.id)">
                <el-icon><View /></el-icon>
                {{ $t('uiAutomation.common.view') }}
              </el-button>
              <el-button size="small" @click="openEditDialog(row)">
                <el-icon><Edit /></el-icon>
                {{ $t('uiAutomation.common.edit') }}
              </el-button>
              <el-button size="small" type="danger" @click="deleteProject(row.id)">
                <el-icon><Delete /></el-icon>
                {{ $t('uiAutomation.common.delete') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="list-page__pagination">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </template>
    </div>

    <el-dialog
      v-model="showCreateDialog"
      :title="$t('uiAutomation.project.createProject')"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="createFormRef" :model="createForm" :rules="formRules" label-width="80px">
        <el-form-item :label="$t('uiAutomation.project.projectName')" prop="name">
          <el-input v-model="createForm.name" :placeholder="$t('uiAutomation.project.rules.nameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.projectDesc')" prop="description">
          <el-input v-model="createForm.description" type="textarea" :placeholder="$t('uiAutomation.project.projectDesc')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.status')" prop="status">
          <el-select v-model="createForm.status" :placeholder="$t('uiAutomation.project.rules.selectStatus')">
            <el-option :label="$t('uiAutomation.status.notStarted')" value="NOT_STARTED" />
            <el-option :label="$t('uiAutomation.status.inProgress')" value="IN_PROGRESS" />
            <el-option :label="$t('uiAutomation.status.completed')" value="COMPLETED" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.baseUrl')" prop="base_url">
          <el-input v-model="createForm.base_url" :placeholder="$t('uiAutomation.project.rules.baseUrlRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.startDate')" prop="start_date">
          <el-date-picker v-model="createForm.start_date" type="date" :placeholder="$t('uiAutomation.project.selectDate')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.endDate')" prop="end_date">
          <el-date-picker v-model="createForm.end_date" type="date" :placeholder="$t('uiAutomation.project.selectDate')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="handleCreate">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showEditDialog"
      :title="$t('uiAutomation.project.editProject')"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="editFormRef" :model="editForm" :rules="formRules" label-width="80px">
        <el-form-item :label="$t('uiAutomation.project.projectName')" prop="name">
          <el-input v-model="editForm.name" :placeholder="$t('uiAutomation.project.rules.nameRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.projectDesc')" prop="description">
          <el-input v-model="editForm.description" type="textarea" :placeholder="$t('uiAutomation.project.projectDesc')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.status')" prop="status">
          <el-select v-model="editForm.status" :placeholder="$t('uiAutomation.project.rules.selectStatus')">
            <el-option :label="$t('uiAutomation.status.notStarted')" value="NOT_STARTED" />
            <el-option :label="$t('uiAutomation.status.inProgress')" value="IN_PROGRESS" />
            <el-option :label="$t('uiAutomation.status.completed')" value="COMPLETED" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.baseUrl')" prop="base_url">
          <el-input v-model="editForm.base_url" :placeholder="$t('uiAutomation.project.rules.baseUrlRequired')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.startDate')" prop="start_date">
          <el-date-picker v-model="editForm.start_date" type="date" :placeholder="$t('uiAutomation.project.selectDate')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.project.endDate')" prop="end_date">
          <el-date-picker v-model="editForm.end_date" type="date" :placeholder="$t('uiAutomation.project.selectDate')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="handleEdit">{{ $t('uiAutomation.common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" :title="$t('uiAutomation.project.projectDetail')" width="600px">
      <div v-if="currentProjectDetail" class="project-detail">
        <el-descriptions bordered column="1">
          <el-descriptions-item :label="$t('uiAutomation.project.projectName')">{{ currentProjectDetail.name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.projectDesc')" :span="2">
            {{ currentProjectDetail.description || $t('uiAutomation.project.noDescription') }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.common.status')">
            <el-tag :type="getStatusType(currentProjectDetail.status)">
              {{ getStatusText(currentProjectDetail.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.baseUrl')">{{ currentProjectDetail.base_url }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.owner')">
            {{ currentProjectDetail.owner?.username || $t('uiAutomation.project.none') }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.startDate')">
            {{ currentProjectDetail.start_date ? formatDateTime(currentProjectDetail.start_date) : $t('uiAutomation.project.notSet') }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.project.endDate')">
            {{ currentProjectDetail.end_date ? formatDateTime(currentProjectDetail.end_date) : $t('uiAutomation.project.notSet') }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.common.createTime')">
            {{ formatDateTime(currentProjectDetail.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.common.updateTime')">
            {{ formatDateTime(currentProjectDetail.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else class="project-detail__loading">
        {{ $t('uiAutomation.common.loading') }}
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDetailDialog = false">{{ $t('uiAutomation.common.close') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus, Search, View } from '@element-plus/icons-vue'
import router from '@/router'
import { useUserStore } from '@/stores/user'
import { createUiProject, deleteUiProject, getUiProjects, updateUiProject } from '@/api/ui_automation'
import { FilterBar } from '@/components/platform-shared'
import {
  StateEmpty,
  StateError,
  StateForbidden,
  StateLoading,
  StateSearchEmpty,
  UI_PAGE_STATE
} from '@/components/ui-states'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'

const { t } = useI18n()

const projects = ref([])
const loading = ref(false)
const total = ref(0)
const searchText = ref('')
const statusFilter = ref('')
const hasLoaded = ref(false)
const requestState = ref(`${UI_PAGE_STATE.READY}`)
const requestErrorMessage = ref('')
const lastLoadedAt = ref('')

const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDetailDialog = ref(false)
const createFormRef = ref(null)
const editFormRef = ref(null)
const currentEditId = ref(null)
const currentProjectDetail = ref(null)

const createForm = reactive({
  name: '',
  description: '',
  status: 'IN_PROGRESS',
  base_url: '',
  start_date: null,
  end_date: null
})

const editForm = reactive({
  name: '',
  description: '',
  status: 'IN_PROGRESS',
  base_url: '',
  start_date: null,
  end_date: null
})

const formRules = computed(() => ({
  name: [
    { required: true, message: t('uiAutomation.project.rules.nameRequired'), trigger: 'blur' },
    { min: 2, max: 200, message: t('uiAutomation.project.rules.nameLength'), trigger: 'blur' }
  ],
  base_url: [
    { required: true, message: t('uiAutomation.project.rules.baseUrlRequired'), trigger: 'blur' },
    { type: 'url', message: t('uiAutomation.project.rules.baseUrlInvalid'), trigger: 'blur' }
  ]
}))

const hasActiveFilter = computed(() => Boolean(searchText.value.trim() || statusFilter.value))

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

  if (hasLoaded.value && !projects.value.length && hasActiveFilter.value) {
    return UI_PAGE_STATE.SEARCH_EMPTY
  }

  if (hasLoaded.value && !projects.value.length) {
    return UI_PAGE_STATE.EMPTY
  }

  return UI_PAGE_STATE.READY
})

usePlatformPageHeader(() => ({
  statusTags: hasActiveFilter.value
    ? [
        {
          label: '筛选已生效',
          type: 'primary'
        }
      ]
    : [],
  updateText: lastLoadedAt.value ? `最近刷新 ${formatDateTime(lastLoadedAt.value)}` : '',
  helperText: '列表页只统一头部、筛选区、状态态和分页结构；项目弹窗逻辑继续保留在页面主体。',
  metaItems: [
    { label: '项目总数', value: `${total.value}` },
    { label: '当前筛选', value: hasActiveFilter.value ? '名称 / 状态筛选中' : '未筛选' }
  ],
  actions: [
    {
      key: 'create-project',
      label: t('uiAutomation.project.newProject'),
      type: 'primary',
      icon: Plus,
      onClick: openCreateDialog
    }
  ]
}))

const loadProjects = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  requestErrorMessage.value = ''

  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }

    if (searchText.value) {
      params.search = searchText.value
    }

    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const response = await getUiProjects(params)
    projects.value = response.data.results || response.data || []
    total.value = response.data.count || projects.value.length
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
  } catch (error) {
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
    ElMessage.error(t('uiAutomation.project.messages.loadFailed'))
    console.error('获取 Web 自动化项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadProjects()
}

const handleFilter = () => {
  pagination.currentPage = 1
  loadProjects()
}

const resetFilters = () => {
  searchText.value = ''
  statusFilter.value = ''
  pagination.currentPage = 1
  loadProjects()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadProjects()
}

const handleCurrentChange = (current) => {
  pagination.currentPage = current
  loadProjects()
}

const formatDateTime = (value) => {
  if (!value) {
    return ''
  }

  return new Date(value).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getStatusType = (status) => {
  const statusMap = {
    NOT_STARTED: 'warning',
    IN_PROGRESS: 'primary',
    COMPLETED: 'success'
  }

  return statusMap[status] || 'default'
}

const getStatusText = (status) => {
  const statusKey = {
    NOT_STARTED: 'notStarted',
    IN_PROGRESS: 'inProgress',
    COMPLETED: 'completed'
  }[status]

  return statusKey ? t(`uiAutomation.status.${statusKey}`) : status
}

const goToProjectDetail = (id) => {
  const project = projects.value.find((item) => item.id === id)

  if (!project) {
    ElMessage.error(t('uiAutomation.project.messages.notFound'))
    return
  }

  currentProjectDetail.value = project
  showDetailDialog.value = true
}

const resetCreateForm = () => {
  Object.assign(createForm, {
    name: '',
    description: '',
    status: 'IN_PROGRESS',
    base_url: '',
    start_date: null,
    end_date: null
  })
  createFormRef.value?.clearValidate()
}

const resetEditForm = () => {
  Object.assign(editForm, {
    name: '',
    description: '',
    status: 'IN_PROGRESS',
    base_url: '',
    start_date: null,
    end_date: null
  })
  currentEditId.value = null
  editFormRef.value?.clearValidate()
}

function openCreateDialog() {
  resetCreateForm()
  showCreateDialog.value = true
}

const openEditDialog = (project) => {
  currentEditId.value = project.id
  Object.assign(editForm, {
    name: project.name,
    description: project.description || '',
    status: project.status,
    base_url: project.base_url,
    start_date: project.start_date ? new Date(project.start_date) : null,
    end_date: project.end_date ? new Date(project.end_date) : null
  })
  showEditDialog.value = true
}

const formatDateToISO = (date) => {
  if (!date) {
    return null
  }

  return new Date(date).toISOString().split('T')[0]
}

const handleCreate = async () => {
  const isValid = await createFormRef.value.validate().catch(() => false)

  if (!isValid) {
    return
  }

  try {
    const userStore = useUserStore()

    if (!userStore.user?.id) {
      await userStore.fetchProfile()
    }

    await createUiProject({
      ...createForm,
      owner: userStore.user.id,
      start_date: formatDateToISO(createForm.start_date),
      end_date: formatDateToISO(createForm.end_date)
    })

    ElMessage.success(t('uiAutomation.project.messages.createSuccess'))
    showCreateDialog.value = false
    resetCreateForm()
    loadProjects()
  } catch (error) {
    ElMessage.error(t('uiAutomation.project.messages.createFailed'))
    console.error('创建 Web 自动化项目失败:', error)
  }
}

const handleEdit = async () => {
  const isValid = await editFormRef.value.validate().catch(() => false)

  if (!isValid) {
    return
  }

  try {
    await updateUiProject(currentEditId.value, {
      ...editForm,
      start_date: formatDateToISO(editForm.start_date),
      end_date: formatDateToISO(editForm.end_date)
    })

    ElMessage.success(t('uiAutomation.project.messages.updateSuccess'))
    showEditDialog.value = false
    resetEditForm()
    loadProjects()
  } catch (error) {
    ElMessage.error(t('uiAutomation.project.messages.updateFailed'))
    console.error('更新 Web 自动化项目失败:', error)
  }
}

const deleteProject = async (id) => {
  try {
    await ElMessageBox.confirm(t('uiAutomation.project.messages.deleteConfirm'), t('uiAutomation.messages.confirm.delete'), {
      confirmButtonText: t('uiAutomation.common.confirm'),
      cancelButtonText: t('uiAutomation.common.cancel'),
      type: 'warning'
    })

    await deleteUiProject(id)
    ElMessage.success(t('uiAutomation.project.messages.deleteSuccess'))
    loadProjects()
  } catch (error) {
    if (error === 'cancel') {
      return
    }

    ElMessage.error(t('uiAutomation.project.messages.deleteFailed'))
    console.error('删除 Web 自动化项目失败:', error)
  }
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.list-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.list-page__panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.list-page__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.list-page__summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  align-items: center;
}

.list-page__summary-main {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.list-page__summary-sub {
  font-size: 13px;
  color: #64748b;
}

.project-filter-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1.4fr) minmax(180px, 220px);
  gap: 16px;
}

.list-page__pagination {
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.project-detail__loading {
  color: #64748b;
  text-align: center;
}

@media (max-width: 1024px) {
  .project-filter-grid {
    grid-template-columns: 1fr;
  }

  .list-page__toolbar {
    align-items: flex-start;
  }

  .list-page__pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .list-page__panel {
    gap: 14px;
  }

  .list-page__summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .list-page__pagination :deep(.el-pagination__sizes),
  .list-page__pagination :deep(.el-pagination__jump) {
    display: none;
  }

  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
}

@media (max-width: 480px) {
  :deep(.el-dialog) {
    width: 98% !important;
  }
}
</style>
