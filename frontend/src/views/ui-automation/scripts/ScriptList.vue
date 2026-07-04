<template>
  <ListShell>
    <!-- 1. 搜索筛选区 -->
    <div class="filters">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-select
            v-model="filters.project"
            style="width: 100%"
            :placeholder="$t('uiAutomation.common.selectProject')"
            clearable
            @change="handleFilter"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input
            v-model="filters.name"
            style="width: 100%"
            :placeholder="$t('uiAutomation.script.newNamePlaceholder')"
            clearable
            @input="handleFilter"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 2. 统一页面状态机联动 -->
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
      @primary-action="loadScripts"
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
      :primary-action-text="$t('uiAutomation.script.newScript')"
      @primary-action="goToScriptEditor"
    />

    <!-- 3. 标准表格与分页展示 -->
    <template v-else>
      <div class="table-container">
        <UnifiedListTable
          v-model:currentPage="pagination.page"
          v-model:pageSize="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          :data="scripts"
          :loading="loading"
          row-key="id"
          selection-mode="multi"
          :actions="{ view: false, edit: false, delete: false }"
          :action-column-width="280"
          @page-change="loadScripts"
          @selection-change="handleSelectionChange"
        >
          <el-table-column :label="$t('uiAutomation.script.projectColumn')" width="150" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.project?.name || $t('uiAutomation.script.unknownProject') }}
            </template>
          </el-table-column>
          <el-table-column prop="name" :label="$t('uiAutomation.script.nameColumn')" min-width="300" show-overflow-tooltip />
          <el-table-column :label="$t('uiAutomation.script.languageColumn')" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="row.language === 'python' ? 'success' : 'primary'">
                {{ getLanguageText(row.language) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="$t('uiAutomation.script.frameworkColumn')" width="120">
            <template #default="{ row }">
              <el-tag size="small" :type="row.framework === 'playwright' ? 'warning' : 'info'">
                {{ getFrameworkText(row.framework) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" :label="$t('uiAutomation.script.createTimeColumn')" width="180">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <template #actions="{ row }">
            <div class="table-actions">
              <el-button link type="primary" @click="viewScript(row)">
                {{ $t('uiAutomation.script.viewDetail') }}
              </el-button>
              <el-button link type="warning" @click="editScript(row)">
                {{ $t('uiAutomation.script.edit') }}
              </el-button>
              <el-button link type="primary" @click="renameScript(row)">
                {{ $t('uiAutomation.script.rename') }}
              </el-button>
              <el-button link type="danger" @click="deleteScript(row)">
                {{ $t('uiAutomation.script.delete') }}
              </el-button>
            </div>
          </template>
        </UnifiedListTable>
      </div>
    </template>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="showDetailDialog" :title="$t('uiAutomation.script.scriptDetail')" width="70%">
      <div v-if="currentScript" class="script-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('uiAutomation.script.scriptName')" :span="2">{{ currentScript.name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.project')">{{ currentScript.project?.name || $t('uiAutomation.script.unknownProject') }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.language')">{{ getLanguageText(currentScript.language) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.framework')">{{ getFrameworkText(currentScript.framework) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.scriptType')">{{ getScriptTypeText(currentScript.script_type) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.createTime')" :span="2">{{ formatTime(currentScript.created_at) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('uiAutomation.script.updateTime')" :span="2">{{ formatTime(currentScript.updated_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="script-content">
          <h4>{{ $t('uiAutomation.script.scriptContent') }}</h4>
          <pre class="code-view">{{ currentScript.content || $t('uiAutomation.script.noContent') }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">{{ $t('uiAutomation.script.close') }}</el-button>
        <el-button type="primary" @click="editScript(currentScript)">{{ $t('uiAutomation.script.editScript') }}</el-button>
      </template>
    </el-dialog>

    <!-- 重命名对话框 -->
    <el-dialog v-model="showRenameDialog" :title="$t('uiAutomation.script.renameScript')" width="400px">
      <el-form @submit.prevent :model="renameForm" label-width="80px">
        <el-form-item :label="$t('uiAutomation.script.newName')">
          <el-input v-model="renameForm.newName" :placeholder="$t('uiAutomation.script.newNamePlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRenameDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
        <el-button type="primary" @click="confirmRename">{{ $t('uiAutomation.common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" :title="$t('uiAutomation.script.editScript')" width="80%" :close-on-click-modal="false">
      <div v-if="editingScript" class="script-editor">
        <div class="editor-header">
          <span class="script-name">{{ editingScript.name }}</span>
          <div class="editor-info">
            <el-tag size="small" :type="editingScript.language === 'python' ? 'success' : 'primary'">
              {{ getLanguageText(editingScript.language) }}
            </el-tag>
            <el-tag size="small" :type="editingScript.framework === 'playwright' ? 'warning' : 'info'" style="margin-left: 10px">
              {{ getFrameworkText(editingScript.framework) }}
            </el-tag>
          </div>
        </div>
        <div class="editor-container">
          <textarea
            v-model="editingScript.content"
            class="code-editor"
            :placeholder="$t('uiAutomation.script.scriptEditorPlaceholder')"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="showEditDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
        <el-button type="primary" @click="saveEditedScript" :loading="saving">{{ $t('uiAutomation.script.save') }}</el-button>
      </template>
    </el-dialog>
  </ListShell>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'
import { ListShell } from '@/components/page-shells'
import { UnifiedListTable } from '@/components/platform-shared'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

import {
  getUiProjects,
  getTestScripts,
  updateTestScript,
  deleteTestScript
} from '@/api/ui_automation'

const router = useRouter()
const { t } = useI18n()

// 响应式数据
const projects = ref([])
const scripts = ref([])
const loading = ref(false)
const hasLoaded = ref(false)
const requestState = ref(`${UI_PAGE_STATE.READY}`)
const requestErrorMessage = ref('')

const filters = reactive({
  project: '',
  name: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 对话框控制
const showDetailDialog = ref(false)
const showRenameDialog = ref(false)
const showEditDialog = ref(false)

// 当前操作的脚本
const currentScript = ref(null)
const editingScript = ref(null)
const saving = ref(false)
const selectedIds = ref([])

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

// 重命名表单
const renameForm = reactive({
  scriptId: null,
  newName: ''
})

const hasActiveFilter = computed(() => Boolean(filters.name))

const pageState = computed(() => {
  let state = String(UI_PAGE_STATE.READY)
  if (loading.value && !hasLoaded.value) {
    state = UI_PAGE_STATE.LOADING
  } else if (requestState.value === UI_PAGE_STATE.FORBIDDEN) {
    state = UI_PAGE_STATE.FORBIDDEN
  } else if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    state = UI_PAGE_STATE.REQUEST_ERROR
  } else if (scripts.value.length === 0) {
    state = hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return state
})

usePlatformPageHeader(() => ({
  helperText: t('uiAutomation.script.helperText', '管理和查看 UI 自动化测试脚本，支持在线查看、编辑和重命名脚本。'),
  metaItems: [
    { label: t('uiAutomation.script.totalCount', '脚本总数'), value: `${pagination.total}` }
  ],
  actions: [
    {
      key: 'new-script-btn',
      label: t('uiAutomation.script.newScript'),
      type: 'primary',
      icon: Plus,
      onClick: goToScriptEditor
    }
  ]
}))

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await getUiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error(t('uiAutomation.script.messages.loadProjectsFailed'))
    console.error('获取项目列表失败:', error)
  }
}

// 加载脚本列表
const loadScripts = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  requestErrorMessage.value = ''
  let shouldRefetch = false

  try {
    const params = {
      project: filters.project,
      name: filters.name,
      page: pagination.page,
      page_size: pagination.size
    }
    Object.keys(params).forEach(key => params[key] === '' && delete params[key])

    const response = await getTestScripts(params)

    let results = []
    let count = 0
    if (response.data.results) {
      results = response.data.results
      count = response.data.count || 0
    } else {
      results = response.data
      count = response.data.length
    }

    scripts.value = results
    pagination.total = count

    const maxPage = Math.max(1, Math.ceil((pagination.total || 0) / pagination.size || 1))
    if (pagination.page > maxPage) {
      pagination.page = maxPage
      shouldRefetch = true
      return
    }
    hasLoaded.value = true
  } catch (error) {
    ElMessage.error(t('uiAutomation.script.messages.loadScriptsFailed'))
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
  } finally {
    if (!shouldRefetch) {
      loading.value = false
    }
  }

  if (shouldRefetch) {
    await loadScripts()
  }
}

const handleFilter = () => {
  pagination.page = 1
  loadScripts()
}

const resetFilters = () => {
  filters.name = ''
  pagination.page = 1
  loadScripts()
}

// 跳转到脚本编辑器
const goToScriptEditor = () => {
  router.push('/ui-automation/scripts/editor')
}

// 查看脚本详情
const viewScript = (script) => {
  currentScript.value = script
  showDetailDialog.value = true
}

// 编辑脚本
const editScript = (script) => {
  editingScript.value = { ...script }
  showDetailDialog.value = false
  showEditDialog.value = true
}

// 保存编辑的脚本
const saveEditedScript = async () => {
  if (!editingScript.value) return

  try {
    saving.value = true

    await updateTestScript(editingScript.value.id, {
      content: editingScript.value.content
    })

    ElMessage.success(t('uiAutomation.script.messages.saveSuccess'))
    showEditDialog.value = false

    // 重新加载脚本列表
    await loadScripts()
  } catch (error) {
    ElMessage.error(t('uiAutomation.script.messages.saveFailed'))
    console.error('脚本保存失败:', error)
  } finally {
    saving.value = false
  }
}

// 重命名脚本
const renameScript = (script) => {
  renameForm.scriptId = script.id
  renameForm.newName = script.name
  showRenameDialog.value = true
}

// 确认重命名
const confirmRename = async () => {
  if (!renameForm.newName.trim()) {
    ElMessage.warning(t('uiAutomation.script.messages.enterNewName'))
    return
  }

  try {
    await updateTestScript(renameForm.scriptId, {
      name: renameForm.newName
    })

    ElMessage.success(t('uiAutomation.script.messages.renameSuccess'))
    showRenameDialog.value = false

    // 重新加载脚本列表
    await loadScripts()
  } catch (error) {
    ElMessage.error(t('uiAutomation.script.messages.renameFailed'))
    console.error('重命名失败:', error)
  }
}

// 删除脚本
const deleteScript = async (script) => {
  try {
    await ElMessageBox.confirm(
      t('uiAutomation.script.messages.deleteConfirm', { name: script.name }),
      t('uiAutomation.script.messages.confirmDelete'),
      {
        confirmButtonText: t('uiAutomation.common.confirm'),
        cancelButtonText: t('uiAutomation.common.cancel'),
        type: 'warning'
      }
    )

    await deleteTestScript(script.id)
    ElMessage.success(t('uiAutomation.script.messages.deleteSuccess'))

    // 重新加载脚本列表
    await loadScripts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('uiAutomation.script.messages.deleteFailed'))
      console.error('删除失败:', error)
    }
  }
}

// 辅助方法
const getScriptTypeText = (type) => {
  const typeMap = {
    'CODE': t('uiAutomation.script.scriptTypes.CODE'),
    'VISUAL': t('uiAutomation.script.scriptTypes.VISUAL'),
    'KEYWORD': t('uiAutomation.script.scriptTypes.KEYWORD')
  }
  return typeMap[type] || type
}

const getLanguageText = (language) => {
  const languageMap = {
    'python': 'Python',
    'javascript': 'JavaScript'
  }
  return languageMap[language] || language || t('uiAutomation.status.unknown')
}

const getFrameworkText = (framework) => {
  const frameworkMap = {
    'playwright': 'Playwright',
    'selenium': 'Selenium'
  }
  return frameworkMap[framework] || framework || t('uiAutomation.status.unknown')
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleString()
}

// 组件挂载
onMounted(async () => {
  await loadProjects()

  if (projects.value.length > 0) {
    filters.project = projects.value[0].id
    await loadScripts()
  }
})
</script>

<style lang="scss" scoped>
.table-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;

  :deep(.unified-list-table) {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  :deep(.unified-list-table__table) {
    flex: 1;
    min-height: 0;
  }
  
  :deep(.el-table) {
    height: 100% !important;
  }
  
  :deep(.el-table__body-wrapper) {
    overflow-y: auto !important;
  }
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.script-detail {
  padding: 10px;
}

.script-content {
  margin-top: 20px;
}

.script-content h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.code-view {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  max-height: 400px;
  overflow: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.script-editor {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #fafafa;
  border-bottom: 1px solid #e6e6e6;
}

.script-name {
  font-weight: bold;
  font-size: 16px;
}

.editor-info {
  display: flex;
  align-items: center;
}

.editor-container {
  flex: 1;
  position: relative;
}

.code-editor {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 15px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  tab-size: 2;
}
</style>
