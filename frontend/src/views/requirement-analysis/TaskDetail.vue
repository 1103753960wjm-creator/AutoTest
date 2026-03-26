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

    <div class="task-action-bar">
      <button class="secondary-btn" @click="handleReturn">{{ returnTarget.label }}</button>
      <button
        v-if="task.project"
        class="secondary-btn"
        @click="goToProjectCases">
        查看项目测试用例
      </button>
      <button
        v-if="task.task_id"
        class="secondary-btn"
        @click="goToGeneratedResults">
        查看生成结果页
      </button>
      <button
        v-if="taskStatusAllowsCancel"
        class="secondary-btn"
        @click="cancelGenerationTask">
        取消生成
      </button>
      <button
        v-if="testCases.length > 0"
        class="export-btn"
        @click="exportToExcel"
        :disabled="isExporting">
        <span v-if="isExporting">{{ $t('taskDetail.exporting') }}</span>
        <span v-else>{{ $t('taskDetail.exportBtn') }}</span>
      </button>
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
        <span class="task-context-card__label">来源分析说明</span>
        <strong class="task-context-card__value">{{ task.source_analysis_summary?.label || '当前分析上下文摘要' }}</strong>
        <span class="task-context-card__desc">{{ task.source_analysis_summary?.detail || '本轮仅承接来源分析说明，不包装成已真实绑定 analysis 对象。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">模型来源摘要</span>
        <strong class="task-context-card__value">{{ task.model_source_summary?.label || '未记录模型来源' }}</strong>
        <span class="task-context-card__desc">{{ task.model_source_summary?.detail || '优先展示任务记录到的模型信息。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">Prompt 来源摘要</span>
        <strong class="task-context-card__value">{{ task.prompt_source_summary?.label || '未记录 Prompt 来源' }}</strong>
        <span class="task-context-card__desc">{{ task.prompt_source_summary?.detail || '本页优先说明生成链上游来源。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">失败信息摘要</span>
        <strong class="task-context-card__value">{{ task.failure_summary?.label || '当前无失败信息' }}</strong>
        <span class="task-context-card__desc">{{ task.failure_summary?.detail || '失败信息仅做最少可用表达，本轮不展开治理后台。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">下游入口预留</span>
        <strong class="task-context-card__value">{{ task.downstream_summary?.label || '结果层入口预留' }}</strong>
        <span class="task-context-card__desc">{{ task.downstream_summary?.detail || '当前可继续跳往生成结果页或项目测试用例。' }}</span>
      </div>
      <div class="task-context-card">
        <span class="task-context-card__label">AI 自动评审</span>
        <strong class="task-context-card__value">{{ autoReviewSummary.label }}</strong>
        <span class="task-context-card__desc">{{ autoReviewSummary.detail }}</span>
        <button
          v-if="autoReviewSummary.has_record"
          class="asset-btn"
          @click="goToAutoReviews">
          查看 AI 自动评审
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
          <h3>结果预览区</h3>
          <p>本区保留任务下游结果预览与轻量处理，完整结果确认流将在后续阶段继续深化。</p>
          <p v-if="isResultReadonly" class="result-readonly-hint">{{ resultReadonlyHint }}</p>
        </div>
      </div>

      <!-- 批量操作区域 -->
      <div class="batch-actions" v-if="testCases.length > 0">
        <div class="selection-info">
          <label class="select-all">
            <input
              type="checkbox"
              :checked="isAllSelected"
              :disabled="isResultReadonly || selectableCases.length === 0"
              @change="toggleSelectAll">
            {{ $t('taskDetail.selectAll') }}
          </label>
          <span class="selected-count" v-if="selectedCases.length > 0">
            {{ $t('taskDetail.selectedCount', { count: selectedCases.length }) }}
          </span>
        </div>
        <div class="batch-buttons">
          <button
            class="batch-adopt-btn"
            :disabled="isResultReadonly || selectedCases.length === 0"
            @click="batchAdopt">
            {{ $t('taskDetail.batchAdopt', { count: selectedCases.length }) }}
          </button>
          <button
            class="batch-discard-btn"
            :disabled="isResultReadonly || selectedCases.length === 0"
            @click="batchDiscard">
            {{ $t('taskDetail.batchDiscard', { count: selectedCases.length }) }}
          </button>
        </div>
      </div>

      <!-- 测试用例列表 -->
      <div class="testcases-table" v-if="testCases.length > 0">
        <div class="table-header">
          <div class="header-cell checkbox-cell">{{ $t('taskDetail.tableSelect') }}</div>
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
              <input 
                type="checkbox" 
                :value="testCase"
                :disabled="isCaseReadonly(testCase)"
                v-model="selectedCases"
                @change="updateSelectAll">
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
                <span v-if="testCase.result_status === 'adopted'" class="adopted-status">{{ testCase.result_status_label || '已采纳' }}</span>
                <span v-else-if="testCase.result_status === 'discarded'" class="discarded-status">{{ testCase.result_status_label || '已弃用' }}</span>
                <button
                  v-if="testCase.result_status === 'adopted' && testCase.adopted_testcase_id"
                  class="asset-btn"
                  @click="goToAdoptedAsset(testCase)">
                  查看资产
                </button>
                <button v-if="canMutateSingleCase(testCase)" class="adopt-btn" @click="adoptSingleCase(testCase, index)">{{ $t('taskDetail.adopt') }}</button>
                <button v-if="canMutateSingleCase(testCase)" class="discard-btn" @click="discardSingleCase(testCase, index)">{{ $t('taskDetail.discard') }}</button>
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
          <h3>{{ isEditing ? $t('taskDetail.modalEditTitle') : $t('taskDetail.modalViewTitle') }}</h3>
          <button class="close-btn" @click="closeCaseDetail">×</button>
        </div>

        <!-- 查看模式 -->
        <div v-if="!isEditing" class="modal-body">
          <div class="detail-item">
            <label>{{ $t('taskDetail.labelCaseId') }}</label>
            <span>{{ selectedCase.caseId || `TC${String(selectedCaseIndex + 1).padStart(3, '0')}` }}</span>
          </div>
          <div class="detail-item">
            <label>{{ $t('taskDetail.labelScenario') }}</label>
            <p v-html="formatMarkdown(selectedCase.scenario)"></p>
          </div>
          <div class="detail-item">
            <label>{{ $t('taskDetail.labelPrecondition') }}</label>
            <p v-html="formatMarkdown(selectedCase.precondition || $t('taskDetail.labelNone'))"></p>
          </div>
          <div class="detail-item">
            <label>{{ $t('taskDetail.labelSteps') }}</label>
            <p class="test-steps" v-html="formatMarkdown(selectedCase.steps)"></p>
          </div>
          <div class="detail-item">
            <label>{{ $t('taskDetail.labelExpected') }}</label>
            <p v-html="formatMarkdown(selectedCase.expected)"></p>
          </div>
          <div class="detail-item">
            <label>{{ $t('taskDetail.labelPriority') }}</label>
            <span class="priority-tag" :class="selectedCase.priority?.toLowerCase()">{{ selectedCase.priority || 'P2' }}</span>
          </div>
        </div>

        <!-- 编辑模式 -->
        <div v-else class="modal-body edit-mode">
          <div class="form-item">
            <label>{{ $t('taskDetail.labelCaseId') }}</label>
            <span class="readonly-field">{{ editForm.caseId || `TC${String(selectedCaseIndex + 1).padStart(3, '0')}` }}</span>
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelScenario') }}</label>
            <el-input v-model="editForm.scenario" type="textarea" :rows="2" :placeholder="$t('taskDetail.placeholderScenario')" />
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelPrecondition') }}</label>
            <el-input v-model="editForm.precondition" type="textarea" :rows="3" :placeholder="$t('taskDetail.placeholderPrecondition')" />
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelSteps') }}</label>
            <el-input v-model="editForm.steps" type="textarea" :rows="6" :placeholder="$t('taskDetail.placeholderSteps')" />
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelExpected') }}</label>
            <el-input v-model="editForm.expected" type="textarea" :rows="4" :placeholder="$t('taskDetail.placeholderExpected')" />
          </div>
          <div class="form-item">
            <label>{{ $t('taskDetail.labelPriority') }}</label>
            <el-select v-model="editForm.priority" :placeholder="$t('taskDetail.placeholderPriority')">
              <el-option label="P0" value="P0"></el-option>
              <el-option label="P1" value="P1"></el-option>
              <el-option label="P2" value="P2"></el-option>
              <el-option label="P3" value="P3"></el-option>
            </el-select>
          </div>
        </div>

        <!-- 底部操作栏 -->
        <div class="modal-footer">
          <template v-if="!isEditing">
            <button class="action-btn edit-btn" @click="startEdit">
              <span>{{ $t('taskDetail.btnEdit') }}</span>
            </button>
            <button class="action-btn close-btn-footer" @click="closeCaseDetail">{{ $t('taskDetail.btnClose') }}</button>
          </template>
          <template v-else>
            <button class="action-btn save-btn" @click="saveEdit" :disabled="isSaving">
              <span v-if="isSaving">{{ $t('taskDetail.btnSaveing') }}</span>
              <span v-else>{{ $t('taskDetail.btnSave') }}</span>
            </button>
            <button class="action-btn cancel-btn" @click="cancelEdit" :disabled="isSaving">{{ $t('taskDetail.btnCancel') }}</button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentCopy } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import { resolveReturnTarget } from '@/router/deeplink'
import { usePlatformPageHeader } from '@/layout/usePlatformPageHeader'

export default {
  name: 'TaskDetail',
  setup() {
    usePlatformPageHeader(() => ({
      title: '生成任务详情',
      description: '围绕任务来源、配置摘要、状态与失败信息组织 AI 生成链核心对象页。',
      helperText: '本页优先承接任务对象信息，结果区只保留次级承接，不在本轮展开结果确认流。'
    }))
  },
  data() {
    return {
      taskId: '',
      task: {},
      testCases: [],
      selectedCases: [],
      isLoading: true,
      showCaseDetail: false,
      selectedCase: {},
      selectedCaseIndex: 0,
      currentPage: 1,
      pageSize: 10,
      isExporting: false,
      // 编辑相关状态
      isEditing: false,
      isSaving: false,
      pollTimer: null,
      editForm: {
        caseId: '',
        scenario: '',
        precondition: '',
        steps: '',
        expected: '',
        priority: 'P2'
      }
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
        label: '未触发自动评审',
        detail: '当前任务尚未生成自动 AI 评审记录。'
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
        return '当前任务结果已全部进入正式测试用例资产，预览区仅保留查看能力。'
      }
      if (this.processingSummary.discarded_count > 0 && this.processingSummary.pending_count === 0) {
        return '当前任务结果已全部处理完成，其中包含已弃用结果，预览区仅保留查看能力。'
      }
      return '当前任务结果暂无可继续处理的待标记项，预览区仅保留查看能力。'
    },

    selectableCases() {
      return this.testCases.filter(testCase => testCase?.result_status === 'pending')
    },

    isAllSelected() {
      return this.selectableCases.length > 0 && this.selectedCases.length === this.selectableCases.length
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
        this.selectedCases = []
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

    toggleSelectAll() {
      if (this.processingSummary.pending_count === 0) {
        return
      }
      if (this.isAllSelected) {
        this.selectedCases = []
      } else {
        this.selectedCases = [...this.selectableCases]
      }
    },

    updateSelectAll() {
      this.selectedCases = this.selectedCases.filter(testCase => !this.isCaseReadonly(testCase))
    },

    canMutateSingleCase(testCase) {
      return this.taskStatusAllowsResultMutation && testCase?.result_status === 'pending'
    },

    isCaseReadonly(testCase) {
      return !this.canMutateSingleCase(testCase)
    },

    buildCaseSourceTag(testCase, fallbackIndex) {
      return {
        source: 'ai_generation_task',
        task_id: this.taskId,
        project_id: this.task.project || null,
        project_name: this.task.project_name || '',
        case_id: testCase.caseId || testCase.case_id || '',
        case_index: testCase.index ?? fallbackIndex ?? null,
        source_label: '由生成任务详情采纳'
      }
    },

    async batchAdopt() {
      if (!this.taskStatusAllowsResultMutation) {
        ElMessage.warning('当前任务状态不允许继续处理生成结果。')
        return
      }
      if (this.processingSummary.pending_count === 0) {
        ElMessage.warning('当前任务已无可采纳的待处理结果。')
        return
      }
      const pendingCases = this.selectedCases.filter(testCase => testCase?.result_status === 'pending')
      if (pendingCases.length === 0) {
        ElMessage.warning(this.$t('taskDetail.pleaseSelectFirst', { action: this.$t('taskDetail.adopt') }))
        return
      }

      try {
        await ElMessageBox.confirm(
          this.$t('taskDetail.confirmAdopt', { count: pendingCases.length }),
          this.$t('taskDetail.confirmAdoptTitle'),
          {
            confirmButtonText: this.$t('taskDetail.btnConfirm'),
            cancelButtonText: this.$t('taskDetail.btnCancelOperation'),
            type: 'success'
          }
        )
      } catch {
        return
      }

      try {
        const casesData = pendingCases.map((testCase, index) => ({
          title: testCase.scenario || `Test Case ${index + 1}`,
          description: testCase.scenario || '',
          project_id: this.task.project || null,
          preconditions: testCase.precondition || '',
          steps: testCase.steps || '',
          expected_result: testCase.expected || '',
          priority: this.mapPriority(testCase.priority),
          test_type: 'functional',
          status: 'draft',
          case_id: testCase.caseId || testCase.case_id || '',
          case_index: testCase.index ?? index + 1,
          tags: [
            {
              ...this.buildCaseSourceTag(testCase, index + 1),
              source_label: '由生成任务详情批量采纳'
            }
          ]
        }))

        await api.post(`/requirement-analysis/testcase-generation/${this.taskId}/batch-adopt-selected/`, {
          test_cases: casesData
        })

        ElMessage.success(this.$t('taskDetail.adoptSuccess', { count: pendingCases.length }))
        await this.loadTaskDetail()

      } catch (error) {
        console.error('Batch adopt failed:', error)
        if (error.response?.status === 400) {
          await this.loadTaskDetail()
        }
        ElMessage.error(this.$t('taskDetail.batchAdoptFailed') + ': ' + (error.response?.data?.message || error.message))
      }
    },

    async batchDiscard() {
      if (!this.taskStatusAllowsResultMutation) {
        ElMessage.warning('当前任务状态不允许继续处理生成结果。')
        return
      }
      if (this.processingSummary.pending_count === 0) {
        ElMessage.warning('当前任务已无可弃用的待处理结果。')
        return
      }
      const pendingCases = this.selectedCases.filter(testCase => testCase?.result_status === 'pending')
      if (pendingCases.length === 0) {
        ElMessage.warning(this.$t('taskDetail.pleaseSelectFirst', { action: this.$t('taskDetail.discard') }))
        return
      }

      try {
        await ElMessageBox.confirm(
          this.$t('taskDetail.confirmDiscard', { count: pendingCases.length }),
          this.$t('taskDetail.confirmDiscardTitle'),
          {
            confirmButtonText: this.$t('taskDetail.btnConfirm'),
            cancelButtonText: this.$t('taskDetail.btnCancelOperation'),
            type: 'warning',
            confirmButtonClass: 'el-button--danger'
          }
        )
      } catch {
        return
      }

      try {
        const caseIndices = pendingCases
          .map(selectedCase => selectedCase?.index)
          .filter(index => Number.isFinite(index))

        const response = await api.post(`/requirement-analysis/testcase-generation/${this.taskId}/discard-selected-cases/`, {
          case_indices: caseIndices
        })

        ElMessage.success(this.$t('taskDetail.discardSuccess', { count: response.data.discarded_count || pendingCases.length }))
        await this.loadTaskDetail()

      } catch (error) {
        console.error('Batch discard failed:', error)
        if (error.response?.status === 400) {
          await this.loadTaskDetail()
        }
        ElMessage.error(this.$t('taskDetail.batchDiscardFailed') + ': ' + (error.response?.data?.error || error.message))
      }
    },

    viewCaseDetail(testCase, index) {
      this.selectedCase = testCase
      this.selectedCaseIndex = index
      this.showCaseDetail = true
    },

    closeCaseDetail() {
      this.showCaseDetail = false
      this.selectedCase = {}
      this.isEditing = false
      this.editForm = {
        caseId: '',
        scenario: '',
        precondition: '',
        steps: '',
        expected: '',
        priority: 'P2'
      }
    },

    // 开始编辑
    startEdit() {
      if (this.isCaseReadonly(this.selectedCase)) {
        ElMessage.info('当前结果已进入只读状态，请前往正式测试用例资产页继续编辑。')
        return
      }
      this.isEditing = true

      this.editForm = {
        caseId: this.selectedCase.caseId || '',
        scenario: this.selectedCase.scenario || '',
        // 将<br>转换为换行符以便编辑
        precondition: this.convertBrToNewline(this.selectedCase.precondition || ''),
        steps: this.convertBrToNewline(this.selectedCase.steps || ''),
        expected: this.convertBrToNewline(this.selectedCase.expected || ''),
        // 直接使用原始优先级值，不转换
        priority: this.selectedCase.priority || 'P2'
      }
    },

    // 取消编辑
    cancelEdit() {
      this.isEditing = false
      this.editForm = {
        caseId: '',
        scenario: '',
        precondition: '',
        steps: '',
        expected: '',
        priority: 'P2'
      }
    },

    // 保存编辑
    async saveEdit() {
      if (!this.taskStatusAllowsResultMutation) {
        ElMessage.warning('当前任务状态不允许继续编辑生成结果。')
        return
      }
      // 简单验证
      if (!this.editForm.scenario?.trim()) {
        ElMessage.warning(this.$t('taskDetail.enterScenario'))
        return
      }

      this.isSaving = true

      try {
        // 将换行符转换回<br>
        const updatedCase = {
          ...this.selectedCase,
          scenario: this.editForm.scenario,
          precondition: this.convertNewlineToBr(this.editForm.precondition),
          steps: this.convertNewlineToBr(this.editForm.steps),
          expected: this.convertNewlineToBr(this.editForm.expected),
          priority: this.editForm.priority
        }

        // 更新本地数组中的数据
        const index = this.testCases.findIndex(tc => tc === this.selectedCase)
        if (index !== -1) {
          this.testCases[index] = updatedCase
          this.selectedCase = updatedCase
        }

        // 重新生成表格格式的测试用例字符串
        const updatedTestCases = this.generateTestCasesString()

        // 调用后端API保存（使用自定义action接口）
        await api.post(`/requirement-analysis/testcase-generation/${this.taskId}/update-test-cases/`, {
          final_test_cases: updatedTestCases
        })

        // 更新内存中的task数据
        this.task.final_test_cases = updatedTestCases

        ElMessage.success(this.$t('taskDetail.updateSuccess'))
        this.isEditing = false
      } catch (error) {
        console.error('Update failed:', error)
        ElMessage.error(this.$t('taskDetail.updateFailed') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.isSaving = false
      }
    },

    // 将testCases数组重新生成为表格格式的字符串
    generateTestCasesString() {
      if (this.testCases.length === 0) return ''

      // 表头
      const headers = [
        this.$t('taskDetail.tableCaseId'),
        this.$t('taskDetail.tableScenario'),
        this.$t('taskDetail.tablePrecondition'),
        this.$t('taskDetail.tableSteps'),
        this.$t('taskDetail.tableExpected'),
        this.$t('taskDetail.tablePriority')
      ]
      let result = headers.join(' | ') + '\n'
      result += '|'.repeat(headers.length) + '\n'

      // 数据行
      this.testCases.forEach((testCase, index) => {
        const row = [
          testCase.caseId || `TC${String(index + 1).padStart(3, '0')}`,
          testCase.scenario || '',
          testCase.precondition || '',
          testCase.steps || '',
          testCase.expected || '',
          testCase.priority || 'P2'
        ]
        result += row.join(' | ') + '\n'
      })

      return result
    },

    // 将HTML的<br>标签转换为换行符
    convertBrToNewline(text) {
      if (!text) return ''
      return text.replace(/<br\s*\/?>/gi, '\n')
    },

    // 将换行符转换为HTML的<br>标签
    convertNewlineToBr(text) {
      if (!text) return ''
      return text.replace(/\n/g, '<br>')
    },

    async adoptSingleCase(testCase, index) {
      if (!this.taskStatusAllowsResultMutation) {
        ElMessage.warning('当前任务状态不允许继续处理生成结果。')
        return
      }
      if (this.processingSummary.pending_count === 0) {
        ElMessage.warning('当前任务已无可采纳的待处理结果。')
        return
      }
      if (testCase?.is_adopted) {
        ElMessage.info('该生成结果已采纳，请直接查看正式测试资产。')
        return
      }
      if (testCase?.result_status === 'discarded') {
        ElMessage.info('该生成结果已弃用，当前不支持继续采纳。')
        return
      }
      try {
        await ElMessageBox.confirm(
          this.$t('taskDetail.confirmAdoptSingle', { scenario: testCase.scenario }),
          this.$t('taskDetail.confirmAdoptTitle'),
          {
            confirmButtonText: this.$t('taskDetail.btnConfirm'),
            cancelButtonText: this.$t('taskDetail.btnCancelOperation'),
            type: 'success'
          }
        )
      } catch {
        return
      }

      try {
        const caseData = {
          title: testCase.scenario || `测试用例${index + 1}`,
          description: testCase.scenario || '',
          project_id: this.task.project || null,
          preconditions: testCase.precondition || '',
          steps: testCase.steps || '',
          expected_result: testCase.expected || '',
          priority: this.mapPriority(testCase.priority),
          test_type: 'functional',
          status: 'draft',
          tags: [
            this.buildCaseSourceTag(testCase, testCase.index ?? index + 1)
          ]
        }

        const response = await api.post('/testcases/', caseData)
        ElMessage.success(response.data?.deduplicated ? '该结果已采纳，已返回现有测试用例。' : this.$t('taskDetail.adoptSuccess', { count: 1 }))
        await this.loadTaskDetail()

      } catch (error) {
        console.error('Adopt case failed:', error)
        ElMessage.error(this.$t('taskDetail.adoptFailed') + ': ' + (error.response?.data?.message || error.message))
      }
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

    async discardSingleCase(testCase, index) {
      if (!this.taskStatusAllowsResultMutation) {
        ElMessage.warning('当前任务状态不允许继续处理生成结果。')
        return
      }
      if (this.processingSummary.pending_count === 0) {
        ElMessage.warning('当前任务已无可弃用的待处理结果。')
        return
      }
      if (testCase?.result_status === 'adopted') {
        ElMessage.info('已采纳结果不能再弃用。')
        return
      }
      if (testCase?.result_status === 'discarded') {
        ElMessage.info('该生成结果已弃用。')
        return
      }
      try {
        await ElMessageBox.confirm(
          this.$t('taskDetail.confirmDiscardSingle', { scenario: testCase.scenario }),
          this.$t('taskDetail.confirmDiscardTitle'),
          {
            confirmButtonText: this.$t('taskDetail.btnConfirm'),
            cancelButtonText: this.$t('taskDetail.btnCancelOperation'),
            type: 'warning',
            confirmButtonClass: 'el-button--danger'
          }
        )
      } catch {
        return
      }

      try {
        const caseIndex = testCase?.index ?? ((this.currentPage - 1) * this.pageSize + index + 1)
        const response = await api.post(`/requirement-analysis/testcase-generation/${this.taskId}/discard-single-case/`, {
          case_index: caseIndex
        })

        ElMessage.success(response.data?.discarded_count ? this.$t('taskDetail.caseDiscardedSuccess') : '该结果已弃用。')
        await this.loadTaskDetail()

      } catch (error) {
        console.error('Discard case failed:', error)
        if (error.response?.status === 400) {
          await this.loadTaskDetail()
        }
        ElMessage.error(this.$t('taskDetail.discardFailed') + ': ' + (error.response?.data?.error || error.message))
      }
    },

    mapPriority(priority) {
      const priorityMap = {
        '最高': 'critical',
        '高': 'high',
        '中': 'medium',
        '低': 'low',
        'P0': 'critical',
        'P1': 'high',
        'P2': 'medium',
        'P3': 'low'
      }
      return priorityMap[priority] || 'medium'
    },

    // 将英文优先级转换为本地化显示
    priorityToChinese(priority) {
      const priorityMap = {
        'critical': this.$t('generatedTestCases.priorityCritical'),
        'high': this.$t('generatedTestCases.priorityHigh'),
        'medium': this.$t('generatedTestCases.priorityMedium'),
        'low': this.$t('generatedTestCases.priorityLow')
      }
      return priorityMap[priority] || this.$t('generatedTestCases.priorityMedium')
    },

    // 导出到Excel
    exportToExcel() {
      if (this.testCases.length === 0) {
        ElMessage.warning(this.$t('taskDetail.noCasesToExport'))
        return
      }

      this.isExporting = true

      try {
        // 创建工作簿
        const workbook = XLSX.utils.book_new()

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

        // 创建工作表
        const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)

        // 设置列宽
        const colWidths = [
          { wch: 15 }, // 测试用例编号
          { wch: 30 }, // 测试场景
          { wch: 25 }, // 前置条件
          { wch: 50 }, // 操作步骤（增加宽度）
          { wch: 40 }, // 预期结果（增加宽度）
          { wch: 10 }  // 优先级
        ]
        worksheet['!cols'] = colWidths

        // 为所有单元格添加自动换行样式
        const range = XLSX.utils.decode_range(worksheet['!ref'])
        for (let row = range.s.r; row <= range.e.r; row++) {
          for (let col = range.s.c; col <= range.e.c; col++) {
            const cellAddress = XLSX.utils.encode_cell({ r: row, c: col })
            if (!worksheet[cellAddress]) continue
            worksheet[cellAddress].s = {
              alignment: {
                wrapText: true,
                vertical: 'top'
              }
            }
          }
        }

        // 将工作表添加到工作簿
        XLSX.utils.book_append_sheet(workbook, worksheet, this.$t('taskDetail.excelSheetName'))

        // 生成文件名
        const dateStr = new Date().toISOString().slice(0, 10)
        const fileName = this.$t('taskDetail.excelFileName', { taskId: this.taskId, date: dateStr })

        // 导出文件
        XLSX.writeFile(workbook, fileName)

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
