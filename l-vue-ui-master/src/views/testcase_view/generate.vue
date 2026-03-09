<script setup lang="ts" name="testcaseGeneratePage">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { MsgSuccess, MsgWarning, NoticeError } from "@/utils/koi.ts";
import { generateTestcases } from "@/api/api_ai/ai.ts";
import { saveReviewedCases } from "@/api/api_requirement/requirement.ts";

const loading = ref(false);
const saveLoading = ref(false);
const tableRef = ref<any>(null);
const caseList = ref<any[]>([]);
const currentCase = ref<any | null>(null);

const resultInfo = ref<any>({
  effective_mode: "",
  configured_mode: "",
  provider: {},
  summary: [],
  generation_source: ""
});

const form = ref({
  title: "",
  source_type: "feature_design",
  target_type: "general",
  content: ""
});

const sourceOptions = [
  { label: "需求文档", value: "requirement_doc" },
  { label: "功能设计", value: "feature_design" },
  { label: "用户故事", value: "user_story" }
];

const targetOptions = [
  { label: "通用", value: "general" },
  { label: "接口", value: "api" },
  { label: "Web", value: "web" },
  { label: "App", value: "app" }
];

const priorityOptions = [
  { label: "P0", value: "P0" },
  { label: "P1", value: "P1" },
  { label: "P2", value: "P2" },
  { label: "P3", value: "P3" }
];

const reviewedCount = computed(() => {
  return caseList.value.filter(item => item.reviewed).length;
});

const buildDraftList = (cases: any[]) => {
  return cases.map((item: any, index: number) => ({
    ...item,
    module: item.module || form.value.title,
    priority: item.priority || "P2",
    preconditions: Array.isArray(item.preconditions) ? item.preconditions.join("\n") : item.preconditions || "",
    steps: Array.isArray(item.steps) ? item.steps.join("\n") : item.steps || "",
    expected_results: Array.isArray(item.expected_results)
      ? item.expected_results.join("\n")
      : item.expected_results || "",
    reviewed: false,
    draft_id: `${item.case_id || "DRAFT"}-${index + 1}`
  }));
};

const clearDrafts = () => {
  resultInfo.value = {
    effective_mode: "",
    configured_mode: "",
    provider: {},
    summary: [],
    generation_source: ""
  };
  caseList.value = [];
  currentCase.value = null;
};

const handleGenerate = async () => {
  if (!form.value.title.trim()) {
    MsgWarning("请输入需求标题");
    return;
  }
  if (!form.value.content.trim()) {
    MsgWarning("请输入需求内容或功能设计说明");
    return;
  }
  try {
    loading.value = true;
    const res: any = await generateTestcases(form.value);
    resultInfo.value = res.data;
    caseList.value = buildDraftList(res.data.cases || []);
    currentCase.value = caseList.value[0] || null;
    MsgSuccess("测试用例草稿生成成功");
  } catch {
    NoticeError("测试用例生成失败，请检查当前模式配置后重试");
  } finally {
    loading.value = false;
  }
};

const handleReset = () => {
  form.value = {
    title: "",
    source_type: "feature_design",
    target_type: "general",
    content: ""
  };
  clearDrafts();
};

const validateBeforeSave = () => {
  if (!reviewedCount.value) {
    MsgWarning("请先至少标记一条已审核用例");
    return false;
  }
  const invalidRow = caseList.value.find(item => {
    if (!item.reviewed) {
      return false;
    }
    return (
      !String(item.module || "").trim() ||
      !String(item.title || "").trim() ||
      !String(item.preconditions || "").trim() ||
      !String(item.steps || "").trim() ||
      !String(item.expected_results || "").trim() ||
      !["P0", "P1", "P2", "P3"].includes(String(item.priority || "").trim())
    );
  });
  if (invalidRow) {
    MsgWarning("已审核用例存在必填字段为空或优先级非法，请先修正");
    return false;
  }
  return true;
};

const handleSaveReviewed = async () => {
  if (!validateBeforeSave()) {
    return;
  }
  try {
    saveLoading.value = true;
    const reviewedCases = caseList.value.filter(item => item.reviewed);
    const res: any = await saveReviewedCases({
      title: form.value.title,
      source_type: form.value.source_type,
      target_type: form.value.target_type,
      content: form.value.content,
      summary: resultInfo.value.summary || [],
      configured_mode: resultInfo.value.configured_mode || "none",
      effective_mode: resultInfo.value.effective_mode || "none",
      provider_name: resultInfo.value.provider?.provider_name || "template_rules",
      cases: reviewedCases.map(item => ({
        case_id: item.case_id,
        title: item.title,
        module: item.module,
        priority: item.priority,
        category: item.category,
        target_type: item.target_type || form.value.target_type,
        automatable: item.automatable,
        reviewed: item.reviewed,
        preconditions: item.preconditions,
        steps: item.steps,
        expected_results: item.expected_results
      }))
    });
    MsgSuccess(`${res.message}，共保存 ${res.data.testcase_count} 条测试用例`);
  } catch {
    NoticeError("保存测试用例失败，请稍后重试");
  } finally {
    saveLoading.value = false;
  }
};

const setReviewedState = (reviewed: boolean) => {
  if (!currentCase.value) {
    MsgWarning("请先选中一条测试用例");
    return;
  }
  currentCase.value.reviewed = reviewed;
  MsgSuccess(reviewed ? "当前用例已标记为已审核" : "当前用例已取消审核");
};

const handleDeleteCurrent = () => {
  if (!currentCase.value) {
    MsgWarning("请先选中一条测试用例");
    return;
  }
  caseList.value = caseList.value.filter(item => item.draft_id !== currentCase.value.draft_id);
  currentCase.value = caseList.value[0] || null;
  MsgSuccess("当前用例已删除");
};

const handleCellClick = ({ row }: any) => {
  currentCase.value = row;
};

const activateCurrentCellEdit = async () => {
  const table = tableRef.value;
  if (!table) {
    return;
  }
  const selected = table.getSelectedCell ? table.getSelectedCell() : null;
  if (selected?.row && selected?.column?.field) {
    await table.setEditCell(selected.row, selected.column.field);
  }
};

const handleKeydown = async (event: KeyboardEvent) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
    event.preventDefault();
    await handleSaveReviewed();
    return;
  }

  if (!caseList.value.length) {
    return;
  }

  if (event.key === "F2" || event.key === "Enter") {
    event.preventDefault();
    await activateCurrentCellEdit();
    return;
  }

  if (event.key === "Escape") {
    const table = tableRef.value;
    if (table?.clearEdit) {
      event.preventDefault();
      await table.clearEdit();
    }
  }
};

onMounted(() => {
  window.addEventListener("keydown", handleKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydown);
});
</script>

<template>
  <div class="koi-flex testcase-generate-page">
    <KoiCard>
      <el-alert
        title="当前页面使用数据网格编辑测试用例草稿。方向键可切换焦点，Enter / F2 进入编辑，Esc 退出编辑，Ctrl + S 一键入库。"
        type="info"
        :closable="false"
        show-icon
      />

      <div class="h-16px"></div>

      <el-form :model="form" label-width="110px">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="24" :md="12">
            <el-form-item label="需求标题">
              <el-input v-model="form.title" placeholder="请输入需求标题或功能名称" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="来源类型">
              <el-select v-model="form.source_type" style="width: 100%">
                <el-option v-for="item in sourceOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="目标类型">
              <el-select v-model="form.target_type" style="width: 100%">
                <el-option v-for="item in targetOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="需求内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="8"
            placeholder="请输入需求文档摘要、功能设计说明或用户故事。"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleGenerate">生成草稿</el-button>
          <el-button plain @click="handleReset">重置输入</el-button>
        </el-form-item>
      </el-form>
    </KoiCard>

    <KoiCard>
      <div class="result-header">
        <div>
          <div class="result-title">测试用例草稿网格</div>
          <div class="result-desc">主编辑区只保留 6 个业务字段，次级信息放在右侧详情区。</div>
        </div>
        <div class="result-tags" v-if="resultInfo.effective_mode">
          <el-tag type="info">配置模式：{{ resultInfo.configured_mode }}</el-tag>
          <el-tag :type="resultInfo.effective_mode === resultInfo.configured_mode ? 'success' : 'warning'">
            实际模式：{{ resultInfo.effective_mode }}
          </el-tag>
          <el-tag>{{ resultInfo.provider?.provider_name || "--" }}</el-tag>
        </div>
      </div>

      <div class="summary-box" v-if="resultInfo.summary?.length">
        <span class="summary-label">需求拆解：</span>
        <el-tag v-for="item in resultInfo.summary" :key="item" class="mr-8px mb-8px">
          {{ item }}
        </el-tag>
      </div>

      <div class="editor-layout" v-loading="loading">
        <div class="editor-grid">
          <vxe-table
            ref="tableRef"
            border
            stripe
            keep-source
            auto-resize
            show-overflow
            :data="caseList"
            :mouse-config="{ selected: true }"
            :keyboard-config="{ isArrow: true, isEnter: true, isEsc: true, isEdit: true }"
            :edit-config="{ trigger: 'click', mode: 'cell', showStatus: true, autoClear: false }"
            @cell-click="handleCellClick"
          >
            <vxe-column field="module" title="所属模块" min-width="160" :edit-render="{ name: 'VxeInput' }" />
            <vxe-column field="title" title="用例标题" min-width="220" :edit-render="{ name: 'VxeInput' }" />
            <vxe-column
              field="preconditions"
              title="前置条件"
              min-width="220"
              :edit-render="{ name: 'VxeTextarea', props: { autosize: { minRows: 3, maxRows: 6 } } }"
            />
            <vxe-column
              field="steps"
              title="测试步骤"
              min-width="260"
              :edit-render="{ name: 'VxeTextarea', props: { autosize: { minRows: 4, maxRows: 8 } } }"
            />
            <vxe-column
              field="expected_results"
              title="预期结果"
              min-width="220"
              :edit-render="{ name: 'VxeTextarea', props: { autosize: { minRows: 3, maxRows: 6 } } }"
            />
            <vxe-column
              field="priority"
              title="优先级"
              width="120"
              :edit-render="{ name: 'VxeSelect', options: priorityOptions }"
            />
          </vxe-table>
        </div>

        <div class="side-panel">
          <el-card shadow="never" class="side-card">
            <template #header>
              <div class="side-card-header">
                <span>次级信息</span>
                <el-tag :type="currentCase?.reviewed ? 'success' : 'info'">
                  {{ currentCase?.reviewed ? "已审核" : "待审核" }}
                </el-tag>
              </div>
            </template>

            <template v-if="currentCase">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="来源编号">{{ currentCase.case_id || "--" }}</el-descriptions-item>
                <el-descriptions-item label="用例类型">{{ currentCase.category || "--" }}</el-descriptions-item>
                <el-descriptions-item label="目标类型">{{ currentCase.target_type || form.target_type }}</el-descriptions-item>
                <el-descriptions-item label="是否可自动化">
                  {{ currentCase.automatable ? "是" : "否" }}
                </el-descriptions-item>
              </el-descriptions>

              <div class="side-actions">
                <el-button type="success" plain @click="setReviewedState(true)">标记当前行为已审核</el-button>
                <el-button plain @click="setReviewedState(false)">取消当前行审核</el-button>
                <el-button type="danger" plain @click="handleDeleteCurrent">删除当前行</el-button>
              </div>
            </template>

            <el-empty v-else description="请先生成草稿并选中一行" />
          </el-card>
        </div>
      </div>
    </KoiCard>

    <div class="save-bar" v-if="caseList.length > 0">
      <div class="save-bar-left">
        <span>总草稿：{{ caseList.length }}</span>
        <span>已审核：{{ reviewedCount }}</span>
      </div>
      <div class="save-bar-right">
        <el-button type="danger" plain @click="clearDrafts">清空全部草稿</el-button>
        <el-button type="primary" :loading="saveLoading" @click="handleSaveReviewed">
          一键入库 (Ctrl + S)
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.testcase-generate-page {
  width: 100%;
  padding-bottom: 88px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.result-title {
  font-size: 18px;
  font-weight: 600;
}

.result-desc {
  margin-top: 4px;
  color: #6b7280;
  font-size: 13px;
}

.result-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.summary-box {
  margin-bottom: 16px;
}

.summary-label {
  margin-right: 8px;
  color: #475569;
}

.editor-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 16px;
}

.editor-grid {
  min-width: 0;
}

.side-panel {
  min-width: 0;
}

.side-card {
  position: sticky;
  top: 0;
}

.side-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.side-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.save-bar {
  position: fixed;
  right: 24px;
  bottom: 20px;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-width: 520px;
  padding: 14px 18px;
  border: 1px solid #dbe4f0;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(12px);
}

.save-bar-left {
  display: flex;
  gap: 16px;
  color: #334155;
  font-weight: 500;
}

.save-bar-right {
  display: flex;
  gap: 12px;
}

@media screen and (max-width: 1100px) {
  .editor-layout {
    grid-template-columns: 1fr;
  }

  .save-bar {
    left: 16px;
    right: 16px;
    min-width: auto;
    flex-direction: column;
    align-items: stretch;
  }

  .save-bar-left,
  .save-bar-right {
    justify-content: space-between;
  }
}
</style>
