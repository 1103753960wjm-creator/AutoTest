<template>
  <div class="element-management">
    <el-card>
      <template #header>
        <div class="header-actions">
          <el-space wrap>
            <el-select
              v-model="projectFilter"
              placeholder="全部项目"
              clearable
              filterable
              style="width: 160px"
              @change="handleSearch"
            >
              <el-option v-for="project in projectList" :key="project.id" :label="project.name" :value="project.id" />
            </el-select>

            <el-radio-group v-model="typeFilter" @change="handleSearch">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="image">图片</el-radio-button>
              <el-radio-button value="pos">坐标</el-radio-button>
              <el-radio-button value="region">区域</el-radio-button>
            </el-radio-group>

            <el-input
              v-model="searchQuery"
              placeholder="搜索元素名称/标签"
              style="width: 250px"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
              <template #suffix>
                <el-button
                  v-if="searchQuery"
                  type="primary"
                  link
                  :icon="Search"
                  style="padding: 0"
                  @click="handleSearch"
                />
              </template>
            </el-input>
          </el-space>

          <el-space>
            <el-button type="success" @click="showCaptureDialog">
              <el-icon><Camera /></el-icon>
              从设备创建
            </el-button>
            <el-button type="primary" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              手动创建
            </el-button>
          </el-space>
        </div>
      </template>

      <div v-if="selectedElements.length > 0 && pageState === UI_PAGE_STATE.READY" class="batch-actions">
        <el-space>
          <span>已选择 {{ selectedElements.length }} 项</span>
          <el-button type="danger" size="small" @click="handleBatchDelete">
            批量删除
          </el-button>
        </el-space>
      </div>

      <div class="table-section">
        <StateLoading v-if="pageState === UI_PAGE_STATE.LOADING" compact />
        <StateForbidden
          v-else-if="pageState === UI_PAGE_STATE.FORBIDDEN"
          compact
          primary-action-text="返回首页"
          @primary-action="router.push('/home')"
        />
        <StateError
          v-else-if="pageState === UI_PAGE_STATE.REQUEST_ERROR"
          compact
          :description="requestErrorMessage || '加载元素列表失败，请稍后重试。'"
          @primary-action="loadElements"
        />
        <StateSearchEmpty
          v-else-if="pageState === UI_PAGE_STATE.SEARCH_EMPTY"
          compact
          primary-action-text="清空筛选"
          @primary-action="resetFilters"
        />
        <StateEmpty v-else-if="pageState === UI_PAGE_STATE.EMPTY" compact />
        <div v-else class="table-container">
          <UnifiedListTable
            v-model:currentPage="currentPage"
            v-model:pageSize="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            :data="elements"
            :loading="loading"
            row-key="id"
            selection-mode="multi"
            :toggle-on-row-click="false"
            :actions="{ view: false, edit: false, delete: false }"
            :action-column-width="220"
            @selection-change="handleSelectionChange"
            @page-change="loadElements"
          >
            <el-table-column prop="name" label="元素名称" min-width="200" fixed="left" show-overflow-tooltip>
              <template #default="{ row }">
                <el-link type="primary" @click="handleView(row)">
                  {{ row.name }}
                </el-link>
              </template>
            </el-table-column>

            <el-table-column prop="element_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getTypeColor(row.element_type)">
                  {{ getTypeName(row.element_type) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="图片分类" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.element_type === 'image' && row.config?.image_category" type="info" size="small">
                  {{ row.config.image_category }}
                </el-tag>
                <span v-else class="placeholder-text">-</span>
              </template>
            </el-table-column>

            <el-table-column prop="tags" label="标签" width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <el-tag
                  v-for="tag in row.tags"
                  :key="tag"
                  size="small"
                  class="tag-item"
                >
                  {{ tag }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="预览" width="200" align="center">
              <template #default="{ row }">
                <div v-if="row.element_type === 'image'" class="preview-image">
                  <el-image
                    :src="getImageUrl(row)"
                    fit="contain"
                    style="width: 150px; height: 80px; cursor: pointer"
                    :preview-src-list="[getImageUrl(row)]"
                    preview-teleported
                  />
                </div>

                <div v-else-if="row.element_type === 'pos'" class="preview-pos">
                  <el-space :size="4">
                    <el-tag type="primary" size="small">X: {{ row.config?.x }}</el-tag>
                    <el-tag type="primary" size="small">Y: {{ row.config?.y }}</el-tag>
                  </el-space>
                </div>

                <div v-else-if="row.element_type === 'region'" class="preview-region">
                  <el-space direction="vertical" :size="4">
                    <el-space :size="4">
                      <el-tag type="success" size="small">X1: {{ row.config?.x1 }}</el-tag>
                      <el-tag type="success" size="small">Y1: {{ row.config?.y1 }}</el-tag>
                    </el-space>
                    <el-space :size="4">
                      <el-tag type="warning" size="small">X2: {{ row.config?.x2 }}</el-tag>
                      <el-tag type="warning" size="small">Y2: {{ row.config?.y2 }}</el-tag>
                    </el-space>
                  </el-space>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="usage_count" label="使用次数" width="100" sortable />

            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>

            <template #actions="{ row }">
              <el-button size="small" type="primary" link @click="handleEdit(row)">
                编辑
              </el-button>
              <el-button size="small" link @click="handleDuplicate(row)">
                复制
              </el-button>
              <el-button size="small" type="danger" link @click="handleDelete(row)">
                删除
              </el-button>
            </template>
          </UnifiedListTable>
        </div>
      </div>
    </el-card>

    <CaptureElementDialog
      v-model="captureDialogVisible"
      :project-list="projectList"
      @success="handleCreateSuccess"
    />

    <ManualElementDialog
      v-model="dialogVisible"
      :edit-data="editElement"
      :project-list="projectList"
      @success="handleCreateSuccess"
    />

    <el-dialog
      v-model="detailDialogVisible"
      title="元素详情"
      width="800px"
    >
      <el-descriptions v-if="viewingElement" :column="2" border>
        <el-descriptions-item label="元素名称">{{ viewingElement.name }}</el-descriptions-item>
        <el-descriptions-item label="元素类型">
          <el-tag :type="getTypeColor(viewingElement.element_type)">
            {{ getTypeName(viewingElement.element_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="标签" :span="2">
          <el-tag v-for="tag in viewingElement.tags" :key="tag" size="small" class="tag-item">
            {{ tag }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="配置信息" :span="2">
          <pre class="config-preview">{{ JSON.stringify(viewingElement.config, null, 2) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="使用次数">{{ viewingElement.usage_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(viewingElement.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Camera } from '@element-plus/icons-vue'
import { UnifiedListTable } from '@/components/platform-shared'
import {
  StateEmpty,
  StateError,
  StateForbidden,
  StateLoading,
  StateSearchEmpty,
  UI_PAGE_STATE
} from '@/components/ui-states'
import {
  getAppElementList,
  createAppElement,
  deleteAppElement as apiDeleteAppElement,
  getAppProjects
} from '@/api/app-automation'
import { formatDateTime } from '@/utils/app-automation-helpers'
import CaptureElementDialog from './components/CaptureElementDialog.vue'
import ManualElementDialog from './components/ManualElementDialog.vue'

const router = useRouter()

const loading = ref(false)
const elements = ref([])
const selectedElements = ref([])
const searchQuery = ref('')
const typeFilter = ref('')
const projectFilter = ref(null)
const projectList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const hasLoaded = ref(false)
const requestState = ref(UI_PAGE_STATE.READY)
const requestErrorMessage = ref('')

const dialogVisible = ref(false)
const captureDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const editElement = ref(null)
const viewingElement = ref(null)

const hasActiveFilter = computed(() => {
  return Boolean(projectFilter.value || typeFilter.value || searchQuery.value.trim())
})

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
  if (elements.value.length === 0) {
    return hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return UI_PAGE_STATE.READY
})

const resolveRequestState = (error) => {
  if (error?.response?.status === 403) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  return UI_PAGE_STATE.REQUEST_ERROR
}

const loadElements = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (typeFilter.value) {
      params.element_type = typeFilter.value
    }
    if (projectFilter.value) {
      params.project = projectFilter.value
    }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }

    const res = await getAppElementList(params)
    elements.value = res.data.results || []
    total.value = res.data.count || 0
    requestState.value = UI_PAGE_STATE.READY
    requestErrorMessage.value = ''
    hasLoaded.value = true

    const maxPage = Math.max(1, Math.ceil((total.value || 0) / pageSize.value))
    if (total.value > 0 && currentPage.value > maxPage) {
      currentPage.value = maxPage
      await loadElements()
    }
  } catch (error) {
    console.error('加载元素列表失败:', error)
    elements.value = []
    total.value = 0
    hasLoaded.value = true
    requestState.value = resolveRequestState(error)
    requestErrorMessage.value = error?.response?.data?.detail || error?.message || '加载元素列表失败'
    ElMessage.error('加载元素列表失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadElements()
}

const resetFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
  projectFilter.value = null
  currentPage.value = 1
  loadElements()
}

const showCreateDialog = () => {
  editElement.value = null
  dialogVisible.value = true
}

const showCaptureDialog = () => {
  captureDialogVisible.value = true
}

const handleView = (element) => {
  viewingElement.value = element
  detailDialogVisible.value = true
}

const handleEdit = (element) => {
  editElement.value = element
  dialogVisible.value = true
}

const findAvailableName = (baseName) => {
  const firstCandidate = `${baseName}_副本`
  if (!elements.value.some((element) => element.name === firstCandidate)) {
    return firstCandidate
  }

  const pattern = new RegExp(`^${baseName.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\$&')}_副本\\((\\d+)\\)$`)
  let maxNum = 1

  elements.value.forEach((element) => {
    const match = element.name.match(pattern)
    if (match) {
      const current = Number.parseInt(match[1], 10)
      if (current > maxNum) {
        maxNum = current
      }
    }
  })

  return `${baseName}_副本(${maxNum + 1})`
}

const handleDuplicate = async (element) => {
  try {
    const newName = findAvailableName(element.name)
    const newConfig = { ...element.config }
    delete newConfig.file_hash

    const duplicateData = {
      ...element,
      name: newName,
      id: undefined,
      created_at: undefined,
      updated_at: undefined,
      created_by: undefined,
      created_by_id: undefined,
      last_used_at: undefined,
      usage_count: 0,
      config: newConfig
    }

    await createAppElement(duplicateData)
    ElMessage.success(`已复制为 "${newName}"`)
    await loadElements()
  } catch (error) {
    console.error('复制失败:', error)
    const errorMsg = error.response?.data?.config?.[0]
      || error.response?.data?.name?.[0]
      || error.response?.data?.message
      || '复制失败'
    ElMessage.error(errorMsg)
  }
}

const handleCreateSuccess = () => {
  currentPage.value = 1
  loadElements()
}

const handleSelectionChange = (selection) => {
  selectedElements.value = selection
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedElements.value.length} 个元素吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    for (const element of selectedElements.value) {
      await apiDeleteAppElement(element.id)
    }

    ElMessage.success('批量删除成功')
    selectedElements.value = []
    await loadElements()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

const handleDelete = async (element) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除元素 "${element.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await apiDeleteAppElement(element.id)
    ElMessage.success('删除成功')
    await loadElements()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const getImageUrl = (element) => {
  if (!element?.id) return ''
  const timestamp = element.updated_at ? new Date(element.updated_at).getTime() : Date.now()
  return `/api/app-automation/elements/${element.id}/preview/?t=${timestamp}`
}

const getTypeColor = (type) => {
  const colorMap = {
    image: 'primary',
    pos: 'success',
    region: 'warning'
  }
  return colorMap[type] || 'info'
}

const getTypeName = (type) => {
  const nameMap = {
    image: '图片',
    pos: '坐标',
    region: '区域'
  }
  return nameMap[type] || type
}

onMounted(() => {
  getAppProjects({ page_size: 100 }).then((res) => {
    projectList.value = res.data.results || res.data || []
  }).catch(() => {})
  loadElements()
})
</script>

<style scoped lang="scss">
.element-management {
  padding: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-section {
  margin-top: 16px;
}

.table-container {
  min-height: 260px;
}

.preview-image {
  padding: 5px;

  :deep(.el-image) {
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    overflow: hidden;

    &:hover {
      border-color: #409eff;
    }
  }
}

.preview-pos,
.preview-region {
  display: flex;
  justify-content: center;
}

.batch-actions {
  margin-bottom: 16px;
  padding: 10px;
  background: #ecf5ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;

  span {
    color: #409eff;
    font-weight: 500;
  }
}

.placeholder-text {
  color: #909399;
}

.tag-item {
  margin-right: 5px;
}

.config-preview {
  margin: 0;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.5;
}
</style>
