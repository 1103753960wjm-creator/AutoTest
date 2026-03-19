<template>
  <div class="page-container">
    <div v-if="project" class="project-object-overview">
      <div class="project-summary-grid">
        <div class="summary-card">
          <span class="summary-card__label">设计资产</span>
          <strong class="summary-card__value">{{ project.testcase_count || 0 }}</strong>
          <span class="summary-card__desc">当前项目下的正式测试用例</span>
        </div>
        <div class="summary-card">
          <span class="summary-card__label">需求分析</span>
          <strong class="summary-card__value">{{ project.requirement_summary?.document_count || 0 }}</strong>
          <span class="summary-card__desc">{{ project.requirement_summary?.label }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-card__label">AI 生成</span>
          <strong class="summary-card__value">{{ project.ai_generation_summary?.task_count || 0 }}</strong>
          <span class="summary-card__desc">{{ project.ai_generation_summary?.label }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-card__label">自动化挂接</span>
          <strong class="summary-card__value">预留</strong>
          <span class="summary-card__desc">{{ project.automation_summary?.label }}</span>
        </div>
      </div>

      <div class="project-relation-grid">
        <div class="relation-card">
          <h3>源头对象摘要</h3>
          <ul class="relation-list">
            <li>项目状态：{{ getStatusText(project.status) }}</li>
            <li>负责人：{{ project.owner?.username || '-' }}</li>
            <li>最近更新：{{ formatDate(project.updated_at) }}</li>
            <li>成员数：{{ project.members?.length || 0 }}</li>
            <li>环境数：{{ project.environments?.length || 0 }}</li>
          </ul>
        </div>
        <div class="relation-card">
          <h3>对象关系</h3>
          <ul class="relation-list">
            <li>项目承接需求输入、分析活动与 AI 生成任务。</li>
            <li>生成结果将在“AI 生成用例”里以结果批次继续查看。</li>
            <li>正式测试用例作为设计资产沉淀到测试用例列表与详情页。</li>
          </ul>
        </div>
        <div class="relation-card">
          <h3>下一步入口</h3>
          <div class="relation-actions">
            <el-button type="primary" @click="goToRequirementAnalysis">进入需求分析</el-button>
            <el-button @click="goToGeneratedResults">查看生成结果</el-button>
            <el-button @click="goToTestCases">查看测试用例</el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="card-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane :label="$t('project.projectInfo')" name="info">
          <div v-if="project">
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="$t('project.projectName')">{{ project.name }}</el-descriptions-item>
              <el-descriptions-item :label="$t('project.status')">
                <el-tag :type="getStatusType(project.status)">{{ getStatusText(project.status) }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('project.owner')">{{ project.owner?.username }}</el-descriptions-item>
              <el-descriptions-item :label="$t('project.createdAt')">{{ formatDate(project.created_at) }}</el-descriptions-item>
              <el-descriptions-item :label="$t('project.projectDescription')" :span="2">
                {{ project.description || $t('project.noDescription') }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="$t('project.projectMembers')" name="members">
          <div class="members-section">
            <el-button type="primary" @click="showAddMemberDialog = true">{{ $t('project.addMember') }}</el-button>
            <el-table :data="project?.members || []" style="width: 100%; margin-top: 20px;">
              <el-table-column prop="user.username" :label="$t('project.username')" />
              <el-table-column prop="user.email" :label="$t('project.email')" />
              <el-table-column prop="role" :label="$t('project.role')" />
              <el-table-column prop="joined_at" :label="$t('project.joinedAt')">
                <template #default="{ row }">
                  {{ formatDate(row.joined_at) }}
                </template>
              </el-table-column>
              <el-table-column :label="$t('project.actions')" width="100">
                <template #default="{ row }">
                  <el-button size="small" type="danger" @click="removeMember(row)">{{ $t('common.delete') }}</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="$t('project.environments')" name="environments">
          <div class="environments-section">
            <el-button type="primary" @click="showAddEnvDialog = true">{{ $t('project.addEnvironment') }}</el-button>
            <el-table :data="project?.environments || []" style="width: 100%; margin-top: 20px;">
              <el-table-column prop="name" :label="$t('project.environmentName')" />
              <el-table-column prop="base_url" :label="$t('project.baseUrl')" />
              <el-table-column prop="description" :label="$t('project.description')" />
              <el-table-column prop="is_default" :label="$t('project.defaultEnvironment')">
                <template #default="{ row }">
                  <el-tag v-if="row.is_default" type="success">{{ $t('project.yes') }}</el-tag>
                  <span v-else>{{ $t('project.no') }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'
import { pickAllowedTab, resolveReturnTarget } from '@/router/deeplink'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const project = ref(null)
const PROJECT_DETAIL_TABS = ['info', 'members', 'environments']
const activeTab = ref(pickAllowedTab(route.query.tab, PROJECT_DETAIL_TABS, 'info'))
const showAddMemberDialog = ref(false)
const showAddEnvDialog = ref(false)

const getStatusType = (status) => {
  const typeMap = {
    active: 'success',
    paused: 'warning',
    completed: 'info',
    archived: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    active: t('project.active'),
    paused: t('project.paused'),
    completed: t('project.completed'),
    archived: t('project.archived')
  }
  return textMap[status] || status
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const headerStatusTag = computed(() => {
  if (!project.value?.status) {
    return []
  }

  return [
    {
      label: getStatusText(project.value.status),
      type: getStatusType(project.value.status)
    }
  ]
})

const headerMetaItems = computed(() => {
  if (!project.value) {
    return []
  }

  return [
    { label: '测试用例', value: `${project.value.testcase_count || 0}` },
    { label: '成员数', value: `${project.value.members?.length || 0}` },
    { label: '环境数', value: `${project.value.environments?.length || 0}` },
    { label: '需求输入', value: `${project.value.requirement_summary?.document_count || 0}` },
    { label: '生成任务', value: `${project.value.ai_generation_summary?.task_count || 0}` }
  ]
})

const returnTarget = computed(() => {
  return resolveReturnTarget({
    route,
    fallbackPath: '/ai-generation/projects',
    fallbackTitle: '项目管理'
  })
})

const handleReturn = () => {
  if (returnTarget.value?.path) {
    router.push(returnTarget.value.path)
    return
  }

  router.back()
}

const goToRequirementAnalysis = () => {
  router.push({
    path: '/ai-generation/requirement-analysis',
    query: {
      project: String(project.value?.id || ''),
      projectName: project.value?.name || ''
    }
  })
}

const goToGeneratedResults = () => {
  router.push({
    path: '/ai-generation/generated-testcases',
    query: {
      project: String(project.value?.id || ''),
      projectName: project.value?.name || ''
    }
  })
}

const goToTestCases = () => {
  router.push({
    path: '/ai-generation/testcases',
    query: {
      project: String(project.value?.id || ''),
      projectName: project.value?.name || ''
    }
  })
}

usePlatformPageHeader(() => ({
  title: project.value?.name || '',
  description: project.value?.description || '',
  statusTags: headerStatusTag.value,
  updateText: project.value?.updated_at ? `最近更新 ${formatDate(project.value.updated_at)}` : '',
  helperText: project.value
    ? `项目 ID：${project.value.id}，当前已收口为测试设计源头对象页，可继续跳转需求分析、生成结果和测试用例。`
    : '详情内容仍在页面主体中承接。',
  metaItems: headerMetaItems.value,
  actions: [
    {
      key: 'back',
      label: returnTarget.value?.label || '返回上一步',
      type: 'primary',
      icon: ArrowLeft,
      onClick: handleReturn
    },
    {
      key: 'go-requirement-analysis',
      label: '需求分析',
      plain: true,
      onClick: goToRequirementAnalysis
    },
    {
      key: 'go-testcases',
      label: '测试用例',
      plain: true,
      onClick: goToTestCases
    }
  ]
}))

const fetchProject = async () => {
  try {
    const response = await api.get(`/projects/${route.params.id}/`)
    project.value = response.data
  } catch (error) {
    ElMessage.error(t('project.fetchDetailFailed'))
  }
}

const removeMember = async (member) => {
  try {
    await api.delete(`/projects/${route.params.id}/members/${member.id}/`)
    ElMessage.success(t('project.memberDeleteSuccess'))
    fetchProject()
  } catch (error) {
    ElMessage.error(t('project.memberDeleteFailed'))
  }
}

onMounted(() => {
  fetchProject()
})

watch(
  () => route.query.tab,
  (nextTab) => {
    const resolvedTab = pickAllowedTab(nextTab, PROJECT_DETAIL_TABS, 'info')

    if (resolvedTab !== activeTab.value) {
      activeTab.value = resolvedTab
    }
  }
)

watch(activeTab, (nextTab) => {
  const currentTab = pickAllowedTab(route.query.tab, PROJECT_DETAIL_TABS, 'info')

  if (nextTab === currentTab) {
    return
  }

  const nextQuery = {
    ...route.query
  }

  if (nextTab === 'info') {
    delete nextQuery.tab
  } else {
    nextQuery.tab = nextTab
  }

  router.replace({
    path: route.path,
    query: nextQuery
  })
})
</script>

<style lang="scss" scoped>
.project-object-overview {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}

.project-summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.summary-card,
.relation-card {
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.94) 100%);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 20px;
}

.summary-card__label {
  font-size: 13px;
  color: #64748b;
}

.summary-card__value {
  font-size: 28px;
  line-height: 1;
  color: #0f172a;
}

.summary-card__desc {
  font-size: 13px;
  line-height: 1.6;
  color: #475569;
}

.project-relation-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.relation-card {
  padding: 18px 20px;
}

.relation-card h3 {
  margin: 0 0 12px;
  font-size: 16px;
  color: #0f172a;
}

.relation-list {
  margin: 0;
  padding-left: 18px;
  color: #475569;
  line-height: 1.8;
}

.relation-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.members-section,
.environments-section {
  padding: 20px 0;
}

@media screen and (max-width: 1100px) {
  .project-summary-grid,
  .project-relation-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media screen and (max-width: 768px) {
  .project-summary-grid,
  .project-relation-grid {
    grid-template-columns: 1fr;
  }
}
</style>
