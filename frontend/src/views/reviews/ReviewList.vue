<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ $t('reviewList.title') }}</h1>
      <div>
        <el-button @click="goToAutoReviews">
          查看 AI 自动评审
        </el-button>
        <el-button type="primary" @click="createReview">
          <el-icon><Plus /></el-icon>
          {{ $t('reviewList.createReview') }}
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item :label="$t('reviewList.project')">
          <el-select
            v-model="filters.project"
            class="filter-select"
            :placeholder="$t('reviewList.selectProject')"
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
        </el-form-item>
        <el-form-item :label="$t('reviewList.status')">
          <el-select
            v-model="filters.status"
            class="filter-select"
            :placeholder="$t('reviewList.selectStatus')"
            clearable
            @change="handleFilter"
          >
            <el-option :label="$t('reviewList.statusPending')" value="pending" />
            <el-option :label="$t('reviewList.statusInProgress')" value="in_progress" />
            <el-option :label="$t('reviewList.statusApproved')" value="approved" />
            <el-option :label="$t('reviewList.statusRejected')" value="rejected" />
            <el-option :label="$t('reviewList.statusCancelled')" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('reviewList.reviewer')">
          <el-select
            v-model="filters.reviewer"
            class="filter-select"
            :placeholder="$t('reviewList.selectReviewer')"
            clearable
            @change="handleFilter"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
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
      @primary-action="fetchReviews"
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
      :primary-action-text="$t('reviewList.createReview')"
      @primary-action="createReview"
    />
    <div v-else class="table-container">
      <UnifiedListTable
        v-model:currentPage="pagination.page"
        v-model:pageSize="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        :data="reviews"
        :loading="loading"
        row-key="id"
        selection-mode="none"
        :actions="{ view: false, edit: false, delete: false }"
        :action-column-width="180"
        @page-change="fetchReviews"
      >
        <el-table-column :label="$t('reviewList.reviewTitle')" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link type="primary" @click="viewReview(row.id)">
              {{ row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column :label="$t('reviewList.reviewProject')" width="200">
          <template #default="{ row }">
            <span v-if="row.projects && row.projects.length > 0">
              {{ row.projects.map(p => p.name).join(', ') }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('reviewList.reviewStatus')" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('reviewList.priority')" width="100">
          <template #default="{ row }">
            <el-tag :class="`priority-tag ${row.priority}`">{{ getPriorityText(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator.username" :label="$t('reviewList.creator')" width="120" />
        <el-table-column :label="$t('reviewList.testcaseCount')" width="100">
          <template #default="{ row }">
            {{ row.testcases?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('reviewList.progress')" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="getReviewProgress(row)"
              :color="getProgressColor(row)"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column prop="deadline" :label="$t('reviewList.deadline')" width="160">
          <template #default="{ row }">
            {{ row.deadline ? formatDate(row.deadline) : $t('reviewList.noDeadline') }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="$t('reviewList.createdAt')" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <template #actions="{ row }">
          <div class="table-actions">
            <el-button v-if="canReview(row)" link type="success" @click="submitReview(row)">{{ $t('reviewList.review') }}</el-button>
            <el-button v-if="canEdit(row)" link type="warning" @click="editReview(row.id)">{{ $t('reviewList.edit') }}</el-button>
            <el-popconfirm
              v-if="canDelete(row)"
              :title="$t('reviewList.deleteConfirm')"
              @confirm="deleteReview(row.id)"
            >
              <template #reference>
                <el-button link type="danger">{{ $t('reviewList.delete') }}</el-button>
              </template>
            </el-popconfirm>
            <span v-if="!hasRowActions(row)" class="action-placeholder">-</span>
          </div>
        </template>
      </UnifiedListTable>
    </div>

    <el-dialog v-model="reviewDialogVisible" :title="$t('reviewList.submitReview')" width="600px">
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item :label="$t('reviewList.reviewResult')" required>
          <el-radio-group v-model="reviewForm.status">
            <el-radio-button label="approved">{{ $t('reviewList.approved') }}</el-radio-button>
            <el-radio-button label="rejected">{{ $t('reviewList.rejected') }}</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="$t('reviewList.reviewComment')">
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            :placeholder="$t('reviewList.reviewCommentPlaceholder')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">{{ $t('reviewList.cancel') }}</el-button>
        <el-button type="primary" @click="confirmSubmitReview">{{ $t('reviewList.submit') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import { UnifiedListTable } from '@/components/platform-shared'
import { StateEmpty, StateError, StateForbidden, StateLoading, StateSearchEmpty, UI_PAGE_STATE } from '@/components/ui-states'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()

const reviews = ref([])
const projects = ref([])
const users = ref([])
const loading = ref(false)
const reviewDialogVisible = ref(false)
const currentReview = ref(null)
const hasLoaded = ref(false)
const requestState = ref(`${UI_PAGE_STATE.READY}`)
const requestErrorMessage = ref('')

const filters = reactive({
  project: '',
  status: '',
  reviewer: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const hasActiveFilter = computed(() => Boolean(filters.project || filters.status || filters.reviewer))

const pageState = computed(() => {
  let state = String(UI_PAGE_STATE.READY)
  if (loading.value && !hasLoaded.value) {
    state = UI_PAGE_STATE.LOADING
  } else if (requestState.value === UI_PAGE_STATE.FORBIDDEN) {
    state = UI_PAGE_STATE.FORBIDDEN
  } else if (requestState.value === UI_PAGE_STATE.REQUEST_ERROR) {
    state = UI_PAGE_STATE.REQUEST_ERROR
  } else if (reviews.value.length === 0) {
    state = hasActiveFilter.value ? UI_PAGE_STATE.SEARCH_EMPTY : UI_PAGE_STATE.EMPTY
  }
  return state
})

const reviewForm = reactive({
  status: 'approved',
  comment: ''
})

const fetchReviews = async () => {
  loading.value = true
  requestState.value = UI_PAGE_STATE.READY
  requestErrorMessage.value = ''
  let shouldRefetch = false
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      ...filters
    }
    Object.keys(params).forEach(key => params[key] === '' && delete params[key])

    const response = await api.get('/reviews/reviews/', { params })
    reviews.value = response.data.results
    pagination.total = response.data.count
    const maxPage = Math.max(1, Math.ceil((pagination.total || 0) / pagination.size || 1))
    if (pagination.page > maxPage) {
      pagination.page = maxPage
      shouldRefetch = true
      return
    }
    hasLoaded.value = true
  } catch (error) {
    ElMessage.error(t('reviewList.fetchListFailed'))
    requestState.value = error.response?.status === 403 ? UI_PAGE_STATE.FORBIDDEN : UI_PAGE_STATE.REQUEST_ERROR
    requestErrorMessage.value = error.response?.data?.detail || error.message || ''
    hasLoaded.value = true
  } finally {
    if (!shouldRefetch) {
      loading.value = false
    }
  }
  if (shouldRefetch) {
    await fetchReviews()
  }
}

const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/')
    projects.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

const fetchUsers = async () => {
  try {
    const response = await api.get('/auth/users/')
    users.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const createReview = () => {
  router.push('/ai-generation/reviews/create')
}

const goToAutoReviews = () => {
  router.push('/ai-generation/reviews/ai-auto')
}

const viewReview = (id) => {
  router.push(`/ai-generation/reviews/${id}`)
}

const editReview = (id) => {
  router.push(`/ai-generation/reviews/${id}/edit`)
}

const submitReview = (review) => {
  currentReview.value = review
  reviewForm.status = 'approved'
  reviewForm.comment = ''
  reviewDialogVisible.value = true
}

const confirmSubmitReview = async () => {
  try {
    await api.post(`/reviews/reviews/${currentReview.value.id}/submit_review/`, reviewForm)
    ElMessage.success(t('reviewList.submitSuccess'))
    reviewDialogVisible.value = false
    fetchReviews()
  } catch (error) {
    ElMessage.error(t('reviewList.submitFailed'))
  }
}

const deleteReview = async (id) => {
  try {
    await api.delete(`/reviews/reviews/${id}/`)
    ElMessage.success(t('reviewList.deleteSuccess'))
    fetchReviews()
  } catch (error) {
    ElMessage.error(t('reviewList.deleteFailed'))
  }
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    in_progress: 'primary',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: t('reviewList.statusPending'),
    in_progress: t('reviewList.statusInProgress'),
    approved: t('reviewList.statusApproved'),
    rejected: t('reviewList.statusRejected'),
    cancelled: t('reviewList.statusCancelled')
  }
  return textMap[status] || status
}

const getPriorityText = (priority) => {
  const textMap = {
    low: t('reviewList.priorityLow'),
    medium: t('reviewList.priorityMedium'),
    high: t('reviewList.priorityHigh'),
    urgent: t('reviewList.priorityCritical')
  }
  return textMap[priority] || priority
}

const getReviewProgress = (review) => {
  const assignments = review.assignments || []
  if (assignments.length === 0) return 0

  const completedCount = assignments.filter(a => a.status !== 'pending').length
  return Math.round((completedCount / assignments.length) * 100)
}

const getProgressColor = (review) => {
  const progress = getReviewProgress(review)
  if (progress === 100) return '#67c23a'
  if (progress >= 50) return '#e6a23c'
  return '#f56c6c'
}

const canReview = (review) => {
  return review.assignments?.some(a => a.reviewer.id === userStore.user?.id && a.status === 'pending')
}

const canEdit = (review) => {
  return review.creator.id === userStore.user?.id && ['pending', 'in_progress'].includes(review.status)
}

const canDelete = (review) => {
  return review.creator.id === userStore.user?.id && review.status === 'pending'
}

const hasRowActions = (review) => {
  return canReview(review) || canEdit(review) || canDelete(review)
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const handleFilter = () => {
  pagination.page = 1
  fetchReviews()
}

const resetFilters = () => {
  filters.project = ''
  filters.status = ''
  filters.reviewer = ''
  pagination.page = 1
  fetchReviews()
}

onMounted(() => {
  fetchReviews()
  fetchProjects()
  fetchUsers()
})
</script>

<style lang="scss" scoped>
.table-container {
  overflow: hidden;

  :deep(.unified-list-table) {
    display: flex;
    flex-direction: column;
  }
}

.filter-form {
  :deep(.filter-select) {
    width: 180px;
  }
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.action-placeholder {
  color: #94a3b8;
}

.priority-tag {
  &.low { color: #67c23a; }
  &.medium { color: #e6a23c; }
  &.high { color: #f56c6c; }
  &.urgent { color: #f56c6c; font-weight: bold; }
}
</style>
