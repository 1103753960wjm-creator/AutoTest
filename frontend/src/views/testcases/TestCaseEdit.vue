<template>
  <div class="page-container">
    <div class="card-container" v-if="!loading">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item :label="$t('testcase.caseTitle')" prop="title">
          <el-input v-model="form.title" :placeholder="$t('testcase.caseTitlePlaceholder')" />
        </el-form-item>

        <el-form-item :label="$t('testcase.caseDescription')" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            :placeholder="$t('testcase.caseDescriptionPlaceholder')"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item :label="$t('testcase.project')" prop="project_id">
              <el-select
                v-model="form.project_id"
                :placeholder="$t('testcase.selectProject')"
                clearable
                filterable
                @change="onProjectChange"
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('testcase.priority')" prop="priority">
              <el-select v-model="form.priority" :placeholder="$t('testcase.selectPriority')">
                <el-option :label="$t('testcase.low')" value="low" />
                <el-option :label="$t('testcase.medium')" value="medium" />
                <el-option :label="$t('testcase.high')" value="high" />
                <el-option :label="$t('testcase.critical')" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('testcase.testType')" prop="test_type">
              <el-select v-model="form.test_type" :placeholder="$t('testcase.selectTestType')">
                <el-option :label="$t('testcase.functional')" value="functional" />
                <el-option :label="$t('testcase.integration')" value="integration" />
                <el-option :label="$t('testcase.api')" value="api" />
                <el-option :label="$t('testcase.ui')" value="ui" />
                <el-option :label="$t('testcase.performance')" value="performance" />
                <el-option :label="$t('testcase.security')" value="security" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item :label="$t('testcase.relatedVersions')">
              <el-select
                v-model="form.version_ids"
                :placeholder="$t('testcase.selectVersions')"
                multiple
                clearable
                filterable
                @change="onVersionChange"
              >
                <el-option
                  v-for="version in projectVersions"
                  :key="version.id"
                  :label="version.name + (version.is_baseline ? ' (' + $t('testcase.baseline') + ')' : '')"
                  :value="version.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item :label="$t('testcase.preconditions')" prop="preconditions">
          <el-input
            v-model="form.preconditions"
            type="textarea"
            :rows="3"
            :placeholder="$t('testcase.preconditionsPlaceholder')"
          />
        </el-form-item>

        <el-form-item :label="$t('testcase.steps')" prop="steps">
          <el-input
            v-model="form.steps"
            type="textarea"
            :rows="6"
            maxlength="1000"
            show-word-limit
            :placeholder="$t('testcase.stepsPlaceholder')"
          />
        </el-form-item>

        <el-form-item :label="$t('testcase.expectedResult')" prop="expected_result">
          <el-input
            v-model="form.expected_result"
            type="textarea"
            :rows="3"
            :placeholder="$t('testcase.expectedResultPlaceholder')"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ $t('testcase.saveChanges') }}
          </el-button>
          <el-button @click="handleReturn">{{ $t('common.cancel') }}</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card-container" v-else>
      <el-skeleton :rows="10" animated />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Check } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'
import { buildDeeplinkLocation, resolveReturnTarget, sanitizeSourceContext } from '@/router/deeplink'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(true)
const submitting = ref(false)
const projects = ref([])
const projectVersions = ref([])

const form = reactive({
  title: '',
  description: '',
  project_id: null,
  priority: 'medium',
  test_type: 'functional',
  preconditions: '',
  steps: '',
  expected_result: '',
  version_ids: []
})

const rules = {
  title: [
    { required: true, message: computed(() => t('testcase.titleRequired')), trigger: 'blur' },
    { min: 5, max: 500, message: computed(() => t('testcase.titleLength')), trigger: 'blur' }
  ],
  expected_result: [
    { required: true, message: computed(() => t('testcase.expectedResultRequired')), trigger: 'blur' }
  ],
  steps: [
    { max: 1000, message: computed(() => t('testcase.stepsMaxLength')), trigger: 'blur' }
  ]
}

const sourceContext = computed(() => sanitizeSourceContext(route.query))

const returnTarget = computed(() => {
  return resolveReturnTarget({
    route,
    fallbackPath: '/ai-generation/testcases',
    fallbackTitle: '测试用例'
  })
})

const handleReturn = () => {
  if (returnTarget.value?.path) {
    router.push(returnTarget.value.path)
    return
  }

  router.back()
}

// 将 HTML 的 <br> 标签转换为换行符，便于编辑时展示。
const convertBrToNewline = (text) => {
  if (!text) return ''
  return text.replace(/<br\s*\/?>/gi, '\n')
}

// 提交前再把换行符转换回 <br>，保持现有接口协议不变。
const convertNewlineToBr = (text) => {
  if (!text) return ''
  return text.replace(/\n/g, '<br>')
}

const testcaseMetaItems = computed(() => ([
  {
    label: '所属项目',
    value: form.project_id ? `${form.project_id}` : '未关联'
  },
  {
    label: '关联版本',
    value: `${form.version_ids.length}`
  }
]))

usePlatformPageHeader(() => ({
  description: '编辑页继续复用统一页面头部，表单与提交逻辑仍由页面主体承接。',
  helperText: sourceContext.value.fromTitle
    ? `当前通过 ${sourceContext.value.fromTitle} 进入编辑页，返回动作会优先回到来源。`
    : '当前仅补齐深链接与回跳规则，不重写表单逻辑。',
  metaItems: testcaseMetaItems.value,
  actions: [
    {
      key: 'back-source',
      label: returnTarget.value?.label || '返回上一步',
      plain: true,
      icon: ArrowLeft,
      onClick: handleReturn
    },
    {
      key: 'save-testcase',
      label: t('testcase.saveChanges'),
      type: 'primary',
      icon: Check,
      onClick: handleSubmit
    }
  ]
}))

const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/list/')
    projects.value = response.data.results || []
  } catch (error) {
    ElMessage.error(t('testcase.fetchProjectsFailed'))
  }
}

const fetchProjectVersions = async (projectId) => {
  if (!projectId) {
    projectVersions.value = []
    return
  }

  try {
    const response = await api.get(`/versions/projects/${projectId}/versions/`)
    projectVersions.value = response.data || []
  } catch (error) {
    console.error(t('testcase.fetchVersionsFailed'), error)
    ElMessage.error(t('testcase.fetchVersionsFailed'))
    projectVersions.value = []
  }
}

const onProjectChange = (projectId) => {
  form.version_ids = []
  fetchProjectVersions(projectId)
}

const onVersionChange = () => {}

const fetchTestCase = async () => {
  try {
    const response = await api.get(`/testcases/${route.params.id}/`)
    const testcase = response.data

    form.title = testcase.title
    form.description = testcase.description
    form.project_id = testcase.project?.id || null
    form.priority = testcase.priority
    form.test_type = testcase.test_type
    form.preconditions = convertBrToNewline(testcase.preconditions || '')
    form.expected_result = convertBrToNewline(testcase.expected_result || '')
    form.steps = convertBrToNewline(testcase.steps || '')
    form.version_ids = testcase.versions ? testcase.versions.map((version) => version.id) : []

    if (form.project_id) {
      await fetchProjectVersions(form.project_id)
    }

    loading.value = false
  } catch (error) {
    ElMessage.error(t('testcase.fetchDetailFailed'))
    handleReturn()
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) {
      return
    }

    submitting.value = true

    try {
      const submitData = {
        ...form,
        preconditions: convertNewlineToBr(form.preconditions || ''),
        steps: convertNewlineToBr(form.steps || ''),
        expected_result: convertNewlineToBr(form.expected_result || '')
      }

      await api.put(`/testcases/${route.params.id}/`, submitData)
      ElMessage.success(t('testcase.updateSuccess'))

      const nextLocation = buildDeeplinkLocation({
        target: `/ai-generation/testcases/${route.params.id}`,
        sourceContext: sourceContext.value
      })

      if (nextLocation) {
        router.push(nextLocation)
        return
      }

      router.push(`/ai-generation/testcases/${route.params.id}`)
    } catch (error) {
      ElMessage.error(t('testcase.updateFailed'))
      console.error('提交测试用例失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

onMounted(async () => {
  await fetchProjects()
  await fetchTestCase()
})
</script>
