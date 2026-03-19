<template>
  <div class="page-container">
    <div class="card-container" v-if="testcase">
      <el-descriptions :column="2" border>
        <el-descriptions-item :label="$t('testcase.caseTitle')" :span="2">{{ testcase.title }}</el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.priority')">
          <el-tag :class="`priority-tag ${testcase.priority}`">{{ getPriorityText(testcase.priority) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.testType')">{{ getTypeText(testcase.test_type) }}</el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.project')">{{ testcase.project?.name || $t('testcase.noProject') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.relatedVersions')" :span="2">
          <div v-if="testcase.versions && testcase.versions.length > 0" class="version-tags">
            <el-tag
              v-for="version in testcase.versions"
              :key="version.id"
              size="small"
              :type="version.is_baseline ? 'warning' : 'info'"
              class="version-tag"
            >
              {{ version.name }}
            </el-tag>
          </div>
          <span v-else class="no-version">{{ $t('testcase.noVersion') }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.author')">{{ testcase.author?.username }}</el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.createdAt')" :span="2">{{ formatDate(testcase.created_at) }}</el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.caseDescription')" :span="2">{{ testcase.description || $t('testcase.noDescription') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.preconditions')" :span="2">
          <div v-html="testcase.preconditions || $t('testcase.none')"></div>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.steps')" :span="2">
          <div class="steps-content" v-html="testcase.steps || $t('testcase.none')"></div>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('testcase.expectedResult')" :span="2">
          <div v-html="testcase.expected_result || $t('testcase.none')"></div>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'
import { buildDeeplinkLocation, resolveReturnTarget, sanitizeSourceContext } from '@/router/deeplink'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const testcase = ref(null)

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

const editTestCase = () => {
  const nextLocation = buildDeeplinkLocation({
    target: `/ai-generation/testcases/${route.params.id}/edit`,
    sourceContext: {
      from: 'detail',
      fromPath: route.fullPath,
      fromTitle: route.meta.title || '测试用例详情',
      fromModule: route.meta.module || 'test-design'
    }
  })

  if (nextLocation) {
    router.push(nextLocation)
    return
  }

  router.push(`/ai-generation/testcases/${route.params.id}/edit`)
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

const testcaseStatusTags = computed(() => {
  if (!testcase.value?.priority) {
    return []
  }

  return [
    {
      label: getPriorityText(testcase.value.priority),
      type: testcase.value.priority === 'critical' || testcase.value.priority === 'high' ? 'danger' : 'primary'
    }
  ]
})

const testcaseMetaItems = computed(() => {
  if (!testcase.value) {
    return []
  }

  return [
    {
      label: '所属项目',
      value: testcase.value.project?.name || '未关联'
    },
    {
      label: '关联版本',
      value: `${testcase.value.versions?.length || 0}`
    }
  ]
})

const sourceContext = computed(() => sanitizeSourceContext(route.query))

usePlatformPageHeader(() => ({
  title: testcase.value?.title || '',
  description: testcase.value?.description || '',
  statusTags: testcaseStatusTags.value,
  updateText: testcase.value?.updated_at ? `最近更新 ${formatDate(testcase.value.updated_at)}` : '',
  helperText: sourceContext.value.fromTitle
    ? `当前通过 ${sourceContext.value.fromTitle} 打开，可在头部直接返回来源。`
    : '当前支持从列表、搜索、最近访问和工作台深链接打开。',
  metaItems: testcaseMetaItems.value,
  actions: [
    {
      key: 'back-source',
      label: returnTarget.value?.label || '返回上一步',
      type: 'primary',
      icon: ArrowLeft,
      onClick: handleReturn
    },
    {
      key: 'edit-testcase',
      label: t('common.edit'),
      plain: true,
      icon: Edit,
      onClick: editTestCase
    }
  ]
}))

const fetchTestCase = async () => {
  try {
    const response = await api.get(`/testcases/${route.params.id}/`)
    testcase.value = response.data
  } catch (error) {
    ElMessage.error(t('testcase.fetchDetailFailed'))
  }
}

onMounted(() => {
  fetchTestCase()
})
</script>

<style lang="scss" scoped>
.priority-tag {
  &.low { color: #67c23a; }
  &.medium { color: #e6a23c; }
  &.high { color: #f56c6c; }
  &.critical { color: #f56c6c; font-weight: bold; }
}

.version-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  .version-tag {
    margin: 0;
  }
}

.no-version {
  color: #909399;
  font-size: 14px;
  font-style: italic;
}

.steps-content {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #303133;
  font-family: inherit;
}
</style>
