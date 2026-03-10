<script setup lang="ts" name="testcaseAssetsPage">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { MsgSuccess, NoticeError } from "@/utils/koi.ts";
import { listRequirementPage } from "@/api/api_requirement/requirement.ts";
import { listTestcasePage, updateReviewStatus } from "@/api/api_testcase/testcase.ts";

const router = useRouter();
const loading = ref(false);
const total = ref(0);
const tableData = ref<any[]>([]);
const requirementOptions = ref<any[]>([]);
const savingIds = ref<number[]>([]);

const searchForm = ref({
  keyword: "",
  requirement_id: "",
  review_status: "",
  target_type: "",
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

const loadRequirementOptions = async () => {
  try {
    const res: any = await listRequirementPage({
      currentPage: 1,
      pageSize: 100,
      search: {}
    });
    requirementOptions.value = res.data.content || [];
  } catch {
    requirementOptions.value = [];
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
        target_type: searchForm.value.target_type
      }
    });
    tableData.value = (res.data.content || []).map((item: any) => ({
      ...item,
      pending_review_status: item.review_status
    }));
    total.value = res.data.total || 0;
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
    currentPage: 1,
    pageSize: 10
  };
  await loadTableData();
};

const handleSaveStatus = async (row: any) => {
  try {
    savingIds.value = [...savingIds.value, row.id];
    await updateReviewStatus({
      testcase_id: row.id,
      review_status: row.pending_review_status
    });
    row.review_status = row.pending_review_status;
    MsgSuccess("审核状态更新成功");
  } catch {
    row.pending_review_status = row.review_status;
    NoticeError("审核状态更新失败，请稍后重试");
  } finally {
    savingIds.value = savingIds.value.filter(item => item !== row.id);
  }
};

const statusLoading = (id: number) => {
  return savingIds.value.includes(id);
};

const automationTargetOptions = [
  { label: "API", value: "api" },
  { label: "Web", value: "web" },
  { label: "App", value: "app" }
];

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

const getAutomationItem = (row: any, targetType: string) => {
  const latestItems = row?.automation_summary?.latest_items || [];
  return latestItems.find((item: any) => item.target_type === targetType) || null;
};

const getAutomationStatusLabel = (item: any) => {
  if (!item) {
    return "未生成";
  }
  return item.save_status === "saved" ? "已保存" : "未保存";
};

const openDraftByQuery = async (query: Record<string, any>) => {
  await router.push({
    path: "/automation_draft",
    query: buildRouteQuery(query)
  });
};

const handleAutomationAction = async (row: any, targetType: string) => {
  const existingItem = getAutomationItem(row, targetType);
  if (existingItem?.draft_id) {
    await openDraftByQuery({
      testcase_id: row.id,
      target_type: targetType,
      draft_id: existingItem.draft_id
    });
    return;
  }

  if (row.review_status !== "approved") {
    NoticeError("只有已审核测试用例才允许生成自动化草稿");
    return;
  }

  await openDraftByQuery({
    testcase_id: row.id,
    target_type: targetType
  });
};

const viewTargetAsset = async (item: any) => {
  if (!item?.target_route || !item?.target_route_query) {
    NoticeError("当前草稿还没有可跳转的目标资产");
    return;
  }
  await router.push({
    path: item.target_route,
    query: buildRouteQuery(item.target_route_query || {})
  });
};

onMounted(async () => {
  await Promise.all([loadRequirementOptions(), loadTableData()]);
});
</script>

<template>
  <div class="koi-flex testcase-assets-page">
    <KoiCard>
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" clearable placeholder="用例标题 / 模块 / 类型" />
        </el-form-item>
        <el-form-item label="所属需求">
          <el-select v-model="searchForm.requirement_id" clearable filterable style="width: 220px">
            <el-option
              v-for="item in requirementOptions"
              :key="item.id"
              :label="item.title"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="searchForm.review_status" clearable style="width: 140px">
            <el-option
              v-for="item in reviewStatusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="目标类型">
          <el-select v-model="searchForm.target_type" clearable style="width: 140px">
            <el-option
              v-for="item in targetTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button plain @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <vxe-table
        v-loading="loading"
        border
        stripe
        auto-resize
        show-overflow
        :data="tableData"
        :row-config="{ isHover: true }"
        class="asset-table"
      >
        <vxe-column field="module" title="所属模块" min-width="160" />
        <vxe-column field="title" title="用例标题" min-width="260" />
        <vxe-column field="priority" title="优先级" width="90" />
        <vxe-column field="category" title="用例类型" min-width="160" />
        <vxe-column field="target_type" title="目标类型" width="100" />
        <vxe-column field="requirement_title" title="所属需求" min-width="220" />
        <vxe-column title="自动化进度" min-width="420">
          <template #default="{ row }">
            <div class="automation-summary-list">
              <div
                v-for="target in automationTargetOptions"
                :key="`${row.id}-${target.value}`"
                class="automation-summary-item"
              >
                <div class="summary-title-row">
                  <span class="summary-target">{{ target.label }}</span>
                  <el-tag
                    size="small"
                    :type="getAutomationItem(row, target.value)?.save_status === 'saved' ? 'success' : 'info'"
                  >
                    {{ getAutomationStatusLabel(getAutomationItem(row, target.value)) }}
                  </el-tag>
                </div>
                <div class="summary-meta">
                  <span>
                    草稿：
                    {{ getAutomationItem(row, target.value)?.draft_id || "-" }}
                  </span>
                  <span>
                    资产：
                    {{ getAutomationItem(row, target.value)?.target_asset_id || getAutomationItem(row, target.value)?.target_menu_id || "-" }}
                  </span>
                </div>
                <div class="draft-actions">
                  <el-button
                    size="small"
                    :type="getAutomationItem(row, target.value) ? 'primary' : 'default'"
                    plain
                    @click="handleAutomationAction(row, target.value)"
                  >
                    {{ getAutomationItem(row, target.value) ? "继续编辑" : "生成草稿" }}
                  </el-button>
                  <el-button
                    v-if="getAutomationItem(row, target.value)?.save_status === 'saved'"
                    size="small"
                    type="success"
                    plain
                    @click="viewTargetAsset(getAutomationItem(row, target.value))"
                  >
                    查看目标资产
                  </el-button>
                </div>
              </div>
            </div>
          </template>
        </vxe-column>
        <vxe-column title="审核状态" width="220" fixed="right">
          <template #default="{ row }">
            <div class="status-cell">
              <el-select v-model="row.pending_review_status" style="width: 120px">
                <el-option label="草稿" value="draft" />
                <el-option label="已审核" value="approved" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
              <el-button
                type="primary"
                link
                :loading="statusLoading(row.id)"
                @click="handleSaveStatus(row)"
              >
                保存
              </el-button>
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
  </div>
</template>

<style scoped lang="scss">
.testcase-assets-page {
  width: 100%;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 0;
}

.asset-table {
  margin-top: 12px;
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.draft-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.automation-summary-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.automation-summary-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  border: 1px solid var(--el-border-color);
  border-radius: 10px;
  background: var(--el-fill-color-blank);
}

.summary-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.summary-target {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.summary-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.pager-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 1400px) {
  .automation-summary-list {
    grid-template-columns: 1fr;
  }
}
</style>
