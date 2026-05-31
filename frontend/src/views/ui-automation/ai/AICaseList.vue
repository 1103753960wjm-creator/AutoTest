<template>
  <ListShell>
    <div class="filters">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-input
            v-model="searchText"
            :placeholder="$t('uiAutomation.ai.caseList.searchPlaceholder')"
            clearable
            @input="handleSearch"
           style="width: 100%">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
      </el-row>
    </div>

    <div class="table-container">
      <UnifiedListTable
        v-model:currentPage="pagination.currentPage"
        v-model:pageSize="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        :data="cases"
        :loading="loading"
        row-key="id"
        selection-mode="multi"
        :actions="{ view: false, edit: false, delete: false }"
        :action-column-width="240"
        @page-change="loadCases"
        @selection-change="handleSelectionChange"
        @row-dblclick="row => editCase(row)"
      >
        <el-table-column prop="name" :label="$t('uiAutomation.ai.caseList.caseName')" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link @click="editCase(row)" type="primary">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" :label="$t('uiAutomation.common.description')" min-width="200" show-overflow-tooltip />
        <el-table-column prop="task_description" :label="$t('uiAutomation.ai.caseList.taskDescription')" min-width="300" show-overflow-tooltip />
        <el-table-column prop="created_at" :label="$t('uiAutomation.common.createTime')" width="180" :formatter="formatDate" />
        <template #actions="{ row }">
          <el-button size="small" type="success" link @click="runCase(row)">
            <el-icon><VideoPlay /></el-icon>
            {{ $t('uiAutomation.common.run') }}
          </el-button>
          <el-button size="small" type="primary" link @click="editCase(row)">
            <el-icon><Edit /></el-icon>
            {{ $t('uiAutomation.common.edit') }}
          </el-button>
          <el-button size="small" type="danger" link @click="deleteCase(row.id)">
            <el-icon><Delete /></el-icon>
            {{ $t('uiAutomation.common.delete') }}
          </el-button>
        </template>
      </UnifiedListTable>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" :title="$t('uiAutomation.ai.caseList.editCase')" width="600px" :close-on-click-modal="false">
      <el-form :model="editForm" :rules="formRules" ref="editFormRef" label-width="100px">
        <el-form-item :label="$t('uiAutomation.ai.caseList.caseName')" prop="name">
          <el-input v-model="editForm.name" :placeholder="$t('uiAutomation.ai.caseNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.common.description')" prop="description">
          <el-input v-model="editForm.description" type="textarea" :placeholder="$t('uiAutomation.ai.caseDescPlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('uiAutomation.ai.caseList.taskDescription')" prop="task_description">
          <el-input
            v-model="editForm.task_description"
            type="textarea"
            :rows="6"
            :placeholder="$t('uiAutomation.ai.taskPlaceholder')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">{{ $t('uiAutomation.common.cancel') }}</el-button>
          <el-button type="primary" @click="confirmEdit" :loading="saving">{{ $t('uiAutomation.common.save') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </ListShell>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, VideoPlay, Edit, Delete } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import {
  getAICases,
  updateAICase,
  deleteAICase,
  runAICase
} from '@/api/ui_automation'
import { UnifiedListTable } from '@/components/platform-shared'
import { ListShell } from '@/components/page-shells'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'

const { t } = useI18n()

// Header actions configuration
usePlatformPageHeader({
  title: computed(() => t('uiAutomation.ai.caseList.title'))
})
const router = useRouter()
const cases = ref([])
const loading = ref(false)
const searchText = ref('')
const total = ref(0)
const pagination = reactive({
  currentPage: 1,
  pageSize: 20
})

const showEditDialog = ref(false)
const saving = ref(false)
const selectedIds = ref([])

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}
const currentCaseId = ref(null)
const editForm = reactive({
  name: '',
  description: '',
  task_description: ''
})
const editFormRef = ref(null)

const formRules = computed(() => ({
  name: [{ required: true, message: t('uiAutomation.ai.rules.nameRequired'), trigger: 'blur' }],
  task_description: [{ required: true, message: t('uiAutomation.ai.caseList.rules.taskDescriptionRequired'), trigger: 'blur' }]
}))

// 加载用例列表
const loadCases = async () => {
  loading.value = true
  try {
    const response = await getAICases({
      page: pagination.currentPage,
      page_size: pagination.pageSize,
      search: searchText.value
    })

    cases.value = response.data.results || []
    total.value = response.data.count || 0
  } catch (error) {
    console.error('获取用例列表失败:', error)
    ElMessage.error(t('uiAutomation.ai.caseList.messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadCases()
}

const handleSizeChange = () => {
  pagination.currentPage = 1
  loadCases()
}

const handleCurrentChange = () => {
  loadCases()
}

// 编辑用例
const editCase = (row) => {
  currentCaseId.value = row.id
  editForm.name = row.name
  editForm.description = row.description
  editForm.task_description = row.task_description
  showEditDialog.value = true
}

const confirmEdit = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await updateAICase(currentCaseId.value, {
          name: editForm.name,
          description: editForm.description,
          task_description: editForm.task_description
        })

        ElMessage.success(t('uiAutomation.ai.caseList.messages.updateSuccess'))
        showEditDialog.value = false
        loadCases()
      } catch (error) {
        console.error('更新失败:', error)
        ElMessage.error(t('uiAutomation.ai.caseList.messages.updateFailed'))
      } finally {
        saving.value = false
      }
    }
  })
}

// 删除用例
const deleteCase = async (id) => {
  try {
    await ElMessageBox.confirm(
      t('uiAutomation.ai.caseList.messages.deleteConfirm'),
      t('uiAutomation.messages.confirm.tip'),
      {
        confirmButtonText: t('uiAutomation.common.confirm'),
        cancelButtonText: t('uiAutomation.common.cancel'),
        type: 'warning'
      }
    )

    await deleteAICase(id)
    ElMessage.success(t('uiAutomation.ai.caseList.messages.deleteSuccess'))
    loadCases()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(t('uiAutomation.ai.caseList.messages.deleteFailed'))
    }
  }
}

// 执行用例
const runCase = async (row) => {
  try {
    await runAICase(row.id)
    ElMessage.success(t('uiAutomation.ai.caseList.messages.runSuccess'))
    // 跳转到执行记录页面
    router.push('/ai-intelligent-mode/execution-records')
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error(t('uiAutomation.ai.caseList.messages.runFailed'))
  }
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  return new Date(cellValue).toLocaleString()
}

onMounted(() => {
  loadCases()
})
</script>

<style lang="scss" scoped>
.table-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;

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
</style>
