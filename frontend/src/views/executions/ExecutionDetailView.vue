<template>
  <div class="execution-detail">
    <div class="execution-summary-card" v-if="testPlan.name">
      <div class="execution-summary-card__meta">
        <el-tag v-if="testPlan.version" type="primary" class="execution-summary-card__tag">
          <el-icon><Stamp /></el-icon>
          {{ testPlan.version }}
        </el-tag>
        <span class="execution-summary-card__projects">
          <el-icon><FolderOpened /></el-icon>
          <span v-if="testPlan.projects && testPlan.projects.length > 0">
            {{ testPlan.projects.join(', ') }}
          </span>
          <span v-else class="no-data">{{ $t('execution.noProject') }}</span>
        </span>
      </div>
      <p class="execution-summary-card__description">
        执行进度、用例状态和历史记录继续由页面主体承接，本轮只补齐统一头部和回跳动作。
      </p>
    </div>

    <div v-if="testPlan.test_runs && testPlan.test_runs.length > 0">
      <div v-for="run in testPlan.test_runs" :key="run.id" class="test-run-card">
        <div class="run-header">
          <div class="run-title-section">
            <h2 class="run-title">{{ run.name }}</h2>
            <el-tag :type="getRunStatusType(run.progress)" size="large" class="run-status-tag">
              {{ getRunStatusText(run.progress) }}
            </el-tag>
          </div>

          <div class="stats-cards">
            <div class="stat-card total">
              <el-icon class="stat-icon"><Document /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ run.progress.total }}</div>
                <div class="stat-label">{{ $t('execution.total') }}</div>
              </div>
            </div>
            <div class="stat-card passed">
              <el-icon class="stat-icon"><CircleCheck /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ run.progress.passed }}</div>
                <div class="stat-label">{{ $t('execution.passed') }}</div>
              </div>
            </div>
            <div class="stat-card failed">
              <el-icon class="stat-icon"><CircleClose /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ run.progress.failed }}</div>
                <div class="stat-label">{{ $t('execution.failed') }}</div>
              </div>
            </div>
            <div class="stat-card blocked">
              <el-icon class="stat-icon"><WarningFilled /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ run.progress.blocked }}</div>
                <div class="stat-label">{{ $t('execution.blocked') }}</div>
              </div>
            </div>
            <div class="stat-card untested">
              <el-icon class="stat-icon"><QuestionFilled /></el-icon>
              <div class="stat-content">
                <div class="stat-value">{{ run.progress.untested }}</div>
                <div class="stat-label">{{ $t('execution.untested') }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="progress-section">
          <el-progress
            :percentage="run.progress.progress"
            :stroke-width="12"
            :color="getProgressColor(run.progress.progress)"
            :show-text="true"
          >
            <template #default="{ percentage }">
              <span class="progress-text">{{ percentage }}%</span>
            </template>
          </el-progress>
        </div>

        <div v-if="selectedCases.length > 0" class="batch-actions">
          <el-button
            type="danger"
            :icon="Delete"
            @click="batchDeleteCases"
            :disabled="isDeleting"
          >
            {{ $t('execution.batchDelete') }} ({{ selectedCases.length }})
          </el-button>
        </div>

        <el-table
          ref="tableRef"
          :data="paginatedCases(run.run_cases)"
          style="width: 100%"
          class="execution-table"
          @selection-change="handleSelectionChange"
          :row-key="(row) => row.id"
        >
          <el-table-column type="selection" width="55" :reserve-selection="true" />
          <el-table-column
            type="index"
            :label="$t('execution.serialNumber')"
            width="80"
            :index="getSerialNumber"
          />
          <el-table-column prop="testcase" :label="$t('execution.testCase')" min-width="250" />
          <el-table-column :label="$t('execution.executionStatus')" width="150">
            <template #default="scope">
              <el-select
                v-model="scope.row.status"
                @change="updateCaseStatus(scope.row)"
                size="small"
              >
                <el-option :label="$t('execution.untested')" value="untested" />
                <el-option :label="$t('execution.passed')" value="passed" />
                <el-option :label="$t('execution.failed')" value="failed" />
                <el-option :label="$t('execution.blocked')" value="blocked" />
                <el-option :label="$t('execution.retest')" value="retest" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="$t('execution.comments')" min-width="250">
            <template #default="scope">
              <el-input
                v-model="scope.row.comments"
                :placeholder="$t('execution.commentsPlaceholder')"
                type="textarea"
                :rows="2"
                size="small"
                @blur="updateCaseDetails(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column :label="$t('execution.actions')" width="120" fixed="right">
            <template #default="scope">
              <el-button
                size="small"
                type="primary"
                :icon="Clock"
                @click="viewCaseHistory(scope.row)"
              >
                {{ $t('execution.viewHistory') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="run.run_cases && run.run_cases.length > 0" class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="run.run_cases.length"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="handlePageChange"
            @size-change="handleSizeChange"
          />
        </div>
      </div>
    </div>

    <el-dialog
      :title="$t('execution.executionHistory')"
      v-model="historyDialogVisible"
      width="80%"
    >
      <el-table :data="currentCaseHistory" style="width: 100%">
        <el-table-column prop="status" :label="$t('execution.status')" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="comments" :label="$t('execution.comments')" show-overflow-tooltip />
        <el-table-column prop="executed_by.username" :label="$t('execution.executedBy')" width="120" />
        <el-table-column prop="executed_at" :label="$t('execution.executedAt')" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.executed_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  CircleCheck,
  CircleClose,
  Clock,
  Delete,
  Document,
  FolderOpened,
  QuestionFilled,
  Stamp,
  WarningFilled
} from '@element-plus/icons-vue'
import axios from 'axios'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'
import { resolveReturnTarget, sanitizeSourceContext } from '@/router/deeplink'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const testPlan = ref({})
const historyDialogVisible = ref(false)
const currentCaseHistory = ref([])
const selectedCases = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const isDeleting = ref(false)
const tableRef = ref(null)

const sourceContext = computed(() => sanitizeSourceContext(route.query))

const returnTarget = computed(() => {
  return resolveReturnTarget({
    route,
    fallbackPath: '/ai-generation/executions',
    fallbackTitle: '测试计划'
  })
})

const handleReturn = () => {
  if (returnTarget.value?.path) {
    router.push(returnTarget.value.path)
    return
  }

  router.back()
}

const executionMetaItems = computed(() => {
  return [
    {
      label: '执行轮次',
      value: `${testPlan.value.test_runs?.length || 0}`
    },
    {
      label: '关联项目',
      value: `${testPlan.value.projects?.length || 0}`
    }
  ]
})

usePlatformPageHeader(() => ({
  title: testPlan.value.name || '',
  description: testPlan.value.description || '执行详情继续承接测试运行、状态修改和历史记录查看。',
  updateText: testPlan.value.updated_at ? `最近更新 ${formatDate(testPlan.value.updated_at)}` : '',
  helperText: sourceContext.value.fromTitle
    ? `当前通过 ${sourceContext.value.fromTitle} 打开执行详情，返回动作会优先回到来源。`
    : '当前仅补齐统一深链接和回跳规则，不改执行详情业务逻辑。',
  metaItems: executionMetaItems.value,
  actions: [
    {
      key: 'back-source',
      label: returnTarget.value?.label || '返回上一步',
      type: 'primary',
      icon: ArrowLeft,
      onClick: handleReturn
    }
  ]
}))

const fetchTestPlan = async () => {
  try {
    const planId = route.params.id
    const response = await axios.get(`/api/executions/plans/${planId}/`)
    testPlan.value = response.data
  } catch (error) {
    ElMessage.error(t('execution.fetchDetailFailed'))
  }
}

const updateCaseStatus = async (runCase) => {
  try {
    await axios.patch(`/api/executions/run_cases/${runCase.id}/update_status/`, {
      status: runCase.status,
      comments: runCase.comments || ''
    })
    await fetchTestPlan()
    ElMessage.success(t('execution.statusUpdateSuccess'))
  } catch (error) {
    ElMessage.error(t('execution.statusUpdateFailed'))
  }
}

const updateCaseDetails = async (runCase) => {
  try {
    await axios.patch(`/api/executions/run_cases/${runCase.id}/update_status/`, {
      status: runCase.status,
      comments: runCase.comments || ''
    })
    ElMessage.success(t('execution.detailsUpdateSuccess'))
  } catch (error) {
    ElMessage.error(t('execution.detailsUpdateFailed'))
  }
}

const viewCaseHistory = async (runCase) => {
  try {
    const response = await axios.get(`/api/executions/run_cases/${runCase.id}/history/`)
    currentCaseHistory.value = response.data
    historyDialogVisible.value = true
  } catch (error) {
    ElMessage.error(t('execution.fetchHistoryFailed'))
  }
}

const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

const batchDeleteCases = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning(t('execution.selectCasesFirst'))
    return
  }

  try {
    await ElMessageBox.confirm(
      t('execution.batchDeleteCasesConfirm', { count: selectedCases.value.length }),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )

    isDeleting.value = true
    let successCount = 0
    let failCount = 0

    for (const runCase of selectedCases.value) {
      try {
        await axios.delete(`/api/executions/run_cases/${runCase.id}/`)
        successCount++
      } catch (error) {
        console.error(`删除用例 ${runCase.id} 失败:`, error)
        failCount++
      }
    }

    if (successCount > 0) {
      if (failCount > 0) {
        ElMessage.success(t('execution.batchDeleteCasesPartialSuccess', { successCount, failCount }))
      } else {
        ElMessage.success(t('execution.batchDeleteCasesSuccess', { successCount }))
      }
    } else {
      ElMessage.error(t('execution.batchDeleteFailed'))
    }

    selectedCases.value = []
    await fetchTestPlan()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error(t('execution.batchDeleteFailed'))
    }
  } finally {
    isDeleting.value = false
  }
}

const paginatedCases = (cases) => {
  if (!cases) return []
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return cases.slice(start, end)
}

const getSerialNumber = (index) => {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

const handlePageChange = () => {
  selectedCases.value = []

  if (tableRef.value) {
    tableRef.value.clearSelection()
  }
}

const handleSizeChange = () => {
  currentPage.value = 1
  selectedCases.value = []

  if (tableRef.value) {
    tableRef.value.clearSelection()
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getProgressColor = (percentage) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

const getRunStatusType = (progress) => {
  if (progress.progress === 100) return 'success'
  if (progress.failed > 0) return 'danger'
  if (progress.blocked > 0) return 'warning'
  return 'info'
}

const getRunStatusText = (progress) => {
  if (progress.progress === 100) return t('execution.completed')
  if (progress.untested === progress.total) return t('execution.notStarted')
  return t('execution.inProgress')
}

const getStatusType = (status) => {
  const typeMap = {
    untested: 'info',
    passed: 'success',
    failed: 'danger',
    blocked: 'warning',
    retest: 'primary'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    untested: t('execution.untested'),
    passed: t('execution.passed'),
    failed: t('execution.failed'),
    blocked: t('execution.blocked'),
    retest: t('execution.retest')
  }
  return textMap[status] || status
}

onMounted(() => {
  fetchTestPlan()
})
</script>

<style scoped>
.execution-detail {
  padding: 24px 0 8px;
}

.execution-summary-card {
  margin-bottom: 24px;
  padding: 20px 22px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.94) 100%);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);
}

.execution-summary-card__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.execution-summary-card__tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.execution-summary-card__projects {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #475569;
  font-size: 14px;
}

.execution-summary-card__description {
  margin: 12px 0 0;
  color: #64748b;
  font-size: 14px;
  line-height: 1.7;
}

.no-data {
  color: #94a3b8;
  font-style: italic;
}

.test-run-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.run-header {
  margin-bottom: 24px;
}

.run-title-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.run-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.run-status-tag {
  font-weight: 600;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.passed {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  color: #155724;
}

.stat-card.failed {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: #721c24;
}

.stat-card.blocked {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #856404;
}

.stat-card.untested {
  background: linear-gradient(135deg, #e0e7ff 0%, #cfd9ff 100%);
  color: #383d41;
}

.stat-icon {
  font-size: 32px;
  opacity: 0.9;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.9;
}

.progress-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.progress-text {
  font-weight: 600;
  font-size: 14px;
}

.batch-actions {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}

.execution-table {
  border-radius: 8px;
  overflow: hidden;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
