<template>
  <div class="app-package-list">
    <div class="page-header">
      <h3>包名管理</h3>
      <div class="header-actions">
        <el-button :icon="Refresh" :loading="loading" @click="loadPackages">
          刷新
        </el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          新增包名
        </el-button>
      </div>
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
        :description="requestErrorMessage || '加载应用包名失败，请稍后重试。'"
        @primary-action="loadPackages"
      />
      <StateEmpty v-else-if="pageState === UI_PAGE_STATE.EMPTY" compact />
      <div v-else class="table-container">
        <UnifiedListTable
          v-model:currentPage="currentPage"
          v-model:pageSize="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          :data="packages"
          :loading="loading"
          row-key="id"
          selection-mode="none"
          :actions="{ view: false, edit: true, delete: true }"
          :action-column-width="180"
          :delete-name="(row) => row?.name || ''"
          @page-change="loadPackages"
          @edit="openEditDialog"
          @delete="handleDelete"
        >
          <el-table-column prop="name" label="应用名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="package_name" label="应用包名" min-width="220" show-overflow-tooltip />
          <el-table-column label="创建人" min-width="120">
            <template #default="{ row }">
              {{ row.created_by_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="创建时间" min-width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="更新时间" min-width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.updated_at) }}
            </template>
          </el-table-column>
        </UnifiedListTable>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="应用名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：Android设置" />
        </el-form-item>
        <el-form-item label="应用包名" prop="package_name">
          <el-input v-model="form.package_name" placeholder="例如：com.android.settings" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { UnifiedListTable } from '@/components/platform-shared'
import {
  StateEmpty,
  StateError,
  StateForbidden,
  StateLoading,
  UI_PAGE_STATE
} from '@/components/ui-states'
import {
  getPackageList,
  createPackage,
  updatePackage,
  deletePackage
} from '@/api/app-automation'
import { formatDateTime } from '@/utils/app-automation-helpers'

const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const packages = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const hasLoaded = ref(false)
const requestState = ref(UI_PAGE_STATE.READY)
const requestErrorMessage = ref('')

const dialogVisible = ref(false)
const dialogTitle = ref('新增包名')
const isEditing = ref(false)
const formRef = ref(null)
const form = reactive({
  id: null,
  name: '',
  package_name: ''
})

const rules = {
  name: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  package_name: [{ required: true, message: '请输入应用包名', trigger: 'blur' }]
}

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
  if (packages.value.length === 0) {
    return UI_PAGE_STATE.EMPTY
  }
  return UI_PAGE_STATE.READY
})

const normalizePayload = (data) => {
  const payload = data?.success !== undefined ? data.data : data
  return {
    results: payload?.results || payload || [],
    count: payload?.count || 0
  }
}

const resolveRequestState = (error) => {
  if (error?.response?.status === 403) {
    return UI_PAGE_STATE.FORBIDDEN
  }
  return UI_PAGE_STATE.REQUEST_ERROR
}

const loadPackages = async () => {
  loading.value = true
  try {
    const res = await getPackageList({
      page: currentPage.value,
      page_size: pageSize.value
    })
    const payload = normalizePayload(res.data)
    packages.value = Array.isArray(payload.results) ? payload.results : []
    total.value = payload.count || packages.value.length || 0
    requestState.value = UI_PAGE_STATE.READY
    requestErrorMessage.value = ''
    hasLoaded.value = true

    const maxPage = Math.max(1, Math.ceil((total.value || 0) / pageSize.value))
    if (total.value > 0 && currentPage.value > maxPage) {
      currentPage.value = maxPage
      await loadPackages()
    }
  } catch (error) {
    console.error('加载应用包名失败:', error)
    packages.value = []
    total.value = 0
    hasLoaded.value = true
    requestState.value = resolveRequestState(error)
    requestErrorMessage.value = error?.response?.data?.detail || error?.message || '加载应用包名失败'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.package_name = ''
}

const openCreateDialog = async () => {
  isEditing.value = false
  dialogTitle.value = '新增包名'
  resetForm()
  dialogVisible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

const openEditDialog = async (row) => {
  isEditing.value = true
  dialogTitle.value = '编辑包名'
  form.id = row.id
  form.name = row.name
  form.package_name = row.package_name
  dialogVisible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

const submitForm = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      if (isEditing.value && form.id) {
        await updatePackage(form.id, {
          name: form.name,
          package_name: form.package_name
        })
        ElMessage.success('更新成功')
      } else {
        await createPackage({
          name: form.name,
          package_name: form.package_name
        })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      if (!isEditing.value) {
        currentPage.value = 1
      }
      await loadPackages()
    } catch (error) {
      console.error('保存应用包名失败:', error)
      ElMessage.error(error?.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await deletePackage(row.id)
    ElMessage.success('删除成功')
    await loadPackages()
  } catch (error) {
    console.error('删除应用包名失败:', error)
    ElMessage.error(error?.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadPackages()
})
</script>

<style scoped lang="scss">
.app-package-list {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    margin: 0;
    font-size: 20px;
    color: #303133;
  }
}

.header-actions {
  display: flex;
  gap: 12px;
}

.table-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.table-container {
  min-height: 200px;
}
</style>
