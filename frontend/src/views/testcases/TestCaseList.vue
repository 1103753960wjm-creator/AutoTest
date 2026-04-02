<template>
  <div class="page-container">
    <div class="card-container">
      <div class="filter-bar">
        <el-row :gutter="20">
          <el-col :span="5">
            <el-input
              v-model="searchText"
              :placeholder="$t('testcase.searchPlaceholder')"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select v-model="projectFilter" :placeholder="$t('testcase.relatedProject')" clearable @change="handleFilter">
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-col>
          <el-col :span="3">
            <el-select v-model="priorityFilter" :placeholder="$t('testcase.priorityFilter')" clearable @change="handleFilter">
              <el-option :label="$t('testcase.low')" value="low" />
              <el-option :label="$t('testcase.medium')" value="medium" />
              <el-option :label="$t('testcase.high')" value="high" />
              <el-option :label="$t('testcase.critical')" value="critical" />
            </el-select>
          </el-col>
        </el-row>
      </div>
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
        @primary-action="fetchTestCases"
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
        :primary-action-text="$t('testcase.newCase')"
        @primary-action="() => router.push('/ai-generation/testcases/create')"
      />
      <template v-else>
        <div class="table-container">
          <UnifiedListTable
            v-model:currentPage="currentPage"
            v-model:pageSize="pageSize"
            :page-sizes="[15, 25, 35, 50, 100]"
            :total="total"
            :data="testcases"
            :loading="loading"
            row-key="id"
            selection-mode="multi"
            :actions="{
              view: true,
              edit: true,
              delete: true
            }"
            :delete-name="(row) => row?.title || ''"
            @selection-change="handleSelectionChange"
            @view="handleView"
            @edit="editTestCase"
            @delete="deleteTestCaseConfirmed"
            @row-dblclick="editTestCase"
            @page-change="fetchTestCases"
          >
            <el-table-column prop="title" :label="$t('testcase.caseTitle')" min-width="250">
              <template #default="{ row }">
                <el-link @click="goToTestCase(row.id)" type="primary">
                  {{ row.title }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="project.name" :label="$t('testcase.relatedProject')" width="150">
              <template #default="{ row }">
                {{ row.project?.name || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="versions" :label="$t('testcase.relatedVersions')" width="200">
              <template #default="{ row }">
                <div v-if="row.versions && row.versions.length > 0" class="version-tags">
                  <el-tag
                    v-for="version in row.versions.slice(0, 2)"
                    :key="version.id"
                    size="small"
                    :type="version.is_baseline ? 'warning' : 'info'"
                    class="version-tag"
                  >
                    {{ version.name }}
                  </el-tag>
                  <el-tooltip v-if="row.versions.length > 2" :content="getVersionsTooltip(row.versions)">
                    <el-tag size="small" type="info" class="version-tag">
                      +{{ row.versions.length - 2 }}
                    </el-tag>
                  </el-tooltip>
                </div>
                <span v-else class="no-version">{{ $t('testcase.noVersion') }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="priority" :label="$t('testcase.priority')" width="100">
              <template #default="{ row }">
                <el-tag :class="`priority-tag ${row.priority}`">{{ getPriorityText(row.priority) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="来源摘要" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.source_summary?.label || '来源未记录' }}
              </template>
            </el-table-column>
            <el-table-column label="自动化状态" min-width="180" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.automation_summary?.label || '待接自动化草稿' }}
              </template>
            </el-table-column>
            <el-table-column prop="test_type" :label="$t('testcase.testType')" width="120">
              <template #default="{ row }">
                {{ getTypeText(row.test_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="author.username" :label="$t('testcase.author')" width="120" />
            <el-table-column prop="created_at" :label="$t('testcase.createdAt')" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </UnifiedListTable>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Download, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'
import * as XLSX from 'xlsx'
import { buildDeeplinkLocation } from '@/router/deeplink'
import { UnifiedListTable } from '@/components/platform-shared'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const loading = ref(false)
const testcases = ref([])
const projects = ref([])
const currentPage = ref(1)
const pageSize = ref(15)
const total = ref(0)
const searchText = ref('')
const projectFilter = ref(null)
const priorityFilter = ref('')
const selectedTestCases = ref([])
const isDeleting = ref(false)
const sourceProjectName = computed(() => String(route.query.projectName || ''))
const hasLoaded = ref(false)
const requestState = ref(`${UI_PAGE_STATE.READY}`)
const requestErrorMessage = ref('')

const hasActiveFilter = computed(() => (
  Boolean(searchText.value) ||
  projectFilter.value !== null ||
  Boolean(priorityFilter.value)
))

const pageState = computed(() => {
  let state = String(UI_PAGE_STATE.READY)
  if (loading.value && !hasLoaded.value) {
    state = UI_PAGE_STATE.LOADING
  } else if (requestState.value === UI_PAGE_STATE.FORBIDDEN) {
    state = UI_PAGE_STATE.FORBIDDEN
  } else if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    state = UI_PAGE_STATE.REQUEST_ERROR
  } else if (testcases.value.length === 0) {
    state = hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return state
})

const listMetaItems = computed(() => ([
  { label: '当前列表', value: `${total.value}` },
  { label: '项目筛选', value: projectFilter.value ? '已按项目收敛' : '全部项目' },
  { label: 'AI 来源位', value: '已展示' },
  { label: '自动化状态位', value: '已预留' }
]))

usePlatformPageHeader(() => ({
  helperText: sourceProjectName.value
    ? `当前从项目 ${sourceProjectName.value} 进入，列表会优先按项目收敛。`
    : '测试用例已作为测试设计资产对象展示来源摘要和自动化状态位。',
  metaItems: listMetaItems.value,
  actions: [
    selectedTestCases.value.length > 0
      ? {
          key: 'delete-selected',
          label: `${t('testcase.batchDelete')} (${selectedTestCases.value.length})`,
          type: 'danger',
          icon: Delete,
          onClick: batchDeleteTestCases
        }
      : null,
    {
      key: 'export-list',
      label: t('testcase.exportExcel'),
      plain: true,
      icon: Download,
      onClick: exportToExcel
    },
    {
      key: 'create-testcase',
      label: t('testcase.newCase'),
      type: 'primary',
      icon: Plus,
      onClick: () => router.push('/ai-generation/testcases/create')
    }
  ].filter(Boolean)
}))

const fetchTestCases = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  requestErrorMessage.value = ''
  let shouldRefetch = false
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchText.value,
      project: projectFilter.value,
      priority: priorityFilter.value
    }
    const response = await api.get('/testcases/', { params })
    testcases.value = response.data.results || []
    total.value = response.data.count || 0
    const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value || 1))
    if (currentPage.value > maxPage) {
      currentPage.value = maxPage
      shouldRefetch = true
      return
    }
    hasLoaded.value = true
  } catch (error) {
    ElMessage.error(t('testcase.fetchListFailed'))
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
  } finally {
    if (!shouldRefetch) {
      loading.value = false
    }
  }
  if (shouldRefetch) {
    await fetchTestCases()
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchTestCases()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchTestCases()
}

const resetFilters = () => {
  searchText.value = ''
  projectFilter.value = null
  priorityFilter.value = ''
  currentPage.value = 1
  fetchTestCases()
}

const handleView = (row) => {
  if (row?.id) goToTestCase(row.id)
}

const goToTestCase = (id) => {
  const nextLocation = buildDeeplinkLocation({
    target: `/ai-generation/testcases/${id}`,
    currentRoute: route,
    sourceType: 'list',
    sourceTitle: '测试用例'
  })

  if (nextLocation) {
    router.push(nextLocation)
    return
  }

  router.push(`/ai-generation/testcases/${id}`)
}

const editTestCase = (testcase) => {
  const nextLocation = buildDeeplinkLocation({
    target: `/ai-generation/testcases/${testcase.id}/edit`,
    currentRoute: route,
    sourceType: 'list',
    sourceTitle: '测试用例'
  })

  if (nextLocation) {
    router.push(nextLocation)
    return
  }

  router.push(`/ai-generation/testcases/${testcase.id}/edit`)
}

const deleteTestCase = async (testcase) => {
  try {
    await api.delete(`/testcases/${testcase.id}/`)
    ElMessage.success(t('testcase.deleteSuccess'))
    fetchTestCases()
  } catch (error) {
    ElMessage.error(t('testcase.deleteFailed'))
  }
}

const deleteTestCaseConfirmed = async (testcase) => {
  await deleteTestCase(testcase)
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedTestCases.value = selection
}


// 批量删除
const batchDeleteTestCases = async () => {
  if (selectedTestCases.value.length === 0) {
    ElMessage.warning(t('testcase.selectFirst'))
    return
  }

  try {
    await ElMessageBox.confirm(
      t('testcase.batchDeleteConfirm', { count: selectedTestCases.value.length }),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )

    isDeleting.value = true
    const ids = selectedTestCases.value.map(tc => tc.id)
    
    const response = await api.post('/testcases/batch-delete/', { ids })
    
    ElMessage.success(response.data.message || t('testcase.batchDeleteSuccess', { successCount: ids.length }))

    // 清空选择并重新加载列表
    selectedTestCases.value = []
    fetchTestCases()

  } catch (error) {
    if (error !== 'cancel') {
      console.error('Batch delete failed:', error)
      ElMessage.error(t('testcase.batchDeleteError') + ': ' + (error.message || t('common.error')))
    }
  } finally {
    isDeleting.value = false
  }
}

const getPriorityText = (priority) => {
  const textMap = {
    low: t('testcase.low'),
    medium: t('testcase.medium'),
    high: t('testcase.high'),
    critical: t('testcase.critical')
  }
  return textMap[priority] || priority
}

const getTypeText = (type) => {
  const textMap = {
    functional: t('testcase.functional'),
    integration: t('testcase.integration'),
    api: t('testcase.api'),
    ui: t('testcase.ui'),
    performance: t('testcase.performance'),
    security: t('testcase.security')
  }
  return textMap[type] || '-'
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const getVersionsTooltip = (versions) => {
  return versions.map(v => v.name + (v.is_baseline ? ' (' + t('testcase.baseline') + ')' : '')).join('、')
}

// 将HTML的<br>标签转换为换行符（用于Excel导出）
const convertBrToNewline = (text) => {
  if (!text) return ''
  return text.replace(/<br\s*\/?>/gi, '\n')
}

const exportToExcel = async () => {
  try {
    loading.value = true

    // 确定要导出的数据
    let testCasesToExport = []

    if (selectedTestCases.value.length > 0) {
      // 如果有勾选，导出勾选的数据
      testCasesToExport = selectedTestCases.value
    } else {
      // 如果没有勾选，分页获取所有数据
      const pageSize = 100  // 使用后端允许的最大值
      let page = 1
      let hasMore = true
      let allData = []

      while (hasMore) {
        const response = await api.get('/testcases/', {
          params: {
            page: page,
            page_size: pageSize,
            search: searchText.value,
            project: projectFilter.value,
            priority: priorityFilter.value
          }
        })

        const results = response.data.results || []
        allData.push(...results)

        // 检查是否还有更多数据
        // 如果返回的数据少于pageSize，说明已经是最后一页
        if (results.length < pageSize) {
          hasMore = false
        } else {
          page++
        }
      }

      testCasesToExport = allData
    }

    if (testCasesToExport.length === 0) {
      ElMessage.warning(t('testcase.noDataToExport'))
      loading.value = false
      return
    }

    // 创建工作簿
    const workbook = XLSX.utils.book_new()

    // 准备Excel数据
    const worksheetData = [
      [t('testcase.excelNumber'), t('testcase.excelTitle'), t('testcase.excelProject'), t('testcase.excelVersions'), t('testcase.excelPreconditions'), t('testcase.excelSteps'), t('testcase.excelExpectedResult'), t('testcase.excelPriority'), t('testcase.excelTestType'), t('testcase.excelAuthor'), t('testcase.excelCreatedAt')]
    ]

    testCasesToExport.forEach((testcase, index) => {
      const versions = testcase.versions && testcase.versions.length > 0
        ? testcase.versions.map(v => v.name + (v.is_baseline ? '(' + t('testcase.baseline') + ')' : '')).join('、')
        : t('testcase.noVersion')

      worksheetData.push([
        `TC${String(index + 1).padStart(3, '0')}`,
        testcase.title || '',
        testcase.project?.name || '',
        versions,
        convertBrToNewline(testcase.preconditions || ''),
        convertBrToNewline(testcase.steps || ''),
        convertBrToNewline(testcase.expected_result || ''),
        getPriorityText(testcase.priority),
        getTypeText(testcase.test_type),
        testcase.author?.username || '',
        formatDate(testcase.created_at)
      ])
    })
    
    // 创建工作表
    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)
    
    // 设置列宽
    const colWidths = [
      { wch: 15 }, // Test case number
      { wch: 30 }, // Case title
      { wch: 20 }, // Related project
      { wch: 25 }, // Related versions
      { wch: 30 }, // Preconditions
      { wch: 40 }, // Steps
      { wch: 30 }, // Expected result
      { wch: 10 }, // Priority
      { wch: 15 }, // Test type
      { wch: 15 }, // Author
      { wch: 20 }  // Created at
    ]
    worksheet['!cols'] = colWidths
    
    // 设置表头样式
    for (let col = 0; col < worksheetData[0].length; col++) {
      const cellAddress = XLSX.utils.encode_cell({ r: 0, c: col })
      if (!worksheet[cellAddress]) continue
      worksheet[cellAddress].s = {
        font: { bold: true },
        alignment: { horizontal: 'center', vertical: 'center', wrapText: true }
      }
    }
    
    // 设置其他行的样式
    for (let row = 1; row < worksheetData.length; row++) {
      for (let col = 0; col < worksheetData[row].length; col++) {
        const cellAddress = XLSX.utils.encode_cell({ r: row, c: col })
        if (worksheet[cellAddress]) {
          worksheet[cellAddress].s = {
            alignment: { vertical: 'top', wrapText: true }
          }
        }
      }
    }

    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(workbook, worksheet, t('testcase.excelSheetName'))

    // Generate filename
    const fileName = t('testcase.excelFileName', { date: new Date().toISOString().slice(0, 10) })

    // Export file
    XLSX.writeFile(workbook, fileName)

    ElMessage.success(t('testcase.exportSuccess'))
  } catch (error) {
    console.error('Export test cases failed:', error)
    ElMessage.error(t('testcase.exportFailed') + ': ' + (error.message || t('common.error')))
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/')
    projects.value = response.data.results || response.data || []
  } catch (error) {
    ElMessage.error(t('testcase.fetchProjectsFailed'))
  }
}

onMounted(() => {
  const projectFromQuery = route.query.project
  if (projectFromQuery) {
    projectFilter.value = Number(projectFromQuery)
  }
  fetchProjects()
  fetchTestCases()
})
</script>

<style lang="scss" scoped>
.page-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.card-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-bar {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}

.table-container {
  flex: 1;
  overflow: hidden;
  padding: 0 20px;

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

.pagination-container {
  padding: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.priority-tag {
  &.low { color: #67c23a; }
  &.medium { color: #e6a23c; }
  &.high { color: #f56c6c; }
  &.critical { color: #f56c6c; font-weight: bold; }
}

.version-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  
  .version-tag {
    margin: 0;
  }
}

.no-version {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

@media (max-width: 1200px) {
  .page-container {
    height: auto;
    min-height: 100vh;
    overflow-y: auto;
  }
  
  .card-container {
    min-height: 600px;
  }
  
  .table-container {
    min-height: 400px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .filter-bar {
    padding: 15px;
  }
  
  .pagination-container {
    padding: 15px;
  }
}

.step-content {
  min-height: 200px;
}

.preview-info {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;

  p {
    margin: 5px 0;
  }
}
</style>
