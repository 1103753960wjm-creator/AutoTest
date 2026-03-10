<script setup lang="ts" name="testcaseAssetsPage">
import { computed, nextTick, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { MsgBox, MsgSuccess, MsgWarning, NoticeError } from "@/utils/koi.ts";
import { listRequirementPage } from "@/api/api_requirement/requirement.ts";
import {
  batchUpdateTestcases,
  compareTestcaseRevisions,
  exportTestcaseExcel,
  listTestcaseHistory,
  listTestcasePage,
  listTestcaseTags,
  updateReviewStatus,
  updateTestcaseContent
} from "@/api/api_testcase/testcase.ts";

const router = useRouter();
const tableRef = ref<any>();
const loading = ref(false);
const exportLoading = ref(false);
const editLoading = ref(false);
const reviewLoading = ref(false);
const historyLoading = ref(false);
const compareLoading = ref(false);
const batchLoading = ref(false);
const total = ref(0);
const tableData = ref<any[]>([]);
const requirementOptions = ref<any[]>([]);
const tagOptions = ref<any[]>([]);
const selectedRows = ref<any[]>([]);
const editVisible = ref(false);
const reviewVisible = ref(false);
const historyVisible = ref(false);
const batchVisible = ref(false);
const currentRow = ref<any>(null);
const historyData = ref<any>({ testcase: null, revisions: [], review_logs: [] });
const compareForm = ref({ base_revision_id: "", target_revision_id: "" });
const compareResult = ref<any>({ field_diffs: [] });

const searchForm = ref({
  keyword: "",
  requirement_id: "",
  review_status: "",
  target_type: "",
  review_reason_type: "",
  tag_names: [] as string[],
  currentPage: 1,
  pageSize: 10
});

const reviewStatusOptions = [
  { label: "全部状态", value: "" },
  { label: "草稿", value: "draft" },
  { label: "已审核", value: "approved" },
  { label: "已拒绝", value: "rejected" }
];

const targetTypeOptions = [
  { label: "全部类型", value: "" },
  { label: "通用", value: "general" },
  { label: "接口", value: "api" },
  { label: "Web", value: "web" },
  { label: "App", value: "app" }
];
const reviewReasonFilterOptions = [
  { label: "全部原因", value: "" },
  { label: "设计完整", value: "design_complete" },
  { label: "范围清晰", value: "scope_clear" },
  { label: "适合自动化", value: "ready_for_automation" },
  { label: "信息缺失", value: "missing_information" },
  { label: "步骤不清", value: "step_issue" },
  { label: "预期不准确", value: "expected_result_issue" },
  { label: "重复用例", value: "duplicate_case" },
  { label: "其他", value: "other" }
];
const approvedReviewReasonOptions = [
  { label: "设计完整", value: "design_complete" },
  { label: "范围清晰", value: "scope_clear" },
  { label: "适合自动化", value: "ready_for_automation" },
  { label: "其他", value: "other" }
];
const rejectedReviewReasonOptions = [
  { label: "信息缺失", value: "missing_information" },
  { label: "步骤不清", value: "step_issue" },
  { label: "预期不准确", value: "expected_result_issue" },
  { label: "重复用例", value: "duplicate_case" },
  { label: "其他", value: "other" }
];

const priorityOptions = ["P0", "P1", "P2", "P3"];
const automationTargetOptions = [
  { label: "API", value: "api" },
  { label: "Web", value: "web" },
  { label: "App", value: "app" }
];
const batchActionOptions = [
  { label: "批量修改优先级", value: "update_priority" },
  { label: "批量修改目标类型", value: "update_target_type" },
  { label: "批量修改所属模块", value: "update_module" },
  { label: "批量审核", value: "update_review_status" },
  { label: "批量打标签", value: "add_tags" },
  { label: "批量移除标签", value: "remove_tags" }
];

const createEditForm = () => ({
  testcase_id: 0,
  module: "",
  title: "",
  preconditions: "",
  steps: "",
  expected_results: "",
  priority: "P2",
  target_type: "general",
  automatable: false,
  tag_names: [] as string[],
  edit_reason: "手工编辑"
});

const createReviewForm = () => ({
  testcase_id: 0,
  review_status: "approved",
  review_reason_type: "",
  review_comment: ""
});

const createBatchForm = () => ({
  action_type: "update_priority",
  action_payload: {
    priority: "P1",
    target_type: "general",
    module: "",
    review_status: "approved",
    review_reason_type: "",
    review_comment: "",
    tag_names: [] as string[],
    edit_reason: "批量修改"
  }
});

const editForm = ref(createEditForm());
const reviewForm = ref(createReviewForm());
const batchForm = ref(createBatchForm());
const selectedCount = computed(() => selectedRows.value.length);

const buildMultilineText = (value: any) => {
  if (Array.isArray(value)) {
    return value.filter((item: any) => String(item || "").trim()).join("\n");
  }
  return String(value || "").trim();
};

const buildRouteQuery = (query: Record<string, any>) => {
  return Object.keys(query || {}).reduce((result: Record<string, string>, key) => {
    const value = query[key];
    if (value === undefined || value === null || value === "") {
      return result;
    }
    result[key] = String(value);
    return result;
  }, {});
};

const getPriorityTagType = (priority: string) => {
  if (priority === "P0") return "danger";
  if (priority === "P1") return "warning";
  if (priority === "P2") return "success";
  return "info";
};

const getReviewReasonOptions = (reviewStatus: string) => {
  if (reviewStatus === "approved") return approvedReviewReasonOptions;
  if (reviewStatus === "rejected") return rejectedReviewReasonOptions;
  return [];
};

const normalizeReviewReasonValue = (reviewStatus: string, currentValue: string) => {
  const matched = getReviewReasonOptions(reviewStatus).some(item => item.value === currentValue);
  return matched ? currentValue : "";
};

const getAutomationItem = (row: any, targetType: string) => {
  const latestItems = row?.automation_summary?.latest_items || [];
  return latestItems.find((item: any) => item.target_type === targetType) || null;
};

const getAutomationActionLabel = (row: any, targetType: string) => {
  const item = getAutomationItem(row, targetType);
  const label = automationTargetOptions.find(option => option.value === targetType)?.label || targetType;
  if (!item) return `生成${label}草稿`;
  return item.save_status === "saved" ? `继续编辑${label}` : `继续完善${label}`;
};

const syncSelectedRows = () => {
  selectedRows.value = tableRef.value?.getCheckboxRecords?.() || [];
};

const loadRequirementOptions = async () => {
  try {
    const res: any = await listRequirementPage({ currentPage: 1, pageSize: 200, search: {} });
    requirementOptions.value = res.data.content || [];
  } catch {
    requirementOptions.value = [];
  }
};

const loadTagOptions = async (keyword = "") => {
  try {
    const res: any = await listTestcaseTags({ keyword });
    tagOptions.value = res.data || [];
  } catch {
    tagOptions.value = [];
  }
};

const loadTableData = async () => {
  try {
    loading.value = true;
    const res: any = await listTestcasePage({
      currentPage: searchForm.value.currentPage,
      pageSize: searchForm.value.pageSize,
      search: {
        keyword: searchForm.value.keyword,
        requirement_id: searchForm.value.requirement_id,
        review_status: searchForm.value.review_status,
        target_type: searchForm.value.target_type,
        review_reason_type: searchForm.value.review_reason_type,
        tag_names: searchForm.value.tag_names
      }
    });
    tableData.value = (res.data.content || []).map((item: any, index: number) => ({
      ...item,
      seq: (searchForm.value.currentPage - 1) * searchForm.value.pageSize + index + 1,
      preconditions_display: item.preconditions_text || buildMultilineText(item.preconditions),
      steps_display: item.steps_text || buildMultilineText(item.steps),
      expected_results_display: item.expected_results_text || buildMultilineText(item.expected_results)
    }));
    total.value = res.data.total || 0;
    selectedRows.value = [];
    await nextTick();
    tableRef.value?.clearCheckboxRow?.();
  } catch {
    NoticeError("测试用例列表加载失败，请稍后重试");
  } finally {
    loading.value = false;
  }
};

const handleSearch = async () => {
  searchForm.value.currentPage = 1;
  await loadTableData();
};

const handleReset = async () => {
  searchForm.value = {
    keyword: "",
    requirement_id: "",
    review_status: "",
    target_type: "",
    review_reason_type: "",
    tag_names: [],
    currentPage: 1,
    pageSize: 10
  };
  await loadTableData();
};

const openEditDrawer = (row: any) => {
  currentRow.value = row;
  editForm.value = {
    testcase_id: row.id,
    module: row.module || "",
    title: row.title || "",
    preconditions: row.preconditions_display || "",
    steps: row.steps_display || "",
    expected_results: row.expected_results_display || "",
    priority: row.priority || "P2",
    target_type: row.target_type || "general",
    automatable: Boolean(row.automatable),
    tag_names: row.tag_names || [],
    edit_reason: "手工编辑"
  };
  editVisible.value = true;
};

const submitEdit = async () => {
  if (!editForm.value.module.trim() || !editForm.value.title.trim()) {
    NoticeError("所属模块和用例标题不能为空");
    return;
  }
  if (!editForm.value.preconditions.trim() || !editForm.value.steps.trim() || !editForm.value.expected_results.trim()) {
    NoticeError("前置条件、测试步骤、预期结果不能为空");
    return;
  }
  if (currentRow.value?.automation_summary?.latest_draft_count > 0 || currentRow.value?.automation_risk?.has_risk) {
    try {
      await MsgBox("当前测试用例已关联自动化草稿，保存后请人工确认脚本是否需要同步调整。是否继续保存？", "自动化风险提示");
    } catch {
      return;
    }
  }
  try {
    editLoading.value = true;
    await updateTestcaseContent(editForm.value);
    MsgSuccess("测试用例保存成功");
    editVisible.value = false;
    await Promise.all([loadTagOptions(), loadTableData()]);
  } catch {
    NoticeError("测试用例保存失败，请稍后重试");
  } finally {
    editLoading.value = false;
  }
};

const openReviewDialog = (row: any) => {
  currentRow.value = row;
  reviewForm.value = {
    testcase_id: row.id,
    review_status: row.review_status || "approved",
    review_reason_type: row.latest_review_reason_type || "",
    review_comment: row.latest_review_comment || ""
  };
  reviewVisible.value = true;
};

const handleReviewStatusChange = (value: string) => {
  reviewForm.value.review_reason_type = normalizeReviewReasonValue(value, reviewForm.value.review_reason_type);
};

const handleBatchReviewStatusChange = (value: string) => {
  batchForm.value.action_payload.review_reason_type = normalizeReviewReasonValue(
    value,
    batchForm.value.action_payload.review_reason_type
  );
};

const submitReview = async () => {
  if (reviewForm.value.review_status !== "draft" && !reviewForm.value.review_reason_type) {
    NoticeError("请选择审核原因类型");
    return;
  }
  if (reviewForm.value.review_status === "rejected" && !reviewForm.value.review_comment.trim()) {
    NoticeError("驳回测试用例时必须填写驳回原因");
    return;
  }
  try {
    reviewLoading.value = true;
    const payload = {
      ...reviewForm.value,
      review_reason_type: reviewForm.value.review_status === "draft" ? "" : reviewForm.value.review_reason_type
    };
    await updateReviewStatus(payload);
    MsgSuccess("审核状态更新成功");
    reviewVisible.value = false;
    await loadTableData();
  } catch {
    NoticeError("审核状态更新失败，请稍后重试");
  } finally {
    reviewLoading.value = false;
  }
};

const openHistoryDrawer = async (row: any) => {
  try {
    historyLoading.value = true;
    historyVisible.value = true;
    historyData.value = { testcase: row, revisions: [], review_logs: [] };
    compareForm.value = { base_revision_id: "", target_revision_id: "" };
    compareResult.value = { field_diffs: [] };
    const res: any = await listTestcaseHistory({ testcase_id: row.id });
    historyData.value = res.data || historyData.value;
    if ((historyData.value.revisions || []).length >= 2) {
      compareForm.value = {
        base_revision_id: historyData.value.revisions[1].id,
        target_revision_id: historyData.value.revisions[0].id
      };
      await loadCompareResult();
    }
  } catch {
    NoticeError("历史记录加载失败，请稍后重试");
  } finally {
    historyLoading.value = false;
  }
};

const loadCompareResult = async () => {
  if (!historyData.value?.testcase?.id) return;
  if (!compareForm.value.base_revision_id || !compareForm.value.target_revision_id) {
    NoticeError("请选择两个版本进行对比");
    return;
  }
  if (compareForm.value.base_revision_id === compareForm.value.target_revision_id) {
    NoticeError("请选择两个不同的版本");
    return;
  }
  try {
    compareLoading.value = true;
    const res: any = await compareTestcaseRevisions({
      testcase_id: historyData.value.testcase.id,
      base_revision_id: compareForm.value.base_revision_id,
      target_revision_id: compareForm.value.target_revision_id
    });
    compareResult.value = res.data || { field_diffs: [] };
  } catch {
    NoticeError("版本对比加载失败，请稍后重试");
  } finally {
    compareLoading.value = false;
  }
};

const openBatchDialog = () => {
  if (!selectedRows.value.length) {
    NoticeError("请至少选择一条测试用例");
    return;
  }
  batchForm.value = createBatchForm();
  batchVisible.value = true;
};

const submitBatch = async () => {
  if (batchForm.value.action_type === "update_module" && !batchForm.value.action_payload.module.trim()) {
    NoticeError("请输入新的所属模块");
    return;
  }
  if ((batchForm.value.action_type === "add_tags" || batchForm.value.action_type === "remove_tags") && !batchForm.value.action_payload.tag_names.length) {
    NoticeError(batchForm.value.action_type === "add_tags" ? "请至少输入一个标签" : "请至少选择一个待移除标签");
    return;
  }
  if (batchForm.value.action_type === "update_review_status" && batchForm.value.action_payload.review_status !== "draft" && !batchForm.value.action_payload.review_reason_type) {
    NoticeError("请选择审核原因类型");
    return;
  }
  if (batchForm.value.action_type === "update_review_status" && batchForm.value.action_payload.review_status === "rejected" && !batchForm.value.action_payload.review_comment.trim()) {
    NoticeError("批量驳回时必须填写驳回原因");
    return;
  }
  try {
    await MsgBox(`本次将批量处理 ${selectedRows.value.length} 条测试用例，是否继续？`, "批量修改确认");
  } catch {
    return;
  }
  try {
    batchLoading.value = true;
    const res: any = await batchUpdateTestcases({
      testcase_ids: selectedRows.value.map((item: any) => item.id),
      action_type: batchForm.value.action_type,
      action_payload: {
        ...batchForm.value.action_payload,
        review_reason_type: batchForm.value.action_type === "update_review_status" && batchForm.value.action_payload.review_status === "draft"
          ? ""
          : batchForm.value.action_payload.review_reason_type
      }
    });
    const data = res.data || {};
    if (data.failed_count > 0) {
      MsgWarning(`批量处理完成，成功 ${data.success_count} 条，失败 ${data.failed_count} 条`);
    } else {
      MsgSuccess(`批量处理成功，共更新 ${data.success_count} 条测试用例`);
    }
    batchVisible.value = false;
    await Promise.all([loadTagOptions(), loadTableData()]);
  } catch {
    NoticeError("批量处理失败，请稍后重试");
  } finally {
    batchLoading.value = false;
  }
};

const resolveDownloadName = (headers: Record<string, any>) => {
  const disposition = headers?.["content-disposition"] || "";
  const match = disposition.match(/filename\*=UTF-8''([^;]+)/i);
  return match?.[1] ? decodeURIComponent(match[1]) : "测试用例.xls";
};

const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

const handleExport = async () => {
  try {
    exportLoading.value = true;
    const res: any = await exportTestcaseExcel({
      search: {
        keyword: searchForm.value.keyword,
        requirement_id: searchForm.value.requirement_id,
        review_status: searchForm.value.review_status,
        target_type: searchForm.value.target_type,
        review_reason_type: searchForm.value.review_reason_type,
        tag_names: searchForm.value.tag_names
      }
    });
    downloadBlob(res.data, resolveDownloadName(res.headers || {}));
    MsgSuccess("测试用例导出成功");
  } catch {
    NoticeError("测试用例导出失败，请稍后重试");
  } finally {
    exportLoading.value = false;
  }
};

const openDraftByQuery = async (query: Record<string, any>) => {
  await router.push({ path: "/automation_draft", query: buildRouteQuery(query) });
};

const handleAutomationAction = async (row: any, targetType: string) => {
  const existingItem = getAutomationItem(row, targetType);
  if (existingItem?.draft_id) {
    await openDraftByQuery({ testcase_id: row.id, target_type: targetType, draft_id: existingItem.draft_id });
    return;
  }
  if (row.review_status !== "approved") {
    NoticeError("只有已审核测试用例才允许生成自动化草稿");
    return;
  }
  await openDraftByQuery({ testcase_id: row.id, target_type: targetType });
};

const viewTargetAsset = async (item: any) => {
  if (!item?.target_route || !item?.target_route_query) {
    NoticeError("当前草稿还没有可跳转的目标资产");
    return;
  }
  await router.push({ path: item.target_route, query: buildRouteQuery(item.target_route_query || {}) });
};

onMounted(async () => {
  await Promise.all([loadRequirementOptions(), loadTagOptions(), loadTableData()]);
});
</script>

<template>
  <div class="testcase-assets-page">
    <KoiCard>
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" clearable placeholder="用例标题 / 模块 / 审核意见" />
        </el-form-item>
        <el-form-item label="所属需求">
          <el-select v-model="searchForm.requirement_id" clearable filterable style="width: 220px">
            <el-option v-for="item in requirementOptions" :key="item.id" :label="item.title" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="searchForm.review_status" clearable style="width: 140px">
            <el-option v-for="item in reviewStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标类型">
          <el-select v-model="searchForm.target_type" clearable style="width: 140px">
            <el-option v-for="item in targetTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核原因">
          <el-select v-model="searchForm.review_reason_type" clearable style="width: 180px">
            <el-option v-for="item in reviewReasonFilterOptions" :key="item.value || 'all'" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签筛选">
          <el-select v-model="searchForm.tag_names" multiple collapse-tags collapse-tags-tooltip clearable filterable style="width: 260px" placeholder="选择标签">
            <el-option v-for="item in tagOptions" :key="item.id" :label="item.name" :value="item.name" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button plain @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar-row">
        <div class="toolbar-left">
          <el-tag type="info" effect="plain">已选 {{ selectedCount }} 条</el-tag>
          <el-button plain @click="openBatchDialog">批量修改</el-button>
        </div>
        <el-button type="warning" plain :loading="exportLoading" @click="handleExport">导出 Excel</el-button>
      </div>

      <vxe-table
        ref="tableRef"
        v-loading="loading"
        border
        stripe
        auto-resize
        :data="tableData"
        :row-config="{ keyField: 'id', isHover: true }"
        :checkbox-config="{ highlight: true }"
        class="asset-table"
        @checkbox-change="syncSelectedRows"
        @checkbox-all="syncSelectedRows"
      >
        <vxe-column type="checkbox" width="54" fixed="left" />
        <vxe-column field="seq" title="序号" width="80" fixed="left" align="center" />
        <vxe-column field="module" title="所属模块" min-width="160" />
        <vxe-column field="title" title="用例标题" min-width="260">
          <template #default="{ row }">
            <div class="title-cell">
              <div class="title-main">{{ row.title || "--" }}</div>
              <div class="title-meta">
                <el-tag size="small" effect="plain">{{ row.review_status_label || "草稿" }}</el-tag>
                <span>{{ row.requirement_title || "未关联需求" }}</span>
                <span>{{ row.category_label || "通用" }}</span>
                <span>{{ row.target_type_label || "通用" }}</span>
                <span v-if="row.latest_review_reason_type_label">审核原因：{{ row.latest_review_reason_type_label }}</span>
              </div>
              <div v-if="row.tag_names?.length" class="tag-summary">
                <el-tag v-for="tagName in row.tag_names" :key="`${row.id}-${tagName}`" size="small" effect="plain" type="success">{{ tagName }}</el-tag>
              </div>
              <div v-if="row.automation_risk?.has_risk" class="title-risk">{{ row.automation_risk.message }}</div>
            </div>
          </template>
        </vxe-column>
        <vxe-column field="preconditions_display" title="前置条件" min-width="220">
          <template #default="{ row }"><div class="multiline-cell">{{ row.preconditions_display || "--" }}</div></template>
        </vxe-column>
        <vxe-column field="steps_display" title="测试步骤" min-width="240">
          <template #default="{ row }"><div class="multiline-cell">{{ row.steps_display || "--" }}</div></template>
        </vxe-column>
        <vxe-column field="expected_results_display" title="预期结果" min-width="240">
          <template #default="{ row }"><div class="multiline-cell">{{ row.expected_results_display || "--" }}</div></template>
        </vxe-column>
        <vxe-column field="priority" title="优先级" width="100" align="center">
          <template #default="{ row }"><el-tag size="small" :type="getPriorityTagType(row.priority)">{{ row.priority }}</el-tag></template>
        </vxe-column>
        <vxe-column title="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="operation-cell">
              <div class="operation-row">
                <el-button link type="primary" @click="openEditDrawer(row)">编辑</el-button>
                <el-button link type="primary" @click="openReviewDialog(row)">审核</el-button>
                <el-button link type="primary" @click="openHistoryDrawer(row)">历史</el-button>
              </div>
              <div class="operation-row">
                <el-dropdown @command="(command: string) => handleAutomationAction(row, command)">
                  <el-button link type="success">自动化</el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item v-for="target in automationTargetOptions" :key="`${row.id}-${target.value}`" :command="target.value">
                        {{ getAutomationActionLabel(row, target.value) }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <span class="operation-note">草稿 {{ row.automation_summary?.latest_draft_count || 0 }} 个</span>
              </div>
            </div>
          </template>
        </vxe-column>
      </vxe-table>

      <div class="pager-wrapper">
        <el-pagination
          v-model:current-page="searchForm.currentPage"
          v-model:page-size="searchForm.pageSize"
          background
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadTableData"
          @size-change="handleSearch"
        />
      </div>
    </KoiCard>

    <el-drawer v-model="editVisible" size="56%" title="编辑测试用例">
      <el-alert v-if="currentRow?.automation_summary?.latest_draft_count > 0 || currentRow?.automation_risk?.has_risk" type="warning" :closable="false" show-icon class="drawer-alert" :title="currentRow?.automation_risk?.message || '当前测试用例已关联自动化草稿，保存后请人工确认脚本是否需要同步调整'" />
      <el-form label-width="100px" class="form-grid">
        <el-form-item label="所属模块"><el-input v-model="editForm.module" maxlength="128" /></el-form-item>
        <el-form-item label="用例标题"><el-input v-model="editForm.title" maxlength="255" /></el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="editForm.priority" style="width: 100%">
            <el-option v-for="item in priorityOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标类型">
          <el-select v-model="editForm.target_type" style="width: 100%">
            <el-option v-for="item in targetTypeOptions.filter(option => option.value)" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="可自动化"><el-switch v-model="editForm.automatable" /></el-form-item>
        <el-form-item label="编辑原因"><el-input v-model="editForm.edit_reason" maxlength="255" /></el-form-item>
        <el-form-item label="标签" class="full-width">
          <el-select
            v-model="editForm.tag_names"
            multiple
            filterable
            allow-create
            default-first-option
            clearable
            style="width: 100%"
            placeholder="输入或选择标签"
          >
            <el-option v-for="item in tagOptions" :key="item.id" :label="item.name" :value="item.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="前置条件" class="full-width"><el-input v-model="editForm.preconditions" type="textarea" :rows="5" /></el-form-item>
        <el-form-item label="测试步骤" class="full-width"><el-input v-model="editForm.steps" type="textarea" :rows="6" /></el-form-item>
        <el-form-item label="预期结果" class="full-width"><el-input v-model="editForm.expected_results" type="textarea" :rows="5" /></el-form-item>
      </el-form>
      <div class="drawer-footer">
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="submitEdit">保存</el-button>
      </div>
    </el-drawer>

    <el-dialog v-model="reviewVisible" width="520px" title="审核测试用例">
      <el-form label-width="100px">
        <el-form-item label="审核状态">
          <el-select v-model="reviewForm.review_status" style="width: 100%" @change="handleReviewStatusChange">
            <el-option v-for="item in reviewStatusOptions.filter(option => option.value)" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="reviewForm.review_status !== 'draft'" label="原因类型">
          <el-select v-model="reviewForm.review_reason_type" clearable style="width: 100%" placeholder="请选择审核原因类型">
            <el-option
              v-for="item in getReviewReasonOptions(reviewForm.review_status)"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="reviewForm.review_status === 'rejected' ? '驳回原因' : '审核意见'">
          <el-input v-model="reviewForm.review_comment" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" :loading="reviewLoading" @click="submitReview">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="batchVisible" width="560px" title="批量修改测试用例">
      <el-alert type="info" :closable="false" class="drawer-alert" :title="`本次将批量处理 ${selectedCount} 条测试用例`" />
      <el-form label-width="110px">
        <el-form-item label="操作类型">
          <el-select v-model="batchForm.action_type" style="width: 100%">
            <el-option v-for="item in batchActionOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="batchForm.action_type === 'update_priority'" label="新优先级">
          <el-select v-model="batchForm.action_payload.priority" style="width: 100%">
            <el-option v-for="item in priorityOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="batchForm.action_type === 'update_target_type'" label="新目标类型">
          <el-select v-model="batchForm.action_payload.target_type" style="width: 100%">
            <el-option v-for="item in targetTypeOptions.filter(option => option.value)" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="batchForm.action_type === 'update_module'" label="新所属模块"><el-input v-model="batchForm.action_payload.module" maxlength="128" /></el-form-item>
        <template v-if="batchForm.action_type === 'update_review_status'">
          <el-form-item label="审核状态">
            <el-select v-model="batchForm.action_payload.review_status" style="width: 100%" @change="handleBatchReviewStatusChange">
              <el-option v-for="item in reviewStatusOptions.filter(option => option.value)" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="batchForm.action_payload.review_status !== 'draft'" label="原因类型">
            <el-select v-model="batchForm.action_payload.review_reason_type" clearable style="width: 100%" placeholder="请选择审核原因类型">
              <el-option
                v-for="item in getReviewReasonOptions(batchForm.action_payload.review_status)"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="batchForm.action_payload.review_status === 'rejected' ? '驳回原因' : '审核意见'"><el-input v-model="batchForm.action_payload.review_comment" type="textarea" :rows="4" /></el-form-item>
        </template>
        <el-form-item v-if="batchForm.action_type === 'add_tags' || batchForm.action_type === 'remove_tags'" label="标签">
          <el-select
            v-model="batchForm.action_payload.tag_names"
            multiple
            filterable
            allow-create
            default-first-option
            clearable
            style="width: 100%"
            placeholder="输入或选择标签"
          >
            <el-option v-for="item in tagOptions" :key="item.id" :label="item.name" :value="item.name" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="batchForm.action_type !== 'update_review_status'" label="修改原因"><el-input v-model="batchForm.action_payload.edit_reason" maxlength="255" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchVisible = false">取消</el-button>
        <el-button type="primary" :loading="batchLoading" @click="submitBatch">确认执行</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="historyVisible" size="62%" title="测试用例历史">
      <div v-loading="historyLoading" class="history-drawer">
        <template v-if="historyData.testcase">
            <el-descriptions border :column="2">
              <el-descriptions-item label="所属模块">{{ historyData.testcase.module || "--" }}</el-descriptions-item>
              <el-descriptions-item label="用例标题">{{ historyData.testcase.title || "--" }}</el-descriptions-item>
              <el-descriptions-item label="优先级">{{ historyData.testcase.priority || "--" }}</el-descriptions-item>
              <el-descriptions-item label="用例类型">{{ historyData.testcase.category_label || "--" }}</el-descriptions-item>
              <el-descriptions-item label="目标类型">{{ historyData.testcase.target_type_label || "--" }}</el-descriptions-item>
              <el-descriptions-item label="审核状态">{{ historyData.testcase.review_status_label || "--" }}</el-descriptions-item>
              <el-descriptions-item label="审核原因">{{ historyData.testcase.latest_review_reason_type_label || "--" }}</el-descriptions-item>
              <el-descriptions-item label="所属需求">{{ historyData.testcase.requirement_title || "--" }}</el-descriptions-item>
              <el-descriptions-item label="版本号">V{{ historyData.testcase.version || 1 }}</el-descriptions-item>
              <el-descriptions-item label="标签" :span="2">
                <div v-if="historyData.testcase.tag_names?.length" class="tag-summary">
                  <el-tag
                    v-for="tagName in historyData.testcase.tag_names"
                    :key="`history-tag-${tagName}`"
                    size="small"
                    effect="plain"
                    type="success"
                  >
                    {{ tagName }}
                  </el-tag>
                </div>
                <span v-else>--</span>
              </el-descriptions-item>
              <el-descriptions-item label="最新审核意见" :span="2">{{ historyData.testcase.latest_review_comment || "--" }}</el-descriptions-item>
            </el-descriptions>

          <div class="summary-panel">
            <div v-for="target in automationTargetOptions" :key="`history-${target.value}`" class="summary-card">
              <div class="summary-card-title">{{ target.label }}</div>
              <div class="summary-card-status">
                {{ getAutomationItem(historyData.testcase, target.value)?.save_status === "saved" ? "已保存" : getAutomationItem(historyData.testcase, target.value) ? "草稿中" : "未生成" }}
              </div>
              <div class="summary-card-actions">
                <el-button link type="primary" @click="handleAutomationAction(historyData.testcase, target.value)">{{ getAutomationActionLabel(historyData.testcase, target.value) }}</el-button>
                <el-button v-if="getAutomationItem(historyData.testcase, target.value)?.target_route" link type="success" @click="viewTargetAsset(getAutomationItem(historyData.testcase, target.value))">查看资产</el-button>
              </div>
            </div>
          </div>

            <el-tabs>
              <el-tab-pane label="版本快照">
                <div class="compare-panel">
                  <div class="compare-toolbar">
                    <el-select v-model="compareForm.base_revision_id" :disabled="historyData.revisions.length < 2" placeholder="选择基准版本" style="width: 180px">
                      <el-option v-for="item in historyData.revisions" :key="`base-${item.id}`" :label="`V${item.version}`" :value="item.id" />
                    </el-select>
                    <el-select v-model="compareForm.target_revision_id" :disabled="historyData.revisions.length < 2" placeholder="选择对比版本" style="width: 180px">
                      <el-option v-for="item in historyData.revisions" :key="`target-${item.id}`" :label="`V${item.version}`" :value="item.id" />
                    </el-select>
                    <el-button type="primary" plain :disabled="historyData.revisions.length < 2" :loading="compareLoading" @click="loadCompareResult">对比版本</el-button>
                  </div>
                  <el-alert v-if="historyData.revisions.length < 2" type="info" :closable="false" title="至少需要两个历史版本才能进行对比" />
                  <div v-else class="compare-result">
                    <div
                      v-for="item in compareResult.field_diffs || []"
                      :key="item.field"
                      class="compare-card"
                      :class="{ changed: item.changed }"
                    >
                      <div class="compare-card-title">
                        <span>{{ item.field_label }}</span>
                        <el-tag size="small" :type="item.changed ? 'warning' : 'info'">
                          {{ item.changed ? "有变化" : "未变化" }}
                        </el-tag>
                      </div>
                      <div class="compare-card-body">
                        <div>
                          <div class="compare-label">基准版本</div>
                          <div class="compare-text">{{ item.before || "--" }}</div>
                        </div>
                        <div>
                          <div class="compare-label">对比版本</div>
                          <div class="compare-text">{{ item.after || "--" }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <el-empty v-if="!historyData.revisions.length" description="暂无版本快照" />
                <el-timeline v-else>
                  <el-timeline-item v-for="item in historyData.revisions" :key="item.id" :timestamp="item.create_time" type="primary">
                    <div class="history-card">
                      <div class="history-card-title">版本 V{{ item.version }} · {{ item.edit_reason || "手工编辑" }}</div>
                    <div class="history-card-text">
                      <p><span>所属模块：</span>{{ item.snapshot?.module || "--" }}</p>
                      <p><span>用例标题：</span>{{ item.snapshot?.title || "--" }}</p>
                      <p><span>前置条件：</span>{{ buildMultilineText(item.snapshot?.preconditions) || "--" }}</p>
                      <p><span>测试步骤：</span>{{ buildMultilineText(item.snapshot?.steps) || "--" }}</p>
                      <p><span>预期结果：</span>{{ buildMultilineText(item.snapshot?.expected_results) || "--" }}</p>
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>
            <el-tab-pane label="审核记录">
              <el-empty v-if="!historyData.review_logs.length" description="暂无审核记录" />
              <el-timeline v-else>
                <el-timeline-item v-for="item in historyData.review_logs" :key="item.id" :timestamp="item.create_time" type="success">
                  <div class="history-card">
                    <div class="history-card-title">{{ item.from_status_label || "--" }} -> {{ item.to_status_label || "--" }}</div>
                    <div v-if="item.review_reason_type_label" class="history-card-subtitle">原因类型：{{ item.review_reason_type_label }}</div>
                    <div class="history-card-text">{{ item.review_comment || "未填写审核意见" }}</div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>
          </el-tabs>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped lang="scss">
.testcase-assets-page {
  width: 100%;
}
.testcase-assets-page :deep(.koi-card) {
  flex: none;
  overflow: visible;
}
.search-form { display: flex; flex-wrap: wrap; gap: 8px 0; }
.toolbar-row { display: flex; align-items: center; justify-content: space-between; margin: 12px 0; gap: 12px; }
.toolbar-left { display: flex; align-items: center; gap: 8px; }
.asset-table { margin-top: 4px; }
.asset-table :deep(.vxe-body--row) { height: auto !important; }
.asset-table :deep(.vxe-body--column) { vertical-align: top; }
.asset-table :deep(.vxe-cell) {
  height: auto !important;
  max-height: none !important;
  white-space: normal;
  overflow: visible;
}
.title-cell { display: flex; flex-direction: column; gap: 6px; }
.title-main { font-weight: 600; color: var(--el-text-color-primary); }
.title-meta { display: flex; flex-wrap: wrap; gap: 8px; font-size: 12px; color: var(--el-text-color-secondary); }
.tag-summary { display: flex; flex-wrap: wrap; gap: 6px; }
.title-risk { font-size: 12px; color: var(--el-color-warning-dark-2); }
.multiline-cell {
  display: block;
  white-space: pre-wrap;
  word-break: break-word;
  overflow: visible;
  line-height: 1.7;
}
.operation-cell { display: flex; flex-direction: column; gap: 6px; }
.operation-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.operation-note { font-size: 12px; color: var(--el-text-color-secondary); }
.pager-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }
.drawer-alert { margin-bottom: 12px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 4px 16px; }
.form-grid :deep(.full-width) { grid-column: 1 / -1; }
.drawer-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 16px; }
.history-drawer { display: flex; flex-direction: column; gap: 16px; }
.summary-panel { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 16px 0; }
.summary-card { border: 1px solid var(--el-border-color-light); border-radius: 10px; padding: 14px; background: #fffaf3; }
.summary-card-title { font-size: 14px; font-weight: 600; color: var(--el-text-color-primary); }
.summary-card-status { margin-top: 8px; color: var(--el-text-color-secondary); }
.summary-card-actions { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.history-card { border: 1px solid var(--el-border-color-light); border-radius: 10px; padding: 12px 14px; background: #fff; }
.history-card-title { font-weight: 600; color: var(--el-text-color-primary); margin-bottom: 8px; }
.history-card-subtitle { margin-bottom: 8px; color: var(--el-text-color-secondary); font-size: 13px; }
.history-card-text { display: flex; flex-direction: column; gap: 6px; color: var(--el-text-color-regular); line-height: 1.7; white-space: pre-line; }
.history-card-text p { margin: 0; }
.history-card-text span { color: var(--el-text-color-secondary); }
.compare-panel { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.compare-toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.compare-result { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
.compare-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  padding: 14px;
  background: #fcfcfc;
}
.compare-card.changed {
  border-color: var(--el-color-warning-light-5);
  background: #fff8eb;
}
.compare-card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  font-weight: 600;
}
.compare-card-body { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.compare-label { font-size: 12px; color: var(--el-text-color-secondary); margin-bottom: 4px; }
.compare-text { white-space: pre-wrap; word-break: break-word; line-height: 1.7; color: var(--el-text-color-regular); }
@media (max-width: 1200px) { .form-grid { grid-template-columns: 1fr; } }
@media (max-width: 900px) { .compare-card-body { grid-template-columns: 1fr; } }
</style>
