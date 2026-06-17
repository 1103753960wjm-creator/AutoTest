<template>
  <div class="task-detail">
    <div class="task-object-strip">
      <div class="task-object-card">
        <span class="task-object-card__label">任务对象</span>
        <strong class="task-object-card__value">{{ task.task_id || taskId }}</strong>
        <span class="task-object-card__desc">{{ task.title || '当前页面承接生成任务对象摘要。' }}</span>
      </div>
      <div class="task-object-card">
        <span class="task-object-card__label">来源项目</span>
        <strong class="task-object-card__value">{{ currentProjectName }}</strong>
        <span class="task-object-card__desc">{{ task.source_summary?.label || '当前任务未记录来源项目' }}</span>
      </div>
      <div class="task-object-card">
        <span class="task-object-card__label">配置摘要</span>
        <strong class="task-object-card__value">{{ task.generation_config_summary?.name || '当前活跃配置' }}</strong>
        <span class="task-object-card__desc">{{ task.generation_config_summary?.detail || '当前展示任务使用的模型、提示词与生成配置摘要。' }}</span>
      </div>
      <div class="task-object-card">
        <span class="task-object-card__label">结果状态</span>
        <strong class="task-object-card__value">{{ resultCount }}</strong>
        <span class="task-object-card__desc">{{ task.processing_status_summary?.label || '尚未处理' }}</span>
      </div>
    </div>

    <div class="task-status-row" v-if="task.status">
      <span class="task-id">{{ $t('taskDetail.taskId') }}: {{ taskId }}</span>
      <span class="task-status" :class="task.status">{{ getStatusText(task.status) }}</span>
      <span class="task-status-detail">{{ task.writer_model_name || '未记录编写模型' }} / {{ task.writer_prompt_name || '未记录编写提示词' }}</span>
      <span class="task-status-detail">{{ task.reviewer_model_name || '未记录评审模型' }} / {{ task.reviewer_prompt_name || '未记录评审提示词' }}</span>
      <span class="task-status-detail">{{ task.generation_config_summary?.label || '未记录生成配置摘要' }}</span>
    </div>

    <div class="task-context-grid" v-if="task.task_id">
      <div class="task-context-card">
        <span class="task-context-card__label">来源分析摘要</span>
        <strong class="task-context-card__value">{{ task.source_analysis_summary?.label || '当前任务来源分析摘要' }}</strong>
        <span class="task-context-card__desc">{{ task.source_analysis_summary?.detail || '当前页面展示任务生成时关联的来源分析摘要信息，用于说明任务生成背景。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">模型配置信息</span>
        <strong class="task-context-card__value">{{ task.model_source_summary?.label || '未记录模型配置' }}</strong>
        <span class="task-context-card__desc">{{ task.model_source_summary?.detail || '展示本次任务执行时使用的模型配置，用于记录生成依据。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">Prompt 配置信息</span>
        <strong class="task-context-card__value">{{ task.prompt_source_summary?.label || '未记录 Prompt 配置' }}</strong>
        <span class="task-context-card__desc">{{ task.prompt_source_summary?.detail || '展示本次任务执行时使用的提示词配置，用于记录生成依据。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">异常信息摘要</span>
        <strong class="task-context-card__value">{{ task.failure_summary?.label || '当前无异常记录' }}</strong>
        <span class="task-context-card__desc">{{ task.failure_summary?.detail || '当前任务未记录异常信息；如任务执行失败，可在此查看失败摘要与原因说明。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">结果处理入口</span>
        <strong class="task-context-card__value">{{ task.downstream_summary?.label || '结果处理统一入口' }}</strong>
        <span class="task-context-card__desc">{{ task.downstream_summary?.detail || '当前页面提供结果预览与跳转入口；结果确认、采纳与弃用等操作请前往结果批次页面完成。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">AI 自动评审</span>
        <strong class="task-context-card__value">{{ autoReviewSummary.label }}</strong>
        <span class="task-context-card__desc">{{ autoReviewSummary.detail }}</span>
        <button
          v-if="autoReviewSummary.has_record"
          class="asset-btn"
          @click="goToAutoReviews">
          查看自动评审记录
        </button>
      </div>
    </div>

    <div v-if="task.requirement_text" class="requirement-description-card">
      <el-collapse>
        <el-collapse-item name="requirement">
          <template #title>
            <div class="collapse-title">
              <span class="title-text">{{ $t('taskDetail.requirementTitle') }}</span>
              <span class="title-hint">{{ $t('taskDetail.requirementHint') }}</span>
            </div>
          </template>
          <div class="requirement-content">
            <div class="requirement-text">
              {{ task.requirement_text }}
            </div>
            <div class="requirement-actions">
              <el-button size="small" @click="copyRequirementText">
                <el-icon><DocumentCopy /></el-icon>
                {{ $t('taskDetail.copyRequirement') }}
              </el-button>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <div v-if="isLoading" class="loading-state">
      <p>{{ $t('taskDetail.loading') }}</p>
    </div>

    <div v-else-if="!task.task_id" class="error-state">
      <h3>{{ $t('taskDetail.taskNotExist') }}</h3>
      <router-link to="/ai-generation/generated-testcases">{{ $t('taskDetail.backToList') }}</router-link>
    </div>

    <div v-else class="task-content">
      <div class="result-preview-header" v-if="testCases.length > 0">
        <div>
          <h3>结果预览</h3>
          <p>本区域展示当前任务生成结果的预览信息，便于快速查看处理状态。</p>
          <p v-if="isResultReadonly" class="result-readonly-hint">{{ resultReadonlyHint }}</p>
        </div>
      </div>

      <div class="result-handoff-card" v-if="testCases.length > 0">
        <div>
          <span class="result-handoff-card__title">结果处理请前往结果批次页</span>
          <p>当前页面保留任务信息、结果预览及相关说明；正式处理入口已统一放到页头动作区。</p>
        </div>
      </div>

      <!-- 测试用例列表 -->
      <div class="testcases-table" v-if="testCases.length > 0">
        <div class="table-header">
          <div class="header-cell checkbox-cell">处理状态</div>
          <div class="header-cell">{{ $t('taskDetail.tableCaseId') }}</div>
          <div class="header-cell">{{ $t('taskDetail.tableScenario') }}</div>
          <div class="header-cell">{{ $t('taskDetail.tablePrecondition') }}</div>
          <div class="header-cell">{{ $t('taskDetail.tableSteps') }}</div>
          <div class="header-cell">{{ $t('taskDetail.tableExpected') }}</div>
          <div class="header-cell">{{ $t('taskDetail.tablePriority') }}</div>
          <div class="header-cell">{{ $t('taskDetail.tableActions') }}</div>
        </div>
        
        <div class="table-body">
          <div 
            v-for="(testCase, index) in paginatedTestCases" 
            :key="testCase.id || index"
            class="table-row">
            <div class="body-cell checkbox-cell">
              <span
                class="result-status-pill"
                :class="testCase.result_status || 'pending'">
                {{ testCase.result_status_label || '待处理' }}
              </span>
            </div>
            <div class="body-cell">{{ testCase.caseId || `TC${String(index + 1).padStart(3, '0')}` }}</div>
            <div class="body-cell">{{ testCase.scenario }}</div>
            <div class="body-cell text-truncate">
              {{ formatTextForList(testCase.precondition) }}
            </div>
            <div class="body-cell text-truncate">
              {{ formatTextForList(testCase.steps) }}
            </div>
            <div class="body-cell text-truncate">
              {{ formatTextForList(testCase.expected) }}
            </div>
            <div class="body-cell">
              <span class="priority-tag" :class="testCase.priority?.toLowerCase()">{{ testCase.priority || 'P2' }}</span>
            </div>
            <div class="body-cell">
              <div class="action-buttons">
                <button class="view-btn" @click="viewCaseDetail(testCase, index)">{{ $t('taskDetail.viewDetail') }}</button>
                <button
                  v-if="testCase.result_status === 'adopted' && testCase.adopted_testcase_id"
                  class="asset-btn"
                  @click="goToAdoptedAsset(testCase)">
                  查看资产
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <h3>{{ $t('taskDetail.emptyTitle') }}</h3>
        <p>{{ $t('taskDetail.emptyHint') }}</p>
      </div>

      <!-- 分页 -->
      <div v-if="testCases.length > 0" class="pagination-section">
        <div class="pagination-info">
          {{ $t('taskDetail.paginationInfo', { start: paginationStart, end: paginationEnd, total: testCases.length }) }}
        </div>
        <div class="pagination-controls">
          <div class="page-size-selector">
            <label>{{ $t('taskDetail.pageSizeLabel') }}</label>
            <select v-model="pageSize" @change="currentPage = 1">
              <option value="10">{{ $t('taskDetail.pageSizeOption', { size: 10 }) }}</option>
              <option value="20">{{ $t('taskDetail.pageSizeOption', { size: 20 }) }}</option>
              <option value="50">{{ $t('taskDetail.pageSizeOption', { size: 50 }) }}</option>
            </select>
          </div>
          <div class="pagination-buttons">
            <button :disabled="currentPage <= 1" @click="currentPage--">{{ $t('taskDetail.previousPage') }}</button>
            <span class="current-page">{{ $t('taskDetail.currentPageInfo', { current: currentPage, total: totalPages }) }}</span>
            <button :disabled="currentPage >= totalPages" @click="currentPage++">{{ $t('taskDetail.nextPage') }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 用例详情弹窗 -->
    <div v-if="showCaseDetail" class="case-detail-modal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('taskDetail.modalViewTitle') }}</h3>
          <button class="close-btn" @click="closeCaseDetail">×</button>
        </div>

        <div class="modal-body">
          <div class="form-item">
            <label>{{ $t('taskDetail.labelCaseId') }}</label>
            <span class="readonly-field">{{ selectedCase.caseId || `TC${String(selectedCaseIndex + 1).padStart(3, '0')}` }}</span>
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelScenario') }}</label>
            <p v-html="formatMarkdown(selectedCase.scenario)"></p>
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelPrecondition') }}</label>
            <p v-html="formatMarkdown(selectedCase.precondition || $t('taskDetail.labelNone'))"></p>
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelSteps') }}</label>
            <p class="test-steps" v-html="formatMarkdown(selectedCase.steps)"></p>
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelExpected') }}</label>
            <p v-html="formatMarkdown(selectedCase.expected)"></p>
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelPriority') }}</label>
            <span class="priority-tag" :class="selectedCase.priority?.toLowerCase()">{{ selectedCase.priority || 'P2' }}</span>
          </div>
          <div class="detail-handoff-note">
            当前弹窗只保留结果预览。
            如需采纳、弃用或调整这条结果，请前往结果批次页统一处理。
          </div>
        </div>

        <!-- 底部操作栏 -->
        <div class="modal-footer">
          <button
            v-if="selectedCase.result_status === 'adopted' && selectedCase.adopted_testcase_id"
            class="action-btn edit-btn"
            @click="goToAdoptedAsset(selectedCase)">
            查看正式资产
          </button>
          <button class="action-btn save-btn" @click="goToGeneratedResults">
            前往结果批次页
          </button>
          <button class="action-btn close-btn-footer" @click="closeCaseDetail">{{ $t('taskDetail.btnClose') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, getCurrentInstance } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import { ArrowLeft, DocumentCopy, Download } from '@element-plus/icons-vue'
import { exportRowsToExcel } from '@/utils/excelExport'
import { resolveReturnTarget } from '@/router/deeplink'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'

export default {
  name: 'TaskDetail',
  setup() {
    const instance = getCurrentInstance()
    const fallbackReturnTarget = {
      path: '/ai-generation/generated-testcases',
      label: '返回AI生成用例'
    }
    const headerActions = computed(() => {
      const vm = instance?.proxy
      if (!vm) {
        return []
      }

      return [
        {
          key: 'back-source',
          label: vm.returnTarget?.label || fallbackReturnTarget.label,
          type: 'primary',
          icon: ArrowLeft,
          onClick: () => vm.handleReturn()
        },
        vm.task?.project
          ? {
              key: 'view-project-cases',
              label: '查看项目测试用例',
              onClick: () => vm.goToProjectCases()
            }
          : null,
        vm.task?.task_id
          ? {
              key: 'go-generated-results',
              label: '进入结果批次页',
              type: 'primary',
              plain: true,
              onClick: () => vm.goToGeneratedResults()
            }
          : null,
        vm.taskStatusAllowsCancel
          ? {
              key: 'cancel-generation',
              label: '取消生成',
              onClick: () => vm.cancelGenerationTask()
            }
          : null,
        vm.testCases?.length > 0
          ? {
              key: 'export-excel',
              label: vm.isExporting ? vm.$t('taskDetail.exporting') : vm.$t('taskDetail.exportBtn'),
              plain: true,
              icon: Download,
              loading: Boolean(vm.isExporting),
              onClick: () => vm.exportToExcel()
            }
          : null
      ].filter(Boolean)
    })

    usePlatformPageHeader(() => ({
      title: '生成任务详情',
      description: '围绕任务来源、配置摘要、状态与失败信息组织 AI 生成链核心对象页。',
      helperText: '本页聚焦任务对象信息展示，结果区主要用于预览与状态查看；结果处理请前往结果批次页。',
      actions: headerActions.value
    }))
  },
  data() {
    return {
      taskId: '',
      task: {},
      testCases: [],
      isLoading: true,
      showCaseDetail: false,
      selectedCase: {},
      selectedCaseIndex: 0,
      currentPage: 1,
      pageSize: 10,
      isExporting: false,
      pollTimer: null,
    }
  },

  computed: {
    returnTarget() {
      return resolveReturnTarget({
        route: this.$route,
        fallbackPath: '/ai-generation/generated-testcases',
        fallbackTitle: 'AI 生成用例'
      }) || {
        path: '/ai-generation/generated-testcases',
        label: '返回AI生成用例'
      }
    },

    currentProjectName() {
      return this.task.project_name || (this.task.project ? `项目 #${this.task.project}` : '未关联项目')
    },

    resultCount() {
      return this.task.processing_status_summary?.total_count || this.task.result_count || this.testCases.length
    },

    processingSummary() {
      return this.task.processing_status_summary || {
        status: 'pending',
        label: '尚未处理',
        detail: '采纳 0，弃用 0，未标记 0',
        total_count: this.resultCount,
        handled_count: 0,
        adopted_count: 0,
        discarded_count: 0,
        pending_count: this.resultCount
      }
    },

    autoReviewSummary() {
      return this.task.auto_review_summary || {
        has_record: false,
        status: 'not_triggered',
        label: '尚未生成自动评审记录',
        detail: '当前任务尚未生成自动评审记录。'
      }
    },

    taskStatusAllowsCancel() {
      return ['pending', 'generating', 'reviewing', 'revising'].includes(this.task?.status)
    },

    taskStatusAllowsResultMutation() {
      return this.task?.status === 'completed'
    },

    isResultReadonly() {
      return !this.taskStatusAllowsResultMutation || this.processingSummary.pending_count === 0
    },

    resultReadonlyHint() {
      if (this.task?.is_saved_to_records) {
        return '当前任务结果已全部进入正式测试用例资产，本区域仅提供查看功能。'
      }
      if (this.processingSummary.discarded_count > 0 && this.processingSummary.pending_count === 0) {
        return '当前任务结果已完成处理，其中包含已弃用结果；本区域仅提供查看功能。'
      }
      return '当前任务结果暂无可继续处理的待标记项，本区域仅提供查看功能。'
    },

    totalPages() {
      return Math.ceil(this.testCases.length / this.pageSize)
    },

    paginatedTestCases() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.testCases.slice(start, end)
    },

    paginationStart() {
      return (this.currentPage - 1) * this.pageSize + 1
    },

    paginationEnd() {
      return Math.min(this.currentPage * this.pageSize, this.testCases.length)
    }
  },

  mounted() {
    this.taskId = this.$route.params.taskId
    this.loadTaskDetail()
  },

  beforeUnmount() {
    this.stopTaskPolling()
  },

  methods: {
    handleReturn() {
      if (this.returnTarget?.path) {
        this.$router.push(this.returnTarget.path)
        return
      }

      this.$router.back()
    },

    goToProjectCases() {
      this.$router.push({
        path: '/ai-generation/testcases',
        query: {
          project: String(this.task.project || ''),
          projectName: this.task.project_name || '',
          taskId: this.task.task_id || this.taskId,
          from: 'detail',
          fromPath: this.$route.fullPath,
          fromTitle: this.$route.meta?.title || '任务详情',
          fromModule: this.$route.meta?.module || 'test-design'
        }
      })
    },

    goToGeneratedResults() {
      this.$router.push({
        path: '/ai-generation/generated-testcases',
        query: {
          project: String(this.task.project || ''),
          projectName: this.task.project_name || '',
          taskId: this.task.task_id || this.taskId,
          from: 'detail',
          fromPath: this.$route.fullPath,
          fromTitle: this.$route.meta?.title || '任务详情',
          fromModule: this.$route.meta?.module || 'test-design'
        }
      })
    },

    goToAutoReviews() {
      this.$router.push({
        path: '/ai-generation/reviews/ai-auto',
        query: {
          taskId: this.task.task_id || this.taskId,
          project: String(this.task.project || ''),
          from: 'detail',
          fromPath: this.$route.fullPath,
          fromTitle: this.$route.meta?.title || '任务详情',
          fromModule: this.$route.meta?.module || 'test-design'
        }
      })
    },

    async cancelGenerationTask() {
      if (!this.taskStatusAllowsCancel) {
        return
      }

      try {
        await api.post(`/requirement-analysis/testcase-generation/${this.taskId}/cancel/`)
        ElMessage.success('任务已取消')
        await this.loadTaskDetail()
      } catch (error) {
        ElMessage.error(`取消任务失败: ${error.response?.data?.error || error.message}`)
      }
    },

    startTaskPolling() {
      if (!this.taskStatusAllowsCancel || this.pollTimer) {
        return
      }

      this.pollTimer = setInterval(() => {
        this.loadTaskDetail({ silent: true })
      }, 3000)
    },

    stopTaskPolling() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
        this.pollTimer = null
      }
    },

    // 复制需求描述文本
    async copyRequirementText() {
      try {
        await navigator.clipboard.writeText(this.task.requirement_text)
        ElMessage.success(this.$t('taskDetail.copySuccess'))
      } catch (error) {
        // 如果 navigator.clipboard 不可用，使用备用方法
        const textArea = document.createElement('textarea')
        textArea.value = this.task.requirement_text
        textArea.style.position = 'fixed'
        textArea.style.opacity = '0'
        document.body.appendChild(textArea)
        textArea.select()
        try {
          document.execCommand('copy')
          ElMessage.success(this.$t('taskDetail.copySuccess'))
        } catch (err) {
          ElMessage.error(this.$t('taskDetail.copyFailed'))
        }
        document.body.removeChild(textArea)
      }
    },

    async loadTaskDetail({ silent = false } = {}) {
      try {
        const taskResponse = await api.get(`/requirement-analysis/testcase-generation/${this.taskId}/progress/`)
        this.task = taskResponse.data

        if (Array.isArray(this.task.generated_results) && this.task.generated_results.length > 0) {
          this.testCases = this.normalizeTaskCases(this.task.generated_results)
        } else if (this.task.final_test_cases) {
          this.testCases = this.normalizeTaskCases(this.parseTestCases(this.task.final_test_cases))
        } else {
          this.testCases = []
        }
        if (this.taskStatusAllowsCancel) {
          this.startTaskPolling()
        } else {
          this.stopTaskPolling()
        }
      } catch (error) {
        console.error('Failed to load task details:', error)
        if (!silent) {
          ElMessage.error(this.$t('taskDetail.loadFailed'))
        }
      } finally {
        this.isLoading = false
      }
    },

    parseTestCases(content) {
      // 复用RequirementAnalysisView中的解析逻辑
      if (!content) return []

      // 去除markdown加粗标记，保留纯净文本
      let cleanContent = content.replace(/\*\*([^*]+)\*\*/g, '$1')

      const lines = cleanContent.split('\n').filter(line => line.trim())
      const testCases = []

      // 尝试解析表格格式
      let isTableFormat = false
      const tableData = []

      for (let line of lines) {
        const trimmedLine = line.trim()
        if (trimmedLine.includes('|') && !trimmedLine.includes('--------')) {
          const cells = trimmedLine.split('|').map(cell => cell.trim()).filter(cell => cell)
          if (cells.length > 1) {
            tableData.push(cells)
            isTableFormat = true
          }
        }
      }
      
      if (isTableFormat && tableData.length > 1) {
        // 表格格式解析
        const headers = tableData[0]
        for (let i = 1; i < tableData.length; i++) {
          const row = tableData[i]
          const testCase = {}

          // 清理<br>标签的辅助函数
          const cleanBrTags = (text) => {
            if (!text) return ''
            return text.replace(/<br\s*\/?>/gi, '\n')
          }

          headers.forEach((header, index) => {
            const value = cleanBrTags(row[index] || '')

            // 使用更精确的匹配逻辑，避免误判
            const cleanHeader = header.trim().toLowerCase()

            // 优先级匹配，避免误判
            if (cleanHeader === '优先级' || cleanHeader === 'priority' || cleanHeader === 'priority（优先级）' || cleanHeader === '优先级（priority）') {
              testCase.priority = value
            } else if (cleanHeader === '用例id' || cleanHeader === '编号' || cleanHeader === 'id' || cleanHeader.includes('用例id')) {
              testCase.caseId = value
            } else if (cleanHeader === '测试目标' || cleanHeader === '测试场景' || cleanHeader === '场景' || cleanHeader === '标题' || cleanHeader.includes('测试目标')) {
              testCase.scenario = value
            } else if (cleanHeader === '前置条件' || cleanHeader === '前置' || cleanHeader === '前提条件') {
              testCase.precondition = value
            } else if (cleanHeader === '测试步骤' || cleanHeader === '操作步骤' || cleanHeader === '步骤') {
              // 确保不要误匹配"预期结果"中包含的"步骤"字样
              if (!cleanHeader.includes('预期') && !cleanHeader.includes('结果')) {
                testCase.steps = value
              }
            } else if (cleanHeader === '预期结果' || cleanHeader === '预期' || cleanHeader === '结果' || cleanHeader.includes('预期结果')) {
              testCase.expected = value
            }
          })

          if (testCase.scenario || testCase.caseId) {
            // If steps field is empty, use scenario as default
            if (!testCase.steps && testCase.scenario) {
              testCase.steps = testCase.scenario
            }
            // 如果没有priority，设置默认值
            if (!testCase.priority) {
              testCase.priority = 'P2'
            }
            testCases.push(testCase)
          }
        }
      } else {
        // 结构化文本格式解析
        let currentTestCase = {}
        let caseNumber = 1
        
        for (const line of lines) {
          if (line.includes('测试用例') || line.includes('Test Case') || 
              line.match(/^(\d+\.|\*|\-|\d+、)/)) {
            
            if (Object.keys(currentTestCase).length > 0) {
              testCases.push(currentTestCase)
              caseNumber++
            }
            
            currentTestCase = {
              caseId: `TC${String(caseNumber).padStart(3, '0')}`,
              scenario: line.replace(/^(\d+\.|\*|\-|\d+、)\s*/, '').replace(/测试用例\d*[:：]?\s*/, '').replace(/Test Case\s*\d*[:：]?\s*/i, ''),
              precondition: '',
              steps: '',
              expected: '',
              priority: 'P2'
            }
          } else if (line.includes('前置条件') || line.includes('前提')) {
            currentTestCase.precondition = line.replace(/.*?[:：]\s*/, '')
          } else if (line.includes('测试步骤') || line.includes('操作步骤') || line.includes('步骤')) {
            currentTestCase.steps = line.replace(/.*?[:：]\s*/, '')
          } else if (line.includes('预期结果') || line.includes('Expected')) {
            currentTestCase.expected = line.replace(/.*?[:：]\s*/, '')
          } else if (line.includes('优先级')) {
            currentTestCase.priority = line.replace(/.*?[:：]\s*/, '')
          }
        }
        
        if (Object.keys(currentTestCase).length > 0) {
          testCases.push(currentTestCase)
        }
      }
      
      return testCases
    },

    normalizeTaskCases(testCases) {
      return (testCases || []).map((item, index) => ({
        ...item,
        index: Number(item.index || index + 1),
        caseId: item.case_id || item.caseId || '',
        result_status: item.result_status || item.display_status || (item.is_adopted ? 'adopted' : 'pending'),
        result_status_label: item.result_status_label || item.display_status_label || (item.is_adopted ? '已采纳' : '待处理'),
        is_adopted: item.result_status ? item.result_status === 'adopted' : Boolean(item.is_adopted),
        adopted_testcase_id: item.adopted_testcase_id || null,
        display_status: item.display_status || item.result_status || (item.is_adopted ? 'adopted' : 'pending'),
        display_status_label: item.display_status_label || item.result_status_label || (item.is_adopted ? '已采纳' : '待处理')
      }))
    },

    getStatusText(status) {
      if (!status) return ''
      const statusKey = 'status' + status.charAt(0).toUpperCase() + status.slice(1)
      return this.$t('taskDetail.' + statusKey) || status
    },

    // 格式化列表中的文本，将<br>转换为换行
    formatTextForList(text) {
      if (!text) return ''
      // 将<br>、<br/>、<br />等标签替换为换行符
      return text.replace(/<br\s*\/?>/gi, '\n')
    },

    // 格式化文本，去除markdown标记并保留格式
    formatMarkdown(text) {
      if (!text) return ''

      // 先转义HTML标签，防止XSS
      let formatted = text.replace(/&/g, '&amp;')
                         .replace(/</g, '&lt;')
                         .replace(/>/g, '&gt;')

      // 去除markdown加粗标记 **text**，保留纯文本
      formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '$1')

      // 转换换行符为<br>
      formatted = formatted.replace(/\n/g, '<br>')

      return formatted
    },

    viewCaseDetail(testCase, index) {
      this.selectedCase = testCase
      this.selectedCaseIndex = index
      this.showCaseDetail = true
    },

    closeCaseDetail() {
      this.showCaseDetail = false
      this.selectedCase = {}
    },

    goToAdoptedAsset(testCase) {
      if (!testCase?.adopted_testcase_id) {
        return
      }

      this.$router.push({
        path: `/ai-generation/testcases/${testCase.adopted_testcase_id}`,
        query: {
          from: 'detail',
          fromPath: this.$route.fullPath,
          fromTitle: this.$route.meta?.title || '任务详情',
          fromModule: this.$route.meta?.module || 'test-design'
        }
      })
    },

    // 导出到Excel
    async exportToExcel() {
      if (this.testCases.length === 0) {
        ElMessage.warning(this.$t('taskDetail.noCasesToExport'))
        return
      }

      this.isExporting = true

      try {
        // 准备数据
        const worksheetData = []

        // 添加表头
        worksheetData.push([
          this.$t('taskDetail.tableCaseId'),
          this.$t('taskDetail.tableScenario'),
          this.$t('taskDetail.tablePrecondition'),
          this.$t('taskDetail.tableSteps'),
          this.$t('taskDetail.tableExpected'),
          this.$t('taskDetail.tablePriority')
        ])

        // 添加数据行
        this.testCases.forEach((testCase, index) => {
          worksheetData.push([
            testCase.caseId || `TC${String(index + 1).padStart(3, '0')}`,
            testCase.scenario || '',
            this.formatTextForList(testCase.precondition || ''),
            this.formatTextForList(testCase.steps || ''),
            this.formatTextForList(testCase.expected || ''),
            testCase.priority || 'P2'
          ])
        })

        // 设置列宽
        const columns = [
          { width: 15 }, // 测试用例编号
          { width: 30 }, // 测试场景
          { width: 25 }, // 前置条件
          { width: 50 }, // 操作步骤（增加宽度）
          { width: 40 }, // 预期结果（增加宽度）
          { width: 10 }  // 优先级
        ]

        // 生成文件名
        const dateStr = new Date().toISOString().slice(0, 10)
        const fileName = this.$t('taskDetail.excelFileName', { taskId: this.taskId, date: dateStr })

        // 导出文件
        await exportRowsToExcel({
          rows: worksheetData,
          columns,
          sheetName: this.$t('taskDetail.excelSheetName'),
          fileName,
          headerStyle: {
            font: { bold: true },
            alignment: { horizontal: 'center', vertical: 'middle', wrapText: true },
          },
          bodyStyle: {
            alignment: { vertical: 'top', wrapText: true },
          },
        })

        ElMessage.success(this.$t('taskDetail.exportSuccess'))
      } catch (error) {
        console.error('Export Excel failed:', error)
        ElMessage.error(this.$t('taskDetail.exportFailed') + ': ' + (error.message || ''))
      } finally {
        this.isExporting = false
      }
    }
  }
}
</script>

<style scoped>
.task-detail {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 需求描述折叠卡片 */
.requirement-description-card {
  margin-bottom: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  position: relative;
  padding-left: 20px;
}

/* 隐藏左侧可能存在的Element Plus默认箭头 */
.collapse-title::before {
  content: none;
}

.title-icon {
  font-size: 18px;
}

.title-text {
  color: #303133;
  font-weight: 600;
}

.title-hint {
  font-size: 13px;
  color: #909399;
  font-weight: normal;
}

.requirement-content {
  padding: 16px 0;
}

.requirement-text {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 16px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  border-left: 4px solid #409eff;
}

.requirement-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

/* 自定义折叠面板样式 */
.requirement-description-card :deep(.el-collapse) {
  border: none;
}

.requirement-description-card :deep(.el-collapse-item__header) {
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  padding: 16px 20px;
  font-size: 15px;
}

/* 隐藏Element Plus默认的箭头图标 */
.requirement-description-card :deep(.el-collapse-item__header .el-icon) {
  display: none !important;
}

.requirement-description-card :deep(.el-collapse-item__arrow) {
  display: none !important;
}

.requirement-description-card :deep(.el-collapse-item__wrap) {
  border-bottom: none;
}

.requirement-description-card :deep(.el-collapse-item__content) {
  padding: 0 20px 16px;
}

.task-object-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.task-object-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 20px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.94) 100%);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}

.task-object-card__label {
  font-size: 13px;
  color: #64748b;
}

.task-object-card__value {
  font-size: 18px;
  color: #0f172a;
}

.task-object-card__desc {
  font-size: 13px;
  line-height: 1.7;
  color: #475569;
}

.task-action-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.secondary-btn {
  border: 1px solid #cbd5e1;
  background: #fff;
  color: #334155;
  padding: 10px 18px;
  border-radius: 6px;
  cursor: pointer;
}

.task-status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.task-id {
  color: #666;
  font-family: monospace;
}

.task-status {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: bold;
}

.task-status.completed {
  background: #e8f5e8;
  color: #388e3c;
}

.task-status-detail {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
}

.task-context-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.task-context-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px 18px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

.task-context-card__label {
  font-size: 12px;
  color: #64748b;
}

.task-context-card__value {
  font-size: 15px;
  color: #0f172a;
}

.task-context-card__desc {
  font-size: 13px;
  line-height: 1.7;
  color: #475569;
}

.result-preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 18px;
  margin-bottom: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.result-preview-header h3 {
  margin: 0 0 6px;
  font-size: 16px;
  color: #0f172a;
}

.result-preview-header p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #475569;
}

.result-handoff-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  margin-bottom: 16px;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  background: #f8fafc;
}

.result-handoff-card__title {
  display: block;
  margin-bottom: 4px;
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.result-readonly-hint {
  margin-top: 8px !important;
  color: #b45309 !important;
  font-weight: 600;
}

.export-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s ease;
  white-space: nowrap;
}

.export-btn:hover:not(:disabled) {
  background: #229954;
}

.export-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.batch-actions {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.selected-count {
  color: #3498db;
  font-weight: bold;
}

.batch-adopting-hint {
  color: #e67e22;
  font-size: 0.9rem;
}

.batch-buttons {
  display: flex;
  gap: 10px;
}

.batch-adopt-btn, .batch-discard-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.batch-adopt-btn {
  background: #27ae60;
  color: white;
}

.batch-adopt-btn:hover:not(:disabled) {
  background: #229954;
}

.batch-discard-btn {
  background: #e74c3c;
  color: white;
}

.batch-discard-btn:hover:not(:disabled) {
  background: #c0392b;
}

.batch-adopt-btn:disabled, .batch-discard-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.testcases-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table-header {
  display: grid;
  grid-template-columns: 60px 120px 1fr 1fr 1fr 1fr 80px 150px;
  background: #f8f9fa;
  font-weight: bold;
  color: #2c3e50;
}

.table-body .table-row {
  display: grid;
  grid-template-columns: 60px 120px 1fr 1fr 1fr 1fr 80px 150px;
  border-bottom: 1px solid #eee;
  transition: background 0.2s ease;
}

.table-row:hover {
  background: #f8f9fa;
}

.header-cell, .body-cell {
  padding: 16px 8px;
  display: flex;
  align-items: flex-start; /* 改为顶部对齐，避免内容被裁剪 */
  border-right: 1px solid #eee;
  word-break: break-word;
  min-height: 60px;
}

/* 文本截断样式 */
.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  white-space: pre-wrap;
  line-height: 1.6;
  word-break: break-word;
}

.checkbox-cell {
  justify-content: center;
}

.header-cell:last-child, .body-cell:last-child {
  border-right: none;
}

.priority-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.priority-tag.low {
  background: #e8f5e8;
  color: #388e3c;
}

.priority-tag.p3 {
  background: #e8f5e8;
  color: #388e3c;
}

.priority-tag.medium {
  background: #e3f2fd;
  color: #1976d2;
}

.priority-tag.p2 {
  background: #e3f2fd;
  color: #1976d2;
}

.priority-tag.high {
  background: #fff3e0;
  color: #f57c00;
}

.priority-tag.p1 {
  background: #fff3e0;
  color: #f57c00;
}

.priority-tag.critical {
  background: #ffebee;
  color: #d32f2f;
}

.priority-tag.p0 {
  background: #ffebee;
  color: #d32f2f;
}

.action-buttons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.view-btn, .adopt-btn, .discard-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.view-btn {
  background: #3498db;
  color: white;
}

.view-btn:hover {
  background: #2980b9;
}

.adopt-btn {
  background: #27ae60;
  color: white;
}

.adopt-btn:hover {
  background: #229954;
}

.discard-btn {
  background: #e74c3c;
  color: white;
}

.discard-btn:hover {
  background: #c0392b;
}

.asset-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  background: #6366f1;
  color: white;
}

.asset-btn:hover {
  background: #4f46e5;
}

.result-status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 72px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #fef3c7;
  color: #92400e;
  font-size: 12px;
  font-weight: 600;
}

.result-status-pill.adopted {
  background: #dcfce7;
  color: #166534;
}

.result-status-pill.discarded {
  background: #fee2e2;
  color: #b91c1c;
}

.adopted-status {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 999px;
  background: #dcfce7;
  color: #166534;
  font-size: 12px;
  font-weight: 600;
}

.discarded-status {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 999px;
  background: #fee2e2;
  color: #b91c1c;
  font-size: 12px;
  font-weight: 600;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 15px;
}

.pagination-buttons button {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.pagination-buttons button:hover:not(:disabled) {
  background: #f0f0f0;
}

.pagination-buttons button:disabled {
  color: #ccc;
  cursor: not-allowed;
}

@media (max-width: 1100px) {
  .task-object-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .task-object-strip {
    grid-template-columns: 1fr;
  }
}

.case-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 30px;
}

.detail-item {
  margin-bottom: 20px;
}

.detail-item label {
  font-weight: bold;
  color: #2c3e50;
  display: block;
  margin-bottom: 8px;
}

.detail-item span, .detail-item p {
  color: #666;
  line-height: 1.6;
}

.test-steps {
  white-space: pre-line;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #3498db;
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.error-state h3, .empty-state h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.error-state a {
  color: #3498db;
  text-decoration: none;
}

.error-state a:hover {
  text-decoration: underline;
}

/* 编辑模式样式 */
.edit-mode {
  .form-item {
    margin-bottom: 20px;
  }

  .form-item label {
    font-weight: bold;
    color: #2c3e50;
    display: block;
    margin-bottom: 8px;
  }

  .readonly-field {
    color: #666;
    padding: 8px 12px;
    background: #f5f5f5;
    border-radius: 4px;
    display: inline-block;
  }
}

/* 底部操作栏 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 30px;
  border-top: 1px solid #eee;
  background: #f9f9f9;
  border-radius: 0 0 12px 12px;
}

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.edit-btn {
  background: #409eff;
  color: white;
}

.edit-btn:hover {
  background: #66b1ff;
}

.save-btn {
  background: #67c23a;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #85ce61;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  background: #909399;
  color: white;
}

.cancel-btn:hover:not(:disabled) {
  background: #a6a9ad;
}

.close-btn-footer {
  background: #e4e7ed;
  color: #606266;
}

.close-btn-footer:hover {
  background: #ecf5ff;
}
</style>

<style>
/* 全局样式：隐藏Element Plus折叠面板的默认箭头图标 */
.requirement-description-card .el-collapse-item__header .el-icon {
  display: none !important;
}

.requirement-description-card .el-collapse-item__arrow {
  display: none !important;
}

/* 针对Element Plus不同版本的箭头图标 */
.requirement-description-card .el-collapse-item__header .el-collapse-item__arrow {
  display: none !important;
}

.requirement-description-card .el-collapse-item__header .el-icon-arrow-right {
  display: none !important;
}

.requirement-description-card .el-collapse-item__header .el-icon-arrow-left {
  display: none !important;
}
</style>
