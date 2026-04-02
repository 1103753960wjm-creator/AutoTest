<template>
  <div class="environment-management">
    <ListShell class="environment-management-shell">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          {{ $t('apiTesting.environment.createEnvironment') }}
        </el-button>
      </template>

      <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane :label="$t('apiTesting.environment.scopeTypes.global')" name="GLOBAL">
        <div class="tab-toolbar">
          <el-select
            v-model="globalStatusFilter"
            clearable
            placeholder="全部状态"
            style="width: 180px"
            @change="handleGlobalFilterChange"
          >
            <el-option label="已激活" :value="true" />
            <el-option label="未激活" :value="false" />
          </el-select>
        </div>

        <div class="table-section">
          <StateLoading v-if="globalPageState === UI_PAGE_STATE.LOADING" compact />
          <StateForbidden
            v-else-if="globalPageState === UI_PAGE_STATE.FORBIDDEN"
            compact
            :primary-action-text="$t('common.uiState.actions.goHome')"
            @primary-action="router.push('/home')"
          />
          <StateError
            v-else-if="globalPageState === UI_PAGE_STATE.REQUEST_ERROR"
            compact
            :description="globalRequestErrorMessage || $t('common.uiState.error.description')"
            @primary-action="loadGlobalEnvironments"
          />
          <StateSearchEmpty
            v-else-if="globalPageState === UI_PAGE_STATE.SEARCH_EMPTY"
            compact
            :primary-action-text="$t('common.uiState.actions.clearFilters')"
            @primary-action="resetGlobalFilters"
          />
          <StateEmpty v-else-if="globalPageState === UI_PAGE_STATE.EMPTY" compact />
          <EnvironmentTable
            v-else
            v-model:currentPage="globalCurrentPage"
            v-model:pageSize="globalPageSize"
            :data="globalEnvironments"
            :loading="globalLoading"
            :total="globalTotal"
            scope="GLOBAL"
            @edit="editEnvironment"
            @delete="deleteEnvironment"
            @activate="activateEnvironment"
            @duplicate="duplicateEnvironment"
            @page-change="loadGlobalEnvironments"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('apiTesting.environment.scopeTypes.local')" name="LOCAL">
        <div class="tab-toolbar">
          <el-select
            v-model="selectedProject"
            :placeholder="$t('apiTesting.common.selectProject')"
            style="width: 220px"
            @change="handleLocalFilterChange"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
          <el-select
            v-model="localStatusFilter"
            clearable
            placeholder="全部状态"
            style="width: 180px"
            @change="handleLocalFilterChange"
          >
            <el-option label="已激活" :value="true" />
            <el-option label="未激活" :value="false" />
          </el-select>
        </div>

        <div class="table-section">
          <StateLoading v-if="localPageState === UI_PAGE_STATE.LOADING" compact />
          <StateForbidden
            v-else-if="localPageState === UI_PAGE_STATE.FORBIDDEN"
            compact
            :primary-action-text="$t('common.uiState.actions.goHome')"
            @primary-action="router.push('/home')"
          />
          <StateError
            v-else-if="localPageState === UI_PAGE_STATE.REQUEST_ERROR"
            compact
            :description="localRequestErrorMessage || $t('common.uiState.error.description')"
            @primary-action="loadLocalEnvironments"
          />
          <StateSearchEmpty
            v-else-if="localPageState === UI_PAGE_STATE.SEARCH_EMPTY"
            compact
            :primary-action-text="$t('common.uiState.actions.clearFilters')"
            @primary-action="resetLocalFilters"
          />
          <StateEmpty v-else-if="localPageState === UI_PAGE_STATE.EMPTY" compact />
          <EnvironmentTable
            v-else
            v-model:currentPage="localCurrentPage"
            v-model:pageSize="localPageSize"
            :data="localEnvironments"
            :loading="localLoading"
            :total="localTotal"
            scope="LOCAL"
            @edit="editEnvironment"
            @delete="deleteEnvironment"
            @activate="activateEnvironment"
            @duplicate="duplicateEnvironment"
            @page-change="loadLocalEnvironments"
          />
        </div>
      </el-tab-pane>
      </el-tabs>
    </ListShell>

    <el-dialog
      v-model="showCreateDialog"
      :title="editingEnvironment ? $t('apiTesting.environment.editEnvironment') : $t('apiTesting.environment.createEnvironment')"
      width="800px"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item :label="$t('apiTesting.environment.environmentName')" prop="name">
          <el-input v-model="form.name" :placeholder="$t('apiTesting.environment.inputEnvironmentName')" />
        </el-form-item>

        <el-form-item :label="$t('apiTesting.environment.scope')" prop="scope">
          <el-radio-group v-model="form.scope" @change="onScopeChange">
            <el-radio value="GLOBAL">{{ $t('apiTesting.environment.scopeTypes.global') }}</el-radio>
            <el-radio value="LOCAL">{{ $t('apiTesting.environment.scopeTypes.local') }}</el-radio>
          </el-radio-group>
          <div class="scope-help">
            <el-text size="small" type="info">
              {{ $t('apiTesting.environment.scopeHelp') }}
            </el-text>
          </div>
        </el-form-item>

        <el-form-item
          v-if="form.scope === 'LOCAL'"
          :label="$t('apiTesting.environment.relatedProject')"
          prop="project"
        >
          <el-select v-model="form.project" :placeholder="$t('apiTesting.environment.selectRelatedProject')">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('apiTesting.environment.environmentVariables')" prop="variables">
          <div class="variables-editor">
            <div class="variables-header">
              <div class="column">{{ $t('apiTesting.environment.variableName') }}</div>
              <div class="column">{{ $t('apiTesting.environment.initialValue') }}</div>
              <div class="column">{{ $t('apiTesting.environment.currentValue') }}</div>
              <div class="column">{{ $t('apiTesting.common.operation') }}</div>
            </div>

            <div class="variables-body">
              <div
                v-for="(variable, index) in form.variables"
                :key="index"
                class="variable-row"
              >
                <div class="column">
                  <el-input
                    v-model="variable.key"
                    :placeholder="$t('apiTesting.environment.variableName')"
                    size="small"
                  />
                </div>
                <div class="column">
                  <el-input
                    v-model="variable.initialValue"
                    :placeholder="$t('apiTesting.environment.initialValue')"
                    size="small"
                  />
                </div>
                <div class="column">
                  <el-input
                    v-model="variable.currentValue"
                    :placeholder="$t('apiTesting.environment.currentValue')"
                    size="small"
                  />
                </div>
                <div class="column">
                  <el-button
                    size="small"
                    type="danger"
                    :icon="Delete"
                    :disabled="form.variables.length <= 1"
                    @click="removeVariable(index)"
                  />
                </div>
              </div>
            </div>

            <div class="variables-footer">
              <el-button size="small" @click="addVariable">
                <el-icon><Plus /></el-icon>
                {{ $t('apiTesting.environment.addVariable') }}
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          {{ editingEnvironment ? $t('apiTesting.common.update') : $t('apiTesting.common.create') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Plus, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { getApiProjects, getEnvironments } from '@/api/api-testing'
import EnvironmentTable from './components/EnvironmentTable.vue'
import { ListShell } from '@/components/page-shells'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

const router = useRouter()
const { t } = useI18n()

const activeTab = ref('GLOBAL')
const globalEnvironments = ref([])
const localEnvironments = ref([])
const projects = ref([])
const selectedProject = ref(null)
const globalStatusFilter = ref('')
const localStatusFilter = ref('')

const globalCurrentPage = ref(1)
const globalPageSize = ref(20)
const globalTotal = ref(0)
const globalLoading = ref(false)
const globalHasLoaded = ref(false)
const globalRequestState = ref(UI_PAGE_STATE.READY)
const globalRequestErrorMessage = ref('')

const localCurrentPage = ref(1)
const localPageSize = ref(20)
const localTotal = ref(0)
const localLoading = ref(false)
const localHasLoaded = ref(false)
const localRequestState = ref(UI_PAGE_STATE.READY)
const localRequestErrorMessage = ref('')

const showCreateDialog = ref(false)
const editingEnvironment = ref(null)
const submitting = ref(false)
const formRef = ref()

const form = reactive({
  name: '',
  scope: 'GLOBAL',
  project: null,
  variables: [
    {
      key: '',
      initialValue: '',
      currentValue: ''
    }
  ]
})

const rules = computed(() => ({
  name: [
    { required: true, message: t('apiTesting.environment.inputEnvironmentName'), trigger: 'blur' }
  ],
  scope: [
    { required: true, message: t('apiTesting.common.pleaseSelect'), trigger: 'change' }
  ],
  project: [
    {
      validator: (rule, value, callback) => {
        if (form.scope === 'LOCAL' && !value) {
          callback(new Error(t('apiTesting.environment.selectRelatedProject')))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}))

const globalHasActiveFilter = computed(() => globalStatusFilter.value !== '')
const localHasActiveFilter = computed(() => localStatusFilter.value !== '' || Boolean(selectedProject.value))

const globalPageState = computed(() => {
  if (globalLoading.value && !globalHasLoaded.value) {
    return UI_PAGE_STATE.LOADING
  }
  if (globalRequestState.value === UI_PAGE_STATE.FORBIDDEN) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  if (globalRequestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    return UI_PAGE_STATE.REQUEST_ERROR
  }
  if (globalEnvironments.value.length === 0) {
    return globalHasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return UI_PAGE_STATE.READY
})

const localPageState = computed(() => {
  if (localLoading.value && !localHasLoaded.value) {
    return UI_PAGE_STATE.LOADING
  }
  if (localRequestState.value === UI_PAGE_STATE.FORBIDDEN) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  if (localRequestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    return UI_PAGE_STATE.REQUEST_ERROR
  }
  if (localEnvironments.value.length === 0) {
    return localHasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return UI_PAGE_STATE.READY
})

const resolveRequestState = (error) => {
  if (error?.response?.status === 403) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  return UI_PAGE_STATE.REQUEST_ERROR
}

const loadProjects = async () => {
  try {
    const response = await getApiProjects({ page_size: 100 })
    projects.value = response.data.results || response.data || []
    if (projects.value.length > 0 && !selectedProject.value) {
      selectedProject.value = projects.value[0].id
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.projectListLoadFailed'))
  }
}

const loadGlobalEnvironments = async () => {
  globalLoading.value = true
  try {
    const params = {
      scope: 'GLOBAL',
      page: globalCurrentPage.value,
      page_size: globalPageSize.value
    }
    if (globalStatusFilter.value !== '') {
      params.is_active = globalStatusFilter.value
    }
    const response = await getEnvironments(params)
    globalEnvironments.value = response.data.results || []
    globalTotal.value = response.data.count || 0
    globalRequestState.value = UI_PAGE_STATE.READY
    globalRequestErrorMessage.value = ''
    globalHasLoaded.value = true

    const maxPage = Math.max(1, Math.ceil((globalTotal.value || 0) / globalPageSize.value))
    if (globalTotal.value > 0 && globalCurrentPage.value > maxPage) {
      globalCurrentPage.value = maxPage
      await loadGlobalEnvironments()
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.globalEnvLoadFailed'))
    globalEnvironments.value = []
    globalTotal.value = 0
    globalHasLoaded.value = true
    globalRequestState.value = resolveRequestState(error)
    globalRequestErrorMessage.value = error?.response?.data?.detail || t('apiTesting.messages.error.globalEnvLoadFailed')
  } finally {
    globalLoading.value = false
  }
}

const loadLocalEnvironments = async () => {
  if (!selectedProject.value) {
    localEnvironments.value = []
    localTotal.value = 0
    localHasLoaded.value = true
    return
  }

  localLoading.value = true
  try {
    const params = {
      scope: 'LOCAL',
      project: selectedProject.value,
      page: localCurrentPage.value,
      page_size: localPageSize.value
    }
    if (localStatusFilter.value !== '') {
      params.is_active = localStatusFilter.value
    }
    const response = await getEnvironments(params)
    localEnvironments.value = response.data.results || []
    localTotal.value = response.data.count || 0
    localRequestState.value = UI_PAGE_STATE.READY
    localRequestErrorMessage.value = ''
    localHasLoaded.value = true

    const maxPage = Math.max(1, Math.ceil((localTotal.value || 0) / localPageSize.value))
    if (localTotal.value > 0 && localCurrentPage.value > maxPage) {
      localCurrentPage.value = maxPage
      await loadLocalEnvironments()
    }
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.localEnvLoadFailed'))
    localEnvironments.value = []
    localTotal.value = 0
    localHasLoaded.value = true
    localRequestState.value = resolveRequestState(error)
    localRequestErrorMessage.value = error?.response?.data?.detail || t('apiTesting.messages.error.localEnvLoadFailed')
  } finally {
    localLoading.value = false
  }
}

const onTabChange = (tab) => {
  if (tab === 'GLOBAL') {
    loadGlobalEnvironments()
  } else {
    loadLocalEnvironments()
  }
}

const handleGlobalFilterChange = () => {
  globalCurrentPage.value = 1
  loadGlobalEnvironments()
}

const handleLocalFilterChange = () => {
  localCurrentPage.value = 1
  loadLocalEnvironments()
}

const resetGlobalFilters = () => {
  globalStatusFilter.value = ''
  globalCurrentPage.value = 1
  loadGlobalEnvironments()
}

const resetLocalFilters = () => {
  localStatusFilter.value = ''
  localCurrentPage.value = 1
  loadLocalEnvironments()
}

const onScopeChange = () => {
  if (form.scope === 'GLOBAL') {
    form.project = null
  }
}

const addVariable = () => {
  form.variables.push({
    key: '',
    initialValue: '',
    currentValue: ''
  })
}

const removeVariable = (index) => {
  if (form.variables.length > 1) {
    form.variables.splice(index, 1)
  }
}

const editEnvironment = (environment) => {
  editingEnvironment.value = environment
  form.name = environment.name
  form.scope = environment.scope
  form.project = typeof environment.project === 'object' ? environment.project.id : environment.project

  const variables = environment.variables || {}
  form.variables = Object.keys(variables).map((key) => {
    const value = variables[key]
    if (typeof value === 'object') {
      return {
        key,
        initialValue: value.initialValue || '',
        currentValue: value.currentValue || ''
      }
    }
    return {
      key,
      initialValue: value || '',
      currentValue: value || ''
    }
  })

  if (form.variables.length === 0) {
    form.variables.push({
      key: '',
      initialValue: '',
      currentValue: ''
    })
  }

  showCreateDialog.value = true
}

const reloadCurrentTab = async () => {
  if (activeTab.value === 'GLOBAL') {
    await loadGlobalEnvironments()
  } else {
    await loadLocalEnvironments()
  }
}

const deleteEnvironment = async (environment) => {
  try {
    await ElMessageBox.confirm(
      t('apiTesting.environment.confirmDeleteEnv', { name: environment.name }),
      t('apiTesting.messages.confirm.deleteTitle'),
      {
        confirmButtonText: t('apiTesting.common.confirm'),
        cancelButtonText: t('apiTesting.common.cancel'),
        type: 'warning'
      }
    )

    await api.delete(`/api-testing/environments/${environment.id}/`)
    ElMessage.success(t('apiTesting.messages.success.delete'))
    await reloadCurrentTab()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('apiTesting.messages.error.deleteFailed'))
    }
  }
}

const activateEnvironment = async (environment) => {
  try {
    await api.post(`/api-testing/environments/${environment.id}/activate/`)
    ElMessage.success(t('apiTesting.messages.success.environmentActivated'))
    await reloadCurrentTab()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.activateFailed'))
  }
}

const duplicateEnvironment = async (environment) => {
  const newEnv = {
    name: `${environment.name} - Copy`,
    scope: environment.scope,
    project: environment.scope === 'LOCAL'
      ? (typeof environment.project === 'object' ? environment.project.id : environment.project)
      : null,
    variables: environment.variables || {}
  }

  try {
    await api.post('/api-testing/environments/', newEnv)
    ElMessage.success(t('apiTesting.messages.success.copy'))
    if (environment.scope === 'GLOBAL') {
      globalCurrentPage.value = 1
    } else {
      localCurrentPage.value = 1
    }
    await reloadCurrentTab()
  } catch (error) {
    ElMessage.error(t('apiTesting.messages.error.copyFailed'))
  }
}

const submitForm = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const variables = {}
    form.variables.forEach((variable) => {
      if (variable.key) {
        variables[variable.key] = {
          initialValue: variable.initialValue || '',
          currentValue: variable.currentValue || variable.initialValue || ''
        }
      }
    })

    const data = {
      name: form.name,
      scope: form.scope,
      project: form.scope === 'LOCAL' ? form.project : null,
      variables
    }

    if (editingEnvironment.value) {
      await api.put(`/api-testing/environments/${editingEnvironment.value.id}/`, data)
      ElMessage.success(t('apiTesting.messages.success.environmentUpdated'))
    } else {
      await api.post('/api-testing/environments/', data)
      ElMessage.success(t('apiTesting.messages.success.environmentCreated'))
      if (data.scope === 'GLOBAL') {
        globalCurrentPage.value = 1
      } else {
        localCurrentPage.value = 1
      }
    }

    showCreateDialog.value = false
    await reloadCurrentTab()
  } catch (error) {
    ElMessage.error(editingEnvironment.value ? t('apiTesting.messages.error.updateFailed') : t('apiTesting.messages.error.createFailed'))
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingEnvironment.value = null
  Object.assign(form, {
    name: '',
    scope: 'GLOBAL',
    project: null,
    variables: [
      {
        key: '',
        initialValue: '',
        currentValue: ''
      }
    ]
  })
  formRef.value?.resetFields()
}

onMounted(async () => {
  await loadProjects()
  await loadGlobalEnvironments()
  if (selectedProject.value) {
    await loadLocalEnvironments()
  }
})
</script>

<style scoped>
.environment-management {
  min-height: 100%;
}

.environment-management-shell {
  min-height: 100%;
}

.tab-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.table-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.scope-help {
  margin-top: 5px;
}

.variables-editor {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: white;
}

.variables-header {
  display: flex;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  padding: 8px;
  font-weight: 500;
  font-size: 12px;
  color: #606266;
}

.variables-body {
  max-height: 300px;
  overflow-y: auto;
}

.variable-row {
  display: flex;
  border-bottom: 1px solid #f5f7fa;
  padding: 8px;
  min-height: 40px;
  align-items: center;
}

.variable-row:hover {
  background: #fafbfc;
}

.column {
  flex: 1;
  padding: 0 4px;
}

.column:last-child {
  flex: 0 0 60px;
}

.variables-footer {
  padding: 8px;
  border-top: 1px solid #f5f7fa;
}
</style>
