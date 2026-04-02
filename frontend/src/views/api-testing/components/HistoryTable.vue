<template>
  <div class="history-table">
    <UnifiedListTable
      :data="data"
      :loading="loading"
      row-key="id"
      selection-mode="multi"
      :show-pagination="false"
      :actions="{ view: false, edit: false, delete: false }"
      :action-column-width="200"
      @selection-change="$emit('selection-change', $event)"
    >
      <el-table-column prop="request.name" :label="$t('apiTesting.component.historyTable.requestName')" min-width="200" />
      <el-table-column prop="request.method" :label="$t('apiTesting.component.historyTable.method')" width="80">
        <template #default="scope">
          <el-tag :type="getMethodType(scope.row.request.method)" size="small">
            {{ scope.row.request.method }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="request_data.url" :label="$t('apiTesting.component.historyTable.url')" min-width="300" show-overflow-tooltip />
      <el-table-column prop="status_code" :label="$t('apiTesting.component.historyTable.statusCode')" width="100">
        <template #default="scope">
          <el-tag
            v-if="scope.row.status_code"
            :type="getStatusType(scope.row.status_code)"
            size="small"
          >
            {{ scope.row.status_code }}
          </el-tag>
          <el-tag v-else type="danger" size="small">{{ $t('apiTesting.component.historyTable.error') }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="response_time" :label="$t('apiTesting.component.historyTable.responseTime')" width="100">
        <template #default="scope">
          {{ scope.row.response_time?.toFixed(0) || 0 }}ms
        </template>
      </el-table-column>
      <el-table-column prop="environment.name" :label="$t('apiTesting.component.historyTable.environment')" width="120">
        <template #default="scope">
          {{ scope.row.environment?.name || $t('apiTesting.component.historyTable.noEnvironment') }}
        </template>
      </el-table-column>
      <el-table-column prop="executed_by.username" :label="$t('apiTesting.component.historyTable.executor')" width="120" />
      <el-table-column prop="executed_at" :label="$t('apiTesting.component.historyTable.executionTime')" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.executed_at) }}
        </template>
      </el-table-column>
      <template #actions="{ row }">
          <el-button link type="primary" @click="$emit('view-detail', row)" size="small">
            {{ $t('apiTesting.component.historyTable.viewDetail') }}
          </el-button>
          <el-button link type="primary" @click="$emit('retry-request', row)" size="small">
            {{ $t('apiTesting.component.historyTable.retryRequest') }}
          </el-button>
          <el-button link type="danger" @click="$emit('delete-item', row)" size="small">
            {{ $t('apiTesting.component.historyTable.delete') }}
          </el-button>
      </template>
    </UnifiedListTable>
  </div>
</template>

<script setup>
import dayjs from 'dayjs'
import { UnifiedListTable } from '@/components/platform-shared'

defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['view-detail', 'retry-request', 'selection-change', 'delete-item'])

const getMethodType = (method) => {
  const typeMap = {
    'GET': 'success',
    'POST': 'primary', 
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return typeMap[method] || 'info'
}

const getStatusType = (status) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 300 && status < 400) return 'warning'
  if (status >= 400) return 'danger'
  return 'info'
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('MM-DD HH:mm')
}
</script>

<style scoped>
.history-table {
  height: 100%;
  overflow: hidden;

  :deep(.unified-list-table) {
    display: flex;
    flex-direction: column;
  }
}
</style>
