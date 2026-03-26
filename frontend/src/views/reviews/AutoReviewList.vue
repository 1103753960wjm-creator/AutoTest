<template>
  <div class="auto-review-list">
    <div class="filter-bar">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="项目">
          <el-select
            v-model="filters.project"
            clearable
            placeholder="全部项目"
            style="width: 180px"
            @change="fetchRecords">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="String(project.id)" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务 ID">
          <el-input
            v-model="filters.taskId"
            clearable
            placeholder="输入任务 ID"
            style="width: 220px"
            @keyup.enter="fetchRecords" />
        </el-form-item>
        <el-form-item label="评审状态">
          <el-select
            v-model="filters.status"
            clearable
            placeholder="全部状态"
            style="width: 180px"
            @change="fetchRecords">
            <el-option label="未触发" value="not_triggered" />
            <el-option label="评审中" value="reviewing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchRecords">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="summary-tip">
      默认仅展示每个任务最新一条自动评审记录。本轮列表不展开历史记录，但每条记录可展开查看完整评审内容。
    </div>

    <el-table :data="records" v-loading="loading" stripe>
      <el-table-column prop="task_id" label="任务 ID" width="180" />
      <el-table-column prop="task_title" label="任务标题" min-width="240" show-overflow-tooltip />
      <el-table-column prop="project_name" label="项目" min-width="160" show-overflow-tooltip />
      <el-table-column label="评审状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.review_status)">{{ getStatusLabel(row.review_status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="review_summary" label="评审摘要" min-width="260" show-overflow-tooltip />
      <el-table-column prop="source_stage" label="来源阶段" width="140" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <div class="row-actions">
            <el-button link type="primary" @click="openReviewContent(row)">查看全文</el-button>
            <el-button link type="success" @click="goToTaskDetail(row)">查看任务</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchRecords"
        @size-change="fetchRecords" />
    </div>

    <el-drawer
      v-model="drawerVisible"
      title="自动评审内容"
      size="50%">
      <div v-if="activeRecord" class="review-drawer">
        <div class="drawer-meta">
          <div><strong>任务：</strong>{{ activeRecord.task_id }}</div>
          <div><strong>项目：</strong>{{ activeRecord.project_name || '未关联项目' }}</div>
          <div><strong>状态：</strong>{{ getStatusLabel(activeRecord.review_status) }}</div>
        </div>
        <div v-if="activeRecord.failure_message" class="failure-block">
          <strong>失败信息</strong>
          <p>{{ activeRecord.failure_message }}</p>
        </div>
        <div class="content-block">
          <strong>评审内容</strong>
          <pre>{{ activeRecord.review_content || '当前记录暂无完整评审内容。' }}</pre>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import { getAutoReviewRecords } from '@/api/requirement-analysis'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'

const router = useRouter()
const route = useRoute()

usePlatformPageHeader(() => ({
  title: 'AI 自动评审',
  description: '统一查看生成链中的自动评审记录，并回到任务对象页继续追踪。',
  helperText: '默认仅展示每个任务最新一条自动评审记录，列表不展开历史记录。'
}))

const loading = ref(false)
const records = ref([])
const projects = ref([])
const drawerVisible = ref(false)
const activeRecord = ref(null)

const filters = reactive({
  project: route.query.project ? String(route.query.project) : '',
  taskId: route.query.taskId ? String(route.query.taskId) : '',
  status: route.query.status ? String(route.query.status) : ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const getStatusLabel = (status) => {
  const labelMap = {
    not_triggered: '未触发',
    reviewing: '评审中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return labelMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    not_triggered: 'info',
    reviewing: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

const formatDate = (value) => {
  if (!value) {
    return '-'
  }
  return dayjs(value).format('YYYY-MM-DD HH:mm')
}

const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/list/')
    projects.value = response.data.results || []
  } catch (error) {
    projects.value = []
  }
}

const syncQuery = () => {
  const nextQuery = {
    ...route.query,
    project: filters.project || undefined,
    taskId: filters.taskId || undefined,
    status: filters.status || undefined
  }
  router.replace({ query: nextQuery })
}

const fetchRecords = async () => {
  loading.value = true
  try {
    syncQuery()
    const response = await getAutoReviewRecords({
      page: pagination.page,
      page_size: pagination.pageSize,
      project: filters.project || undefined,
      task_id: filters.taskId || undefined,
      status: filters.status && filters.status !== 'not_triggered' ? filters.status : undefined
    })
    records.value = response.data.results || response.data || []
    pagination.total = response.data.count || records.value.length
  } catch (error) {
    ElMessage.error(`获取自动评审记录失败: ${error.response?.data?.error || error.message}`)
  } finally {
    loading.value = false
  }
}

const resetFilters = async () => {
  filters.project = ''
  filters.taskId = ''
  filters.status = ''
  pagination.page = 1
  await fetchRecords()
}

const openReviewContent = (record) => {
  activeRecord.value = record
  drawerVisible.value = true
}

const goToTaskDetail = (record) => {
  router.push({
    name: 'TaskDetail',
    params: { taskId: record.task_id },
    query: {
      from: 'list',
      fromPath: route.fullPath,
      fromTitle: route.meta?.title || 'AI 自动评审',
      fromModule: route.meta?.module || 'test-design'
    }
  })
}

onMounted(async () => {
  await fetchProjects()
  await fetchRecords()
})
</script>

<style scoped>
.summary-tip {
  margin-bottom: 16px;
  color: #64748b;
}

.row-actions {
  display: flex;
  gap: 12px;
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.drawer-meta {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
}

.failure-block {
  margin-bottom: 16px;
  color: #b91c1c;
}

.content-block pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
}
</style>
