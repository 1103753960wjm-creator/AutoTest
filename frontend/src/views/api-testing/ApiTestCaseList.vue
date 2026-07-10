<template>
  <div class="api-test-case-list">
    <ListShell class="api-test-case-list__shell">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新建接口测试用例
        </el-button>
      </template>

      <template #filters>
        <div class="filters">
          <el-row :gutter="16" class="filters__row">
            <el-col :xs="24" :sm="12" :md="6">
              <el-input
                v-model="searchText"
                placeholder="搜索用例名称或 URL"
                clearable
                @clear="handleFilterChange"
                @keyup.enter="handleFilterChange"
                style="width: 100%"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-select
                v-model="selectedProject"
                placeholder="选择项目"
                filterable
                @change="handleProjectChange"
                style="width: 100%"
              >
                <el-option
                  v-for="project in httpProjects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-select
                v-model="methodFilter"
                placeholder="请求方法"
                clearable
                @change="handleFilterChange"
                style="width: 100%"
              >
                <el-option v-for="method in methods" :key="method" :label="method" :value="method" />
              </el-select>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-select
                v-model="collectionFilter"
                placeholder="所属集合"
                clearable
                filterable
                :disabled="collections.length === 0"
                @change="handleFilterChange"
                style="width: 100%"
              >
                <el-option
                  v-for="collection in collections"
                  :key="collection.id"
                  :label="collection.name"
                  :value="collection.id"
                />
              </el-select>
            </el-col>
          </el-row>
        </div>
      </template>

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
        :description="requestErrorMessage || '接口测试用例加载失败，请重试'"
        @primary-action="loadTestCases"
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
        primary-action-text="新建接口测试用例"
        @primary-action="openCreateDialog"
      />
      <UnifiedListTable
        v-else
        v-model:currentPage="currentPage"
        v-model:pageSize="pageSize"
        :data="testCases"
        :total="total"
        :loading="loading"
        row-key="id"
        selection-mode="none"
        :actions="{ view: false, edit: false, delete: false }"
        :action-column-width="260"
        @page-change="loadTestCases"
        @row-dblclick="openWorkspace"
      >
        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="method" label="请求方法" width="100">
          <template #default="{ row }">
            <el-tag :type="getMethodTagType(row.method)" size="small">
              {{ row.method || 'GET' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="URL" min-width="260" show-overflow-tooltip />
        <el-table-column label="所属项目" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ getProjectName(row) }}
          </template>
        </el-table-column>
        <el-table-column label="所属集合" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ getCollectionName(row.collection) }}
          </template>
        </el-table-column>
        <el-table-column label="断言数" width="90" align="center">
          <template #default="{ row }">
            {{ getAssertionCount(row) }}
          </template>
        </el-table-column>
        <el-table-column label="来源" width="110">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ getSourceLabel(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最近执行状态" width="130">
          <template #default="{ row }">
            <el-tag :type="getLatestStatusTagType(row)" size="small">
              {{ getLatestStatusText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <template #actions="{ row }">
          <el-button link type="primary" @click.stop="openWorkspace(row)">编辑/调试</el-button>
          <el-button link type="success" :loading="executingId === row.id" @click.stop="executeCase(row)">执行</el-button>
          <el-button link type="primary" :loading="movingId === row.id" @click.stop="openMoveDialog(row)">移动集合</el-button>
          <el-button link type="primary" @click.stop="openAddToSuiteDialog(row)">加入套件</el-button>
          <el-button link type="primary" @click.stop="openHistory(row)">历史</el-button>
          <el-button link type="danger" :loading="deletingId === row.id" @click.stop="deleteCase(row)">删除</el-button>
        </template>
      </UnifiedListTable>
    </ListShell>

    <el-dialog
      v-model="showCreateDialog"
      title="新建接口测试用例"
      width="640px"
      :close-on-click-modal="false"
      @close="resetCreateForm"
    >
      <el-form
        ref="formRef"
        @submit.prevent
        :model="createForm"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="所属项目" prop="project">
          <el-select v-model="createForm.project" placeholder="请选择项目" filterable @change="loadCollectionsForCreate">
            <el-option
              v-for="project in httpProjects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属集合" prop="collection">
          <el-select v-model="createForm.collection" placeholder="请选择集合" filterable>
            <el-option
              v-for="collection in createCollections"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="请求方法" prop="method">
          <el-select v-model="createForm.method" placeholder="请选择请求方法">
            <el-option v-for="method in methods" :key="method" :label="method" :value="method" />
          </el-select>
        </el-form-item>
        <el-form-item label="请求 URL" prop="url">
          <el-input v-model="createForm.url" placeholder="请输入 http:// 或 https:// 开头的 URL" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitCreateForm">创建并进入调试</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showAddToSuiteDialog"
      title="加入测试套件"
      width="520px"
      :close-on-click-modal="false"
      @close="resetAddToSuiteForm"
    >
      <el-form @submit.prevent label-width="120px">
        <el-form-item label="接口测试用例">
          <el-input :model-value="suiteTargetCase?.name || '-'" readonly />
        </el-form-item>
        <el-form-item label="目标测试套件">
          <el-select
            v-model="selectedSuiteId"
            placeholder="请选择测试套件"
            filterable
            :loading="loadingSuites"
            :disabled="loadingSuites || availableSuites.length === 0"
            style="width: 100%"
          >
            <el-option
              v-for="suite in availableSuites"
              :key="suite.id"
              :label="suite.name"
              :value="suite.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddToSuiteDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="addingToSuite"
          :disabled="loadingSuites || availableSuites.length === 0"
          @click="submitAddToSuite"
        >
          确认加入
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showMoveDialog"
      title="移动集合"
      width="520px"
      :close-on-click-modal="false"
      @close="resetMoveForm"
    >
      <el-form @submit.prevent label-width="120px">
        <el-form-item label="接口测试用例">
          <el-input :model-value="moveTargetCase?.name || '-'" readonly />
        </el-form-item>
        <el-form-item label="当前集合">
          <el-input :model-value="getCollectionName(moveTargetCase?.collection)" readonly />
        </el-form-item>
        <el-form-item label="目标集合" required>
          <el-select
            v-model="targetCollectionId"
            placeholder="请选择目标集合"
            filterable
            :loading="loadingMoveCollections"
            :disabled="loadingMoveCollections || moveCollections.length === 0"
            style="width: 100%"
          >
            <el-option
              v-for="collection in moveCollections"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
              :disabled="collection.id === moveTargetCase?.collection"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showMoveDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="movingId === moveTargetCase?.id"
          :disabled="loadingMoveCollections || moveCollections.length === 0"
          @click="submitMoveCollection"
        >
          确认移动
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import {
  addApiRequestsToTestSuite,
  createApiTestCase,
  deleteApiTestCase,
  executeApiTestCase,
  getApiCollections,
  getApiProjects,
  getApiTestCases,
  getTestSuites,
  moveApiTestCaseCollection
} from '@/api/api-testing'
import { UnifiedListTable } from '@/components/platform-shared'
import { ListShell } from '@/components/page-shells'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

defineOptions({
  name: 'ApiTestCaseList'
})

const router = useRouter()

const methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

const loading = ref(false)
const hasLoaded = ref(false)
const requestState = ref(`${UI_PAGE_STATE.READY}`)
const requestErrorMessage = ref('')
const projects = ref([])
const collections = ref([])
const testCases = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const selectedProject = ref(null)
const methodFilter = ref('')
const collectionFilter = ref(null)
const showCreateDialog = ref(false)
const createCollections = ref([])
const submitting = ref(false)
const executingId = ref(null)
const deletingId = ref(null)
const movingId = ref(null)
const formRef = ref()
const showAddToSuiteDialog = ref(false)
const suiteTargetCase = ref(null)
const selectedSuiteId = ref(null)
const availableSuites = ref([])
const addingToSuite = ref(false)
const loadingSuites = ref(false)
const showMoveDialog = ref(false)
const moveTargetCase = ref(null)
const targetCollectionId = ref(null)
const moveCollections = ref([])
const loadingMoveCollections = ref(false)
let testCaseLoadSeq = 0
let collectionLoadSeq = 0
let createCollectionLoadSeq = 0
let moveCollectionLoadSeq = 0

const createForm = reactive({
  project: null,
  collection: null,
  name: '',
  method: 'GET',
  url: '',
  description: ''
})

const rules = {
  project: [{ required: true, message: '请选择项目', trigger: 'change' }],
  collection: [{ required: true, message: '请选择集合', trigger: 'change' }],
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  method: [{ required: true, message: '请选择请求方法', trigger: 'change' }],
  url: [
    { required: true, message: '请输入请求 URL', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (!/^https?:\/\//i.test(String(value || '').trim())) {
          callback(new Error('URL 需要以 http:// 或 https:// 开头'))
          return
        }
        callback()
      },
      trigger: 'blur'
    }
  ]
}

const httpProjects = computed(() => projects.value.filter((project) => project.project_type !== 'WEBSOCKET'))

const hasActiveFilter = computed(() => Boolean(searchText.value.trim() || methodFilter.value || collectionFilter.value))

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

const loadProjects = async () => {
  const response = await getApiProjects({ page_size: 100 })
  projects.value = response.data.results || response.data || []
  if (!selectedProject.value && httpProjects.value.length) {
    selectedProject.value = httpProjects.value[0].id
  }
}

const loadCollections = async (projectId = selectedProject.value) => {
  const loadSeq = ++collectionLoadSeq
  if (!projectId) {
    if (loadSeq === collectionLoadSeq) {
      collections.value = []
    }
    return
  }
  const response = await getApiCollections({ project: projectId, page_size: 500 })
  if (loadSeq !== collectionLoadSeq || projectId !== selectedProject.value) return

  collections.value = response.data.results || response.data || []
  if (collectionFilter.value && !collections.value.some((item) => item.id === collectionFilter.value)) {
    collectionFilter.value = null
  }
}

const loadTestCases = async () => {
  const loadSeq = ++testCaseLoadSeq
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  requestErrorMessage.value = ''

  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      request_type: 'HTTP',
      ordering: '-updated_at'
    }

    if (selectedProject.value) {
      params.project = selectedProject.value
    }
    if (methodFilter.value) {
      params.method = methodFilter.value
    }
    if (collectionFilter.value) {
      params.collection = collectionFilter.value
    }
    if (searchText.value.trim()) {
      params.search = searchText.value.trim()
    }

    const response = await getApiTestCases(params)
    if (loadSeq !== testCaseLoadSeq) return

    const data = response.data.results || response.data || []
    testCases.value = data
    total.value = response.data.count ?? data.length
    hasLoaded.value = true

    const maxPage = Math.max(1, Math.ceil((total.value || 0) / pageSize.value))
    if (total.value > 0 && currentPage.value > maxPage) {
      currentPage.value = maxPage
      await loadTestCases()
    }
  } catch (error) {
    if (loadSeq !== testCaseLoadSeq) return

    testCases.value = []
    total.value = 0
    hasLoaded.value = true
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    ElMessage.error('接口测试用例加载失败')
    console.error(error)
  } finally {
    if (loadSeq === testCaseLoadSeq) {
      loading.value = false
    }
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadTestCases()
}

const handleProjectChange = async () => {
  currentPage.value = 1
  collectionFilter.value = null
  await loadCollections()
  await loadTestCases()
}

const resetFilters = async () => {
  searchText.value = ''
  methodFilter.value = ''
  collectionFilter.value = null
  selectedProject.value = httpProjects.value[0]?.id || null
  currentPage.value = 1
  await loadCollections()
  await loadTestCases()
}

const openCreateDialog = async () => {
  createForm.project = selectedProject.value || httpProjects.value[0]?.id || null
  await loadCollectionsForCreate()
  showCreateDialog.value = true
}

const loadCollectionsForCreate = async () => {
  const loadSeq = ++createCollectionLoadSeq
  if (!createForm.project) {
    if (loadSeq === createCollectionLoadSeq) {
      createCollections.value = []
      createForm.collection = null
    }
    return
  }

  const response = await getApiCollections({ project: createForm.project, page_size: 500 })
  if (loadSeq !== createCollectionLoadSeq) return

  createCollections.value = response.data.results || response.data || []
  if (createForm.collection && !createCollections.value.some((item) => item.id === createForm.collection)) {
    createForm.collection = null
  }
}

const resetCreateForm = () => {
  Object.assign(createForm, {
    project: selectedProject.value || httpProjects.value[0]?.id || null,
    collection: null,
    name: '',
    method: 'GET',
    url: '',
    description: ''
  })
  createCollections.value = []
  formRef.value?.resetFields()
}

const submitCreateForm = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const response = await createApiTestCase({
      collection: createForm.collection || null,
      name: createForm.name.trim(),
      description: createForm.description || '',
      request_type: 'HTTP',
      method: createForm.method,
      url: createForm.url.trim(),
      headers: {},
      params: {},
      body: {},
      auth: {},
      pre_request_script: '',
      post_request_script: '',
      assertions: []
    })

    const targetProjectId = createForm.project
    ElMessage.success('接口测试用例创建成功')
    showCreateDialog.value = false
    if (targetProjectId && selectedProject.value !== targetProjectId) {
      selectedProject.value = targetProjectId
      await loadCollections(targetProjectId)
    }
    await loadTestCases()
    openWorkspace(response.data, targetProjectId)
  } catch (error) {
    ElMessage.error('接口测试用例创建失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const openWorkspace = (row, projectId = getCaseProjectId(row)) => {
  router.push({
    path: '/api-testing/test-cases/workspace',
    query: {
      caseId: row.id,
      projectId
    }
  })
}

const openHistory = (row) => {
  router.push({
    path: '/api-testing/history',
    query: { requestId: row.id }
  })
}

const openAddToSuiteDialog = async (row) => {
  if (!row.collection) {
    await ElMessageBox.alert(
      '该用例未归属集合，无法加入测试套件。请先进入调试页补齐集合归属后再操作。',
      '无法加入测试套件',
      {
        confirmButtonText: '知道了',
        type: 'warning'
      }
    )
    return
  }

  suiteTargetCase.value = row
  selectedSuiteId.value = null
  showAddToSuiteDialog.value = true
  loadingSuites.value = true

  try {
    const projectId = getCaseProjectId(row)
    const response = await getTestSuites({ project: projectId, page_size: 100 })
    availableSuites.value = response.data.results || response.data || []
    if (availableSuites.value.length === 0) {
      showAddToSuiteDialog.value = false
      await ElMessageBox.alert(
        '当前项目暂无可加入的测试套件。请先在测试套件页面创建测试套件后再加入。',
        '暂无可用测试套件',
        {
          confirmButtonText: '知道了',
          type: 'info'
        }
      )
    }
  } catch (error) {
    availableSuites.value = []
    showAddToSuiteDialog.value = false
    await ElMessageBox.alert(
      error.response?.data?.error || error.response?.data?.detail || '测试套件加载失败，请稍后重试。',
      '加载失败',
      {
        confirmButtonText: '知道了',
        type: 'error'
      }
    )
    console.error(error)
  } finally {
    loadingSuites.value = false
  }
}

const resetAddToSuiteForm = () => {
  suiteTargetCase.value = null
  selectedSuiteId.value = null
  availableSuites.value = []
  loadingSuites.value = false
}

const submitAddToSuite = async () => {
  if (!suiteTargetCase.value) return
  if (availableSuites.value.length === 0) {
    await ElMessageBox.alert(
      '当前项目暂无可加入的测试套件。请先在测试套件页面创建测试套件后再加入。',
      '暂无可用测试套件',
      {
        confirmButtonText: '知道了',
        type: 'info'
      }
    )
    return
  }
  if (!selectedSuiteId.value) {
    await ElMessageBox.alert('请先选择一个测试套件。', '请选择测试套件', {
      confirmButtonText: '知道了',
      type: 'warning'
    })
    return
  }

  addingToSuite.value = true
  try {
    await addApiRequestsToTestSuite(selectedSuiteId.value, [suiteTargetCase.value.id])
    showAddToSuiteDialog.value = false
    addingToSuite.value = false
    await ElMessageBox.alert('已加入测试套件。', '加入成功', {
      confirmButtonText: '知道了',
      type: 'success'
    })
  } catch (error) {
    addingToSuite.value = false
    await ElMessageBox.alert(
      error.response?.data?.error || error.response?.data?.detail || '加入测试套件失败，请稍后重试。',
      '加入失败',
      {
        confirmButtonText: '知道了',
        type: 'error'
      }
    )
    console.error(error)
  } finally {
    addingToSuite.value = false
  }
}

const openMoveDialog = async (row) => {
  if (!row.collection) {
    await ElMessageBox.alert(
      '该用例当前没有集合归属，请先进入调试页选择集合并保存。',
      '无法移动集合',
      {
        confirmButtonText: '知道了',
        type: 'warning'
      }
    )
    return
  }

  moveTargetCase.value = row
  targetCollectionId.value = row.collection
  showMoveDialog.value = true
  loadingMoveCollections.value = true
  const loadSeq = ++moveCollectionLoadSeq

  try {
    const projectId = getCaseProjectId(row)
    const response = await getApiCollections({ project: projectId, page_size: 500 })
    if (loadSeq !== moveCollectionLoadSeq) return
    moveCollections.value = response.data.results || response.data || []
  } catch (error) {
    if (loadSeq !== moveCollectionLoadSeq) return
    moveCollections.value = []
    showMoveDialog.value = false
    await ElMessageBox.alert(
      error.response?.data?.error || error.response?.data?.detail || '集合加载失败，请稍后重试。',
      '加载失败',
      {
        confirmButtonText: '知道了',
        type: 'error'
      }
    )
    console.error(error)
  } finally {
    if (loadSeq === moveCollectionLoadSeq) {
      loadingMoveCollections.value = false
    }
  }
}

const resetMoveForm = () => {
  moveTargetCase.value = null
  targetCollectionId.value = null
  moveCollections.value = []
  loadingMoveCollections.value = false
}

const submitMoveCollection = async () => {
  if (!moveTargetCase.value) return
  if (!targetCollectionId.value) {
    await ElMessageBox.alert('请先选择目标集合。', '请选择目标集合', {
      confirmButtonText: '知道了',
      type: 'warning'
    })
    return
  }
  if (targetCollectionId.value === moveTargetCase.value.collection) {
    await ElMessageBox.alert('目标集合和当前集合相同，无需移动。', '无需移动', {
      confirmButtonText: '知道了',
      type: 'info'
    })
    return
  }

  const currentCaseId = moveTargetCase.value.id
  movingId.value = currentCaseId
  try {
    await moveApiTestCaseCollection(currentCaseId, targetCollectionId.value)
    ElMessage.success('接口测试用例已移动')
    showMoveDialog.value = false
    await loadCollections()
    await loadTestCases()
  } catch (error) {
    await ElMessageBox.alert(
      error.response?.data?.error || error.response?.data?.detail || '移动集合失败，请稍后重试。',
      '移动失败',
      {
        confirmButtonText: '知道了',
        type: 'error'
      }
    )
    console.error(error)
  } finally {
    if (movingId.value === currentCaseId) {
      movingId.value = null
    }
  }
}

const executeCase = async (row) => {
  executingId.value = row.id
  try {
    await executeApiTestCase(row.id, {})
    ElMessage.success('接口测试用例执行完成')
    await loadTestCases()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '接口测试用例执行失败')
    console.error(error)
  } finally {
    executingId.value = null
  }
}

const deleteCase = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认删除接口测试用例「${row.name}」？如果该用例已加入测试套件，删除会影响套件执行，此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    deletingId.value = row.id
    await deleteApiTestCase(row.id)
    ElMessage.success('接口测试用例已删除')
    await loadTestCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('接口测试用例删除失败')
      console.error(error)
    }
  } finally {
    deletingId.value = null
  }
}

const getCollectionName = (collectionId) => {
  if (!collectionId) return '未分组'
  return collections.value.find((item) => item.id === collectionId)?.name || `集合 #${collectionId}`
}

const getCaseProjectId = (row) => {
  if (row?.project_id) return row.project_id
  if (!row?.collection) return selectedProject.value
  return collections.value.find((item) => item.id === row.collection)?.project || selectedProject.value
}

const getProjectName = (row) => {
  if (row?.project_name) return row.project_name
  const projectId = getCaseProjectId(row)
  return httpProjects.value.find((project) => project.id === projectId)?.name || (projectId ? `项目 #${projectId}` : '未归属项目')
}

const getSourceLabel = (row) => {
  if (row?.source_label) return row.source_label
  const sourceType = row?.source_metadata?.source_type || row?.source_type
  const sourceMap = {
    manual: '手工创建',
    ai: 'AI 生成',
    import: '导入'
  }
  return sourceMap[sourceType] || '来源未记录'
}

const getLatestStatusText = (row) => {
  return row?.latest_execution_status || '未执行'
}

const getLatestStatusTagType = (row) => {
  const statusText = getLatestStatusText(row)
  const typeMap = {
    通过: 'success',
    失败: 'danger',
    未执行: 'info',
    未知: 'warning'
  }
  return typeMap[statusText] || 'info'
}

const getAssertionCount = (row) => {
  if (Number.isFinite(Number(row?.assertions_count))) return Number(row.assertions_count)
  return Array.isArray(row.assertions) ? row.assertions.length : 0
}

const getMethodTagType = (method) => {
  const typeMap = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info',
    HEAD: 'info',
    OPTIONS: 'info'
  }
  return typeMap[method] || 'info'
}

const formatDate = (value) => {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '-'
}

onMounted(async () => {
  try {
    await loadProjects()
    await loadCollections()
    await loadTestCases()
  } catch (error) {
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
    ElMessage.error('接口测试用例初始化失败')
    console.error(error)
  }
})
</script>

<style scoped>
.api-test-case-list {
  min-height: 100%;
}

.api-test-case-list__shell {
  min-height: 100%;
}

.filters {
  width: 100%;
}

.filters__row {
  row-gap: 12px;
}
</style>
