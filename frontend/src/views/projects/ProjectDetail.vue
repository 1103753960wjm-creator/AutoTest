<template>
  <div class="page-container">
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
              <el-descriptions-item :label="$t('project.projectDescription')" :span="2">{{ project.description || $t('project.noDescription') }}</el-descriptions-item>
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
import { computed, ref, onMounted, watch } from 'vue'
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
    { label: '成员数', value: `${project.value.members?.length || 0}` },
    { label: '环境数', value: `${project.value.environments?.length || 0}` }
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

usePlatformPageHeader(() => ({
  title: project.value?.name || '',
  description: project.value?.description || '',
  statusTags: headerStatusTag.value,
  updateText: project.value?.updated_at ? `最近更新 ${formatDate(project.value.updated_at)}` : '',
  helperText: project.value
    ? `项目 ID：${project.value.id}，支持通过 query.tab 精确打开信息、成员和环境页签。`
    : '详情内容仍在页面主体中承接。',
  metaItems: headerMetaItems.value,
  actions: [
    {
      key: 'back',
      label: returnTarget.value?.label || '返回上一步',
      type: 'primary',
      icon: ArrowLeft,
      onClick: handleReturn
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
.members-section,
.environments-section {
  padding: 20px 0;
}
</style>
