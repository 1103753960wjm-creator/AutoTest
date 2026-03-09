<script setup lang="ts" name="requirementAssetsPage">
import { onMounted, ref } from "vue";
import { NoticeError } from "@/utils/koi.ts";
import { listRequirementPage } from "@/api/api_requirement/requirement.ts";
import { listByRequirement } from "@/api/api_testcase/testcase.ts";

const loading = ref(false);
const detailLoading = ref(false);
const detailVisible = ref(false);
const total = ref(0);
const tableData = ref<any[]>([]);
const detailTestcases = ref<any[]>([]);
const currentRequirement = ref<any>({
  title: ""
});

const searchForm = ref({
  keyword: "",
  source_type: "",
  status: "",
  currentPage: 1,
  pageSize: 10
});

const sourceOptions = [
  { label: "全部来源", value: "" },
  { label: "需求文档", value: "requirement_doc" },
  { label: "功能设计", value: "feature_design" },
  { label: "用户故事", value: "user_story" }
];

const statusOptions = [
  { label: "全部状态", value: "" },
  { label: "已审核", value: "reviewed" }
];

const loadTableData = async () => {
  try {
    loading.value = true;
    const res: any = await listRequirementPage({
      currentPage: searchForm.value.currentPage,
      pageSize: searchForm.value.pageSize,
      search: {
        keyword: searchForm.value.keyword,
        source_type: searchForm.value.source_type,
        status: searchForm.value.status
      }
    });
    tableData.value = res.data.content || [];
    total.value = res.data.total || 0;
  } catch {
    NoticeError("需求资产列表加载失败，请稍后重试");
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
    source_type: "",
    status: "",
    currentPage: 1,
    pageSize: 10
  };
  await loadTableData();
};

const handleView = async (row: any) => {
  try {
    detailLoading.value = true;
    detailVisible.value = true;
    currentRequirement.value = row;
    const res: any = await listByRequirement({ requirement_id: row.id });
    currentRequirement.value = res.data.requirement || row;
    detailTestcases.value = res.data.testcases || [];
  } catch {
    NoticeError("需求详情加载失败，请稍后重试");
  } finally {
    detailLoading.value = false;
  }
};

onMounted(() => {
  loadTableData();
});
</script>

<template>
  <div class="koi-flex requirement-assets-page">
    <KoiCard>
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" clearable placeholder="需求标题 / 内容关键词" />
        </el-form-item>
        <el-form-item label="来源类型">
          <el-select v-model="searchForm.source_type" clearable style="width: 160px">
            <el-option v-for="item in sourceOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable style="width: 140px">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
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
        <vxe-column field="title" title="需求标题" min-width="260" />
        <vxe-column field="source_type" title="来源类型" width="140" />
        <vxe-column field="status" title="状态" width="120" />
        <vxe-column field="testcase_count" title="用例数量" width="100" align="center" />
        <vxe-column field="effective_mode" title="生效模式" width="120" />
        <vxe-column field="provider_name" title="Provider" min-width="180" />
        <vxe-column field="create_time" title="保存时间" width="180" />
        <vxe-column title="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看用例</el-button>
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

    <el-drawer v-model="detailVisible" size="64%" :title="`${currentRequirement.title || '需求资产'} - 关联用例`">
      <div v-loading="detailLoading">
        <el-descriptions border :column="2">
          <el-descriptions-item label="需求标题">{{ currentRequirement.title || "--" }}</el-descriptions-item>
          <el-descriptions-item label="来源类型">{{ currentRequirement.source_type || "--" }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentRequirement.status || "--" }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentRequirement.create_time || "--" }}</el-descriptions-item>
        </el-descriptions>

        <div class="h-16px"></div>

        <vxe-table border stripe auto-resize show-overflow :data="detailTestcases">
          <vxe-column field="module" title="所属模块" min-width="180" />
          <vxe-column field="title" title="用例标题" min-width="240" />
          <vxe-column field="priority" title="优先级" width="100" />
          <vxe-column field="category" title="用例类型" min-width="160" />
          <vxe-column field="review_status" title="审核状态" width="120" />
        </vxe-table>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped lang="scss">
.requirement-assets-page {
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

.pager-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
