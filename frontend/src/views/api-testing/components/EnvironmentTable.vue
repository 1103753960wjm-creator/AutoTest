<template>
  <div class="environment-table">
    <UnifiedListTable
      v-model:currentPage="innerCurrentPage"
      v-model:pageSize="innerPageSize"
      :total="total"
      :page-sizes="pageSizes"
      :data="data"
      :loading="loading"
      row-key="id"
      selection-mode="none"
      :actions="{ view: false, edit: false, delete: false }"
      :action-column-width="280"
      @page-change="emitPageChange"
    >
      <el-table-column prop="name" :label="$t('apiTesting.component.environmentTable.environmentName')" min-width="200" show-overflow-tooltip />
      <el-table-column prop="scope" :label="$t('apiTesting.component.environmentTable.scope')" width="120">
        <template #default="{ row }">
          <el-tag :type="row.scope === 'GLOBAL' ? 'primary' : 'success'">
            {{ row.scope === 'GLOBAL' ? $t('apiTesting.component.environmentTable.global') : $t('apiTesting.component.environmentTable.local') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        v-if="scope === 'LOCAL'"
        prop="project_name"
        :label="$t('apiTesting.component.environmentTable.relatedProject')"
        width="150"
      />
      <el-table-column :label="$t('apiTesting.component.environmentTable.variableCount')" width="100">
        <template #default="{ row }">
          {{ Object.keys(row.variables || {}).length }}
        </template>
      </el-table-column>
      <el-table-column prop="is_active" :label="$t('apiTesting.component.environmentTable.status')" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_active" type="success" size="small">{{ $t('apiTesting.component.environmentTable.activated') }}</el-tag>
          <el-tag v-else type="info" size="small">{{ $t('apiTesting.component.environmentTable.notActivated') }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_by.username" :label="$t('apiTesting.component.environmentTable.createdBy')" width="120" />
      <el-table-column prop="created_at" :label="$t('apiTesting.component.environmentTable.createdAt')" width="160">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <template #actions="{ row }">
        <el-button
          v-if="!row.is_active"
          link
          type="success"
          size="small"
          @click="$emit('activate', row)"
        >
          {{ $t('apiTesting.component.environmentTable.activate') }}
        </el-button>
        <el-button link type="primary" size="small" @click="viewVariables(row)">
          {{ $t('apiTesting.component.environmentTable.viewVariables') }}
        </el-button>
        <el-button link type="primary" size="small" @click="$emit('edit', row)">
          {{ $t('apiTesting.component.environmentTable.edit') }}
        </el-button>
        <el-button link type="primary" size="small" @click="$emit('duplicate', row)">
          {{ $t('apiTesting.component.environmentTable.copy') }}
        </el-button>
        <el-button link type="danger" size="small" @click="$emit('delete', row)">
          {{ $t('apiTesting.component.environmentTable.delete') }}
        </el-button>
      </template>
    </UnifiedListTable>

    <el-dialog
      v-model="showViewDialog"
      :title="$t('apiTesting.component.environmentTable.environmentVariables')"
      width="600px"
    >
      <div v-if="viewingEnvironment" class="variables-view">
        <div class="env-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item :label="$t('apiTesting.component.environmentTable.environmentName')">
              {{ viewingEnvironment.name }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('apiTesting.component.environmentTable.scope')">
              <el-tag :type="viewingEnvironment.scope === 'GLOBAL' ? 'primary' : 'success'">
                {{ viewingEnvironment.scope === 'GLOBAL' ? $t('apiTesting.component.environmentTable.global') : $t('apiTesting.component.environmentTable.local') }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="viewingEnvironment.project_name" :label="$t('apiTesting.component.environmentTable.relatedProject')">
              {{ viewingEnvironment.project_name }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('apiTesting.component.environmentTable.status')">
              <el-tag v-if="viewingEnvironment.is_active" type="success">{{ $t('apiTesting.component.environmentTable.activated') }}</el-tag>
              <el-tag v-else type="info">{{ $t('apiTesting.component.environmentTable.notActivated') }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="variables-table">
          <h4>{{ $t('apiTesting.component.environmentTable.variableList') }}</h4>
          <el-table :data="formatVariables(viewingEnvironment.variables)" style="width: 100%">
            <el-table-column prop="key" :label="$t('apiTesting.component.environmentTable.variableName')" width="150" />
            <el-table-column prop="initialValue" :label="$t('apiTesting.component.environmentTable.initialValue')" />
            <el-table-column prop="currentValue" :label="$t('apiTesting.component.environmentTable.currentValue')" />
          </el-table>
        </div>
      </div>

      <template #footer>
        <el-button @click="showViewDialog = false">{{ $t('apiTesting.component.environmentTable.close') }}</el-button>
        <el-button type="primary" @click="$emit('edit', viewingEnvironment)">
          {{ $t('apiTesting.component.environmentTable.editEnvironment') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import dayjs from 'dayjs'
import { UnifiedListTable } from '@/components/platform-shared'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  scope: {
    type: String,
    default: 'GLOBAL'
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 20
  },
  total: {
    type: Number,
    default: 0
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  }
})

const emit = defineEmits([
  'edit',
  'delete',
  'activate',
  'duplicate',
  'update:currentPage',
  'update:pageSize',
  'page-change'
])

const showViewDialog = ref(false)
const viewingEnvironment = ref(null)
const innerCurrentPage = ref(props.currentPage)
const innerPageSize = ref(props.pageSize)

watch(() => props.currentPage, (value) => {
  innerCurrentPage.value = value
})

watch(() => props.pageSize, (value) => {
  innerPageSize.value = value
})

const formatDate = (dateString) => {
  return dateString ? dayjs(dateString).format('YYYY-MM-DD HH:mm') : '-'
}

const formatVariables = (variables) => {
  if (!variables || typeof variables !== 'object') return []

  return Object.keys(variables).map((key) => {
    const value = variables[key]
    if (typeof value === 'object') {
      return {
        key,
        initialValue: value.initialValue || '',
        currentValue: value.currentValue || value.initialValue || ''
      }
    }
    return {
      key,
      initialValue: value || '',
      currentValue: value || ''
    }
  })
}

const viewVariables = (environment) => {
  viewingEnvironment.value = environment
  showViewDialog.value = true
}

const emitPageChange = ({ currentPage, pageSize }) => {
  emit('update:currentPage', currentPage)
  emit('update:pageSize', pageSize)
  emit('page-change', { currentPage, pageSize })
}
</script>

<style scoped>
.environment-table {
  height: 100%;
}

.variables-view {
  max-height: 70vh;
  overflow-y: auto;
}

.env-info {
  margin-bottom: 20px;
}

.variables-table h4 {
  margin: 20px 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}
</style>
