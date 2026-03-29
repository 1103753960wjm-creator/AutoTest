<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ $t('version.title') }}</h1>
      <div class="header-actions">
        <el-button
          v-if="selectedVersions.length > 0"
          type="danger"
          :disabled="isDeleting"
          @click="batchDeleteVersions"
        >
          批量删除 ({{ selectedVersions.length }})
        </el-button>
        <el-button type="primary" @click="createVersion">
          <el-icon><Plus /></el-icon>
          {{ $t('version.newVersion') }}
        </el-button>
      </div>
    </div>

    <div class="card-container">
      <div class="filter-bar">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchText"
              :placeholder="$t('version.searchPlaceholder')"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select v-model="projectFilter" :placeholder="$t('version.relatedProject')" clearable @change="handleFilter">
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-col>
          <el-col :span="3">
            <el-select v-model="baselineFilter" :placeholder="$t('version.versionType')" clearable @change="handleFilter">
              <el-option :label="$t('version.baselineVersion')" :value="true" />
              <el-option :label="$t('version.normalVersion')" :value="false" />
            </el-select>
          </el-col>
        </el-row>
      </div>
      
      <UnifiedListTable
        v-model:currentPage="currentPage"
        v-model:pageSize="pageSize"
        :total="total"
        :data="versions"
        :loading="loading"
        row-key="id"
        selection-mode="multi"
        :actions="{
          view: false,
          edit: true,
          delete: true
        }"
        :delete-name="(row) => row?.name || ''"
        @selection-change="handleSelectionChange"
        @edit="editVersion"
        @delete="deleteVersionConfirmed"
        @row-dblclick="editVersion"
        @page-change="fetchVersions"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" :label="$t('version.versionName')" min-width="120" sortable="custom">
          <template #default="{ row }">
            <div class="version-name">
              <span>{{ row.name }}</span>
              <el-tag v-if="row.is_baseline" type="warning" size="small" class="baseline-tag">{{ $t('version.baseline') }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="projects" :label="$t('version.relatedProject')" width="300">
          <template #default="{ row }">
            <div v-if="row.projects && row.projects.length > 0" class="project-tags">
              <el-tag
                v-for="project in row.projects.slice(0, 2)"
                :key="project.id"
                size="small"
                type="primary"
                class="project-tag"
              >
                {{ project.name }}
              </el-tag>
              <el-tooltip v-if="row.projects.length > 2" :content="getProjectsTooltip(row.projects)">
                <el-tag size="small" type="info" class="project-tag">
                  +{{ row.projects.length - 2 }}
                </el-tag>
              </el-tooltip>
            </div>
            <span v-else class="no-project">{{ $t('version.noProject') }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" :label="$t('version.description')" min-width="200" show-overflow-tooltip />
        <el-table-column prop="testcases_count" :label="$t('version.testCaseCount')" width="100">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.testcases_count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by.username" :label="$t('version.creator')" width="120" />
        <el-table-column prop="created_at" :label="$t('version.createdAt')" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </UnifiedListTable>
    </div>
    
    <!-- 版本表单对话框 -->
    <el-dialog
      v-model="versionDialogVisible"
      :title="isEdit ? $t('version.editVersion') : $t('version.newVersion')"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="versionForm" :rules="versionRules" ref="versionFormRef" label-width="120px">
        <el-form-item :label="$t('version.versionName')" prop="name">
          <el-input v-model="versionForm.name" :placeholder="$t('version.versionNamePlaceholder')" />
        </el-form-item>

        <el-form-item :label="$t('version.relatedProject')" prop="project_ids">
          <el-select
            v-model="versionForm.project_ids"
            :placeholder="$t('version.selectProjects')"
            multiple
            style="width: 100%"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('version.versionDescription')">
          <el-input
            v-model="versionForm.description"
            type="textarea"
            :rows="3"
            :placeholder="$t('version.versionDescriptionPlaceholder')"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="versionForm.is_baseline">{{ $t('version.setAsBaseline') }}</el-checkbox>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="versionDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="saveVersion" :loading="saving">{{ $t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'
import { UnifiedListTable } from '@/components/platform-shared'

const { t } = useI18n()
const loading = ref(false)
const versions = ref([])
const projects = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const projectFilter = ref('')
const baselineFilter = ref('')
const sortOrdering = ref('')
const selectedVersions = ref([])
const isDeleting = ref(false)

const versionDialogVisible = ref(false)
const versionFormRef = ref()
const saving = ref(false)
const isEdit = ref(false)
const editingVersionId = ref(null)

const versionForm = reactive({
  name: '',
  description: '',
  project_ids: [],
  is_baseline: false
})

const versionRules = {
  name: [{ required: true, message: computed(() => t('version.versionNameRequired')), trigger: 'blur' }],
  project_ids: [{ required: true, message: computed(() => t('version.projectRequired')), trigger: 'change' }]
}

const fetchVersions = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchText.value,
      projects: projectFilter.value,
      is_baseline: baselineFilter.value,
      ordering: sortOrdering.value
    }
    Object.keys(params).forEach((key) => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) delete params[key]
    })
    const response = await api.get('/versions/', { params })
    versions.value = response.data.results || []
    total.value = response.data.count || 0
  } catch (error) {
    ElMessage.error(t('version.fetchListFailed'))
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/')
    projects.value = response.data.results || response.data || []
  } catch (error) {
    ElMessage.error(t('version.fetchProjectsFailed'))
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchVersions()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchVersions()
}

const handleSortChange = ({ prop, order }) => {
  if (!prop || !order) {
    sortOrdering.value = ''
  } else if (order === 'ascending') {
    sortOrdering.value = prop
  } else if (order === 'descending') {
    sortOrdering.value = `-${prop}`
  } else {
    sortOrdering.value = ''
  }
  currentPage.value = 1
  fetchVersions()
}

const createVersion = () => {
  isEdit.value = false
  resetVersionForm()
  versionDialogVisible.value = true
}

const editVersion = (version) => {
  isEdit.value = true
  editingVersionId.value = version.id
  
  versionForm.name = version.name
  versionForm.description = version.description
  versionForm.project_ids = version.projects.map(p => p.id)
  versionForm.is_baseline = version.is_baseline
  
  versionDialogVisible.value = true
}

const saveVersion = async () => {
  if (!versionFormRef.value) return

  try {
    await versionFormRef.value.validate()
    saving.value = true

    if (isEdit.value) {
      await api.put(`/versions/${editingVersionId.value}/`, versionForm)
      ElMessage.success(t('version.updateSuccess'))
    } else {
      await api.post('/versions/', versionForm)
      ElMessage.success(t('version.createSuccess'))
    }

    versionDialogVisible.value = false
    fetchVersions()

  } catch (error) {
    if (error.response?.data) {
      const errors = Object.values(error.response.data).flat()
      ElMessage.error(errors[0] || t('version.saveFailed'))
    } else {
      ElMessage.error(t('version.saveFailed'))
    }
  } finally {
    saving.value = false
  }
}

const deleteVersionConfirmed = async (version) => {
  try {
    await api.delete(`/versions/${version.id}/`)
    ElMessage.success(t('version.deleteSuccess'))
    fetchVersions()
  } catch (error) {
    ElMessage.error(t('version.deleteFailed'))
  }
}

const handleSelectionChange = (selection) => {
  selectedVersions.value = selection || []
}

const batchDeleteVersions = async () => {
  if (selectedVersions.value.length === 0) {
    ElMessage.warning('请先选择要删除的版本')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认删除已选择的 ${selectedVersions.value.length} 条记录？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    isDeleting.value = true
    const response = await api.post('/versions/batch-delete/', {
      ids: selectedVersions.value.map(v => v.id)
    })
    
    ElMessage.success(response.data.message || t('version.deleteSuccess'))
    selectedVersions.value = []
    fetchVersions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || t('version.deleteFailed'))
    }
  } finally {
    isDeleting.value = false
  }
}

const resetVersionForm = () => {
  versionForm.name = ''
  versionForm.description = ''
  versionForm.project_ids = []
  versionForm.is_baseline = false
  editingVersionId.value = null
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const getProjectsTooltip = (projects) => {
  return projects.map(p => p.name).join('、')
}

onMounted(() => {
  fetchProjects()
  fetchVersions()
})
</script>

<style lang="scss" scoped>
.filter-bar {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.version-name {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .baseline-tag {
    font-size: 12px;
  }
}

.project-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  
  .project-tag {
    margin: 0;
  }
}

.no-project {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}
</style>