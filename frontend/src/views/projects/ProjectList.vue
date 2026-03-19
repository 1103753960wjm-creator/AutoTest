<template>
  <div class="list-page">
    <div class="list-page__panel">
      <FilterBar>
        <div class="project-filter-grid">
          <el-input
            v-model="searchText"
            class="project-filter-grid__search"
            :placeholder="$t('project.searchPlaceholder')"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="statusFilter"
            class="project-filter-grid__status"
            :placeholder="$t('project.statusFilter')"
            clearable
            @change="handleFilter"
          >
            <el-option :label="$t('project.active')" value="active" />
            <el-option :label="$t('project.paused')" value="paused" />
            <el-option :label="$t('project.completed')" value="completed" />
            <el-option :label="$t('project.archived')" value="archived" />
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
        @primary-action="fetchProjects"
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
        :primary-action-text="$t('project.newProject')"
        @primary-action="handleCreateProject"
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
          <el-table-column prop="name" :label="$t('project.projectName')" min-width="200">
            <template #default="{ row }">
              <el-link @click="goToProject(row.id)" type="primary">
                {{ row.name }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="$t('project.description')" min-width="300" show-overflow-tooltip />
          <el-table-column prop="status" :label="$t('project.status')" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="设计资产" min-width="140">
            <template #default="{ row }">
              <span>{{ row.testcase_count || 0 }} 个用例</span>
            </template>
          </el-table-column>
          <el-table-column label="需求分析摘要" min-width="220" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.requirement_summary?.label || '尚未建立需求分析摘要' }}
            </template>
          </el-table-column>
          <el-table-column label="AI 生成摘要" min-width="220" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.ai_generation_summary?.label || '尚未建立 AI 生成摘要' }}
            </template>
          </el-table-column>
          <el-table-column label="自动化状态" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.automation_summary?.label || '待接自动化草稿' }}
            </template>
          </el-table-column>
          <el-table-column prop="owner.username" :label="$t('project.owner')" width="120" />
          <el-table-column prop="created_at" :label="$t('project.createdAt')" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('project.actions')" width="150" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="editProject(row)">{{ $t('common.edit') }}</el-button>
              <el-button size="small" type="danger" @click="deleteProject(row)">{{ $t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="list-page__pagination">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="handlePageChange"
          />
        </div>
      </template>
    </div>
    
    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      :title="isEdit ? $t('project.editProject') : $t('project.createProject')"
      v-model="showCreateDialog"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :modal="true"
      :destroy-on-close="false"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item :label="$t('project.projectName')" prop="name">
          <el-input v-model="form.name" :placeholder="$t('project.projectNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('project.projectDescription')" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            :placeholder="$t('project.projectDescriptionPlaceholder')"
          />
        </el-form-item>
        <el-form-item :label="$t('project.status')" prop="status">
          <el-select v-model="form.status" :placeholder="$t('project.selectStatus')">
            <el-option :label="$t('project.active')" value="active" />
            <el-option :label="$t('project.paused')" value="paused" />
            <el-option :label="$t('project.completed')" value="completed" />
            <el-option :label="$t('project.archived')" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? $t('project.update') : $t('project.create') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { FilterBar } from '@/components/platform-shared'
import api from '@/utils/api'
import dayjs from 'dayjs'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'
import { buildDeeplinkLocation } from '@/router/deeplink'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const isEdit = ref(false)
const formRef = ref()

const projects = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const statusFilter = ref('')
const hasLoaded = ref(false)
const requestState = ref(UI_PAGE_STATE.READY)
const requestErrorMessage = ref('')
const lastLoadedAt = ref('')

const form = reactive({
  id: null,
  name: '',
  description: '',
  status: 'active'
})

const rules = {
  name: [
    { required: true, message: computed(() => t('project.projectNameRequired')), trigger: 'blur' },
    { min: 2, max: 200, message: computed(() => t('project.projectNameLength')), trigger: 'blur' }
  ],
  status: [
    { required: true, message: computed(() => t('project.projectStatusRequired')), trigger: 'change' }
  ]
}

const hasActiveFilter = computed(() => Boolean(searchText.value.trim() || statusFilter.value))



usePlatformPageHeader(() => ({
  statusTags: hasActiveFilter.value
    ? [
        {
          label: '筛选已生效',
          type: 'primary'
        }
      ]
    : [],
  updateText: lastLoadedAt.value ? `最近刷新 ${formatDate(lastLoadedAt.value)}` : '',
  helperText: '筛选区、表格和分页仍然属于页面主体，不回收到 Layout 层。',
  metaItems: [
    { label: '项目总数', value: `${total.value}` },
    {
      label: '当前筛选',
      value: hasActiveFilter.value ? '名称 / 状态筛选中' : '未筛选'
    }
  ],
  actions: [
    {
      key: 'create-project',
      label: t('project.newProject'),
      type: 'primary',
      icon: Plus,
      onClick: handleCreateProject
    }
  ]
}))

const fetchProjects = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  requestErrorMessage.value = ''
  try {
    const params = {
      page: currentPage.value,
      search: searchText.value,
      status: statusFilter.value
    }
    const response = await api.get('/projects/', { params })
    projects.value = response.data.results
    total.value = response.data.count
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
  } catch (error) {
    ElMessage.error(t('project.fetchListFailed'))
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
    lastLoadedAt.value = new Date().toISOString()
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchProjects()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchProjects()
}

const resetFilters = () => {
  searchText.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  fetchProjects()
}

const handlePageChange = () => {
  fetchProjects()
}

const goToProject = (id) => {
  const nextLocation = buildDeeplinkLocation({
    target: `/ai-generation/projects/${id}`,
    currentRoute: route,
    sourceType: 'list',
    sourceTitle: '项目管理'
  })

  if (nextLocation) {
    router.push(nextLocation)
    return
  }

  router.push(`/ai-generation/projects/${id}`)
}

const handleCreateProject = () => {
  resetForm()
  showCreateDialog.value = true
}

const editProject = (project) => {
  isEdit.value = true
  form.id = project.id
  form.name = project.name
  form.description = project.description
  form.status = project.status
  showCreateDialog.value = true
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.description = ''
  form.status = 'active'
  isEdit.value = false
  // 清除表单验证错误
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.put(`/projects/${form.id}/`, form)
          ElMessage.success(t('project.updateSuccess'))
        } else {
          await api.post('/projects/', form)
          ElMessage.success(t('project.createSuccess'))
        }
        showCreateDialog.value = false
        resetForm()
        fetchProjects()
      } catch (error) {
        ElMessage.error(isEdit.value ? t('project.updateFailed') : t('project.createFailed'))
      } finally {
        submitting.value = false
      }
    }
  })
}

const deleteProject = async (project) => {
  try {
    await ElMessageBox.confirm(t('project.deleteConfirm'), t('common.warning'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning'
    })

    await api.delete(`/projects/${project.id}/`)
    ElMessage.success(t('project.deleteSuccess'))
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('project.deleteFailed'))
    }
  }
}

const getStatusType = (status) => {
  const typeMap = {
    active: 'success',
    paused: 'warning',
    completed: 'info',
    archived: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    active: t('project.active'),
    paused: t('project.paused'),
    completed: t('project.completed'),
    archived: t('project.archived')
  }
  return textMap[status] || status
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  fetchProjects()
})
</script>

<style lang="scss" scoped>
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

@media screen and (max-width: 1920px) {
  .list-page__panel {
    gap: 18px;
  }
}

@media screen and (max-width: 1024px) {
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

@media screen and (max-width: 768px) {
  .list-page__panel {
    gap: 14px;
  }

  .list-page__pagination :deep(.el-pagination) {
    :deep(.el-pagination__sizes),
    :deep(.el-pagination__jump) {
      display: none;
    }
  }

  .list-page__summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
}

@media screen and (max-width: 480px) {
  :deep(.el-table) {
    font-size: 12px;
    
    .el-button {
      padding: 5px 8px;
      font-size: 12px;
    }
  }
  
  :deep(.el-dialog) {
    width: 98% !important;
  }
}
</style>


