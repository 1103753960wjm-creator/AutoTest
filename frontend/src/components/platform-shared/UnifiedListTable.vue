<template>
  <div class="unified-list-table">
    <el-table
      ref="tableRef"
      class="unified-list-table__table"
      :data="data"
      :row-key="rowKey"
      :loading="loading"
      :default-sort="defaultSort"
      :highlight-current-row="selectionMode === 'single'"
      :border="true"
      :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#606266' }"
      @row-click="handleRowClick"
      @row-dblclick="handleRowDblClick"
      @sort-change="emit('sort-change', $event)"
      @selection-change="emit('selection-change', $event)"
    >
      <el-table-column
        v-if="selectionMode === 'multi'"
        type="selection"
        width="55"
        fixed="left"
        align="center"
      />

      <el-table-column
        v-else-if="selectionMode === 'single'"
        width="56"
        fixed="left"
        align="center"
        class-name="unified-list-table__selection-col"
      >
        <template #header>
          <span class="unified-list-table__selection-header" />
        </template>
        <template #default="{ row }">
          <el-radio
            :model-value="selectedKey"
            :label="getRowKey(row)"
            @change="setSelectedRow(row)"
            @click.stop
          >
            <span />
          </el-radio>
        </template>
      </el-table-column>

      <el-table-column
        v-if="showIndex"
        type="index"
        label="序号"
        width="80"
        align="center"
        :index="computeIndex"
        fixed="left"
      />

      <slot />

      <el-table-column
        v-if="hasActions"
        :label="actionLabel"
        :width="actionColumnWidth"
        fixed="right"
        class-name="unified-list-table__action-col"
      >
        <template #default="{ row }">
          <div class="unified-list-table__actions">
            <slot name="actions" :row="row">
              <!-- 默认操作列：详情 / 编辑 / 删除 -->
            <div class="unified-list-table__actions-inline">
              <el-button
                v-if="canShowAction('view', row)"
                size="small"
                type="primary"
                link
                @click.stop="emit('view', row)"
              >
                详情
              </el-button>
              <el-button
                v-if="canShowAction('edit', row)"
                size="small"
                type="primary"
                link
                @click.stop="emit('edit', row)"
              >
                编辑
              </el-button>
              <el-button
                v-if="canShowAction('delete', row)"
                size="small"
                type="danger"
                link
                :loading="isDeletingRow(row)"
                @click.stop="confirmDelete(row)"
              >
                删除
              </el-button>
            </div>

            <div class="unified-list-table__actions-dropdown">
              <el-dropdown trigger="click" @command="handleActionCommand($event, row)">
                <el-button size="small">
                  更多
                  <el-icon class="unified-list-table__more-icon">
                    <ArrowDown />
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item v-if="canShowAction('view', row)" command="view">详情</el-dropdown-item>
                    <el-dropdown-item v-if="canShowAction('edit', row)" command="edit">编辑</el-dropdown-item>
                    <el-dropdown-item v-if="canShowAction('delete', row)" command="delete" divided>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            </slot>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div v-if="showPagination" class="unified-list-table__pagination">
      <el-pagination
        v-model:current-page="innerCurrentPage"
        v-model:page-size="innerPageSize"
        :total="total"
        :page-sizes="pageSizes"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="emitPageChange"
        @size-change="emitPageSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, useSlots } from 'vue'
import { ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },

  rowKey: { type: [String, Function], default: 'id' },

  selectionMode: {
    type: String,
    default: 'multi',
    validator: (value) => ['none', 'single', 'multi'].includes(String(value))
  },
  selectedKey: { type: [String, Number, null], default: null },

  showIndex: { type: Boolean, default: true },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  total: { type: Number, default: 0 },
  showPagination: { type: Boolean, default: true },
  pageSizes: { type: Array, default: () => [10, 20, 50, 100] },

  defaultSort: { type: Object, default: undefined },

  actionColumnWidth: { type: Number, default: 160 },
  actionLabel: { type: String, default: '操作' },
  actions: {
    type: Object,
    default: () => ({
      view: true,
      edit: true,
      delete: true
    })
  },
  toggleOnRowClick: { type: Boolean, default: true },
  deleteName: { type: [String, Function], default: '' },
  deletingKey: { type: [String, Number, null], default: null }
})

const emit = defineEmits([
  'update:selectedKey',
  'row-click',
  'row-dblclick',
  'selection-change',
  'sort-change',
  'view',
  'edit',
  'delete',
  'update:currentPage',
  'update:pageSize',
  'page-change'
])

const tableRef = ref()
const slots = useSlots()

const hasActions = computed(() => {
  if (slots.actions) return true
  return Boolean(props.actions?.view || props.actions?.edit || props.actions?.delete)
})

const innerCurrentPage = ref(props.currentPage)
const innerPageSize = ref(props.pageSize)

watch(
  () => props.currentPage,
  (val) => {
    innerCurrentPage.value = val
  }
)

watch(
  () => props.pageSize,
  (val) => {
    innerPageSize.value = val
  }
)

function getRowKey(row) {
  if (typeof props.rowKey === 'function') return props.rowKey(row)
  return row?.[props.rowKey]
}

function computeIndex(index) {
  return (innerCurrentPage.value - 1) * innerPageSize.value + index + 1
}

function setSelectedRow(row) {
  emit('update:selectedKey', getRowKey(row))
}

function handleRowClick(row, column, event) {
  if (props.selectionMode === 'single') {
    setSelectedRow(row)
  }
  if (props.selectionMode === 'multi') {
    if (props.toggleOnRowClick) {
      tableRef.value?.toggleRowSelection?.(row)
    }
  }
  emit('row-click', row, column, event)
}

function handleRowDblClick(row, column, event) {
  emit('row-dblclick', row, column, event)
}

function resolveDeleteName(row) {
  if (typeof props.deleteName === 'function') return props.deleteName(row)
  if (props.deleteName) return props.deleteName
  return row?.name || row?.title || row?.label || row?.id || ''
}

function canShowAction(key, row) {
  const val = props.actions?.[key]
  if (typeof val === 'function') return Boolean(val(row))
  return Boolean(val)
}

function isDeletingRow(row) {
  if (props.deletingKey === null || props.deletingKey === undefined) return false
  return String(props.deletingKey) === String(getRowKey(row))
}

async function confirmDelete(row) {
  const displayName = resolveDeleteName(row)
  const text = displayName ? `确认删除【${displayName}】？此操作不可恢复。` : '确认删除该条记录？此操作不可恢复。'
  await ElMessageBox.confirm(text, '删除确认', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning'
  })
  emit('delete', row)
}

function handleActionCommand(command, row) {
  if (command === 'view') emit('view', row)
  if (command === 'edit') emit('edit', row)
  if (command === 'delete') confirmDelete(row)
}

function emitPageChange() {
  emit('update:currentPage', innerCurrentPage.value)
  emit('page-change', { currentPage: innerCurrentPage.value, pageSize: innerPageSize.value })
}

function emitPageSizeChange() {
  emit('update:pageSize', innerPageSize.value)
  emit('update:currentPage', 1)
  emit('page-change', { currentPage: 1, pageSize: innerPageSize.value })
}

</script>

<style scoped lang="scss">
.unified-list-table {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.unified-list-table__pagination {
  display: flex;
  justify-content: flex-end;
}

.unified-list-table__actions {
  display: flex;
  justify-content: flex-start;
}

.unified-list-table__actions-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.unified-list-table__actions-dropdown {
  display: none;
}

.unified-list-table__more-icon {
  margin-left: 6px;
}

@media (max-width: 768px) {
  .unified-list-table__actions-inline {
    display: none;
  }

  .unified-list-table__actions-dropdown {
    display: inline-flex;
  }
}
</style>

