<script setup lang="ts" name="automationDraftPage">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { MsgSuccess, MsgWarning, NoticeError } from "@/utils/koi.ts";
import {
  generateAutomationDraft,
  getAutomationDraftInfo,
  listAutomationDraftByTestcase,
  saveAutomationDraftToAsset
} from "@/api/api_automation_draft/automation_draft.ts";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const saveLoading = ref(false);
const historyLoading = ref(false);
const draftInfo = ref<any>(null);
const historyList = ref<any[]>([]);
const draftJson = ref("");
const draftOpenMode = ref("new");

const targetLabelMap: Record<string, string> = {
  api: "API",
  web: "Web",
  app: "App"
};

const currentDraftId = computed(() => {
  const raw = route.query.draft_id;
  return Number(raw || 0);
});

const currentTestcaseId = computed(() => {
  const raw = route.query.testcase_id || draftInfo.value?.testcase?.id || 0;
  return Number(raw || 0);
});

const currentTargetType = computed(() => {
  return String(route.query.target_type || draftInfo.value?.target_type || "");
});

const draftOpenModeLabel = computed(() => {
  if (draftOpenMode.value === "history") {
    return "历史草稿";
  }
  return "新生成草稿";
});

const formatDraftJson = (payload: any) => {
  return JSON.stringify(payload || {}, null, 2);
};

const loadHistory = async (testcaseId: number) => {
  if (!testcaseId) {
    historyList.value = [];
    return;
  }
  try {
    historyLoading.value = true;
    const res: any = await listAutomationDraftByTestcase({ testcase_id: testcaseId });
    historyList.value = res.data || [];
  } catch {
    historyList.value = [];
  } finally {
    historyLoading.value = false;
  }
};

const loadDraftInfo = async (draftId: number) => {
  const res: any = await getAutomationDraftInfo({ draft_id: draftId });
  draftInfo.value = res.data;
  draftJson.value = formatDraftJson(res.data.draft_payload);
  await loadHistory(res.data.testcase?.id || 0);
};

const buildTargetRouteQuery = (query: Record<string, any>) => {
  return Object.keys(query || {}).reduce((result: Record<string, string>, key) => {
    const value = query[key];
    if (value === undefined || value === null || value === "") {
      return result;
    }
    result[key] = String(value);
    return result;
  }, {});
};

const generateCurrentDraft = async () => {
  if (!currentTestcaseId.value || !currentTargetType.value) {
    NoticeError("缺少测试用例或目标类型，无法生成自动化草稿");
    return;
  }
  try {
    loading.value = true;
    const res: any = await generateAutomationDraft({
      testcase_id: currentTestcaseId.value,
      target_type: currentTargetType.value
    });
    draftOpenMode.value = "new";
    draftInfo.value = res.data;
    draftJson.value = formatDraftJson(res.data.draft_payload);
    await loadHistory(res.data.testcase?.id || 0);
    await router.replace({
      path: "/automation_draft",
      query: {
        testcase_id: String(currentTestcaseId.value),
        target_type: currentTargetType.value,
        draft_id: String(res.data.id)
      }
    });
    MsgSuccess("自动化草稿生成成功");
  } catch {
    NoticeError("自动化草稿生成失败，请检查测试用例状态或 AI 配置");
  } finally {
    loading.value = false;
  }
};

const handleReloadDraft = async () => {
  if (!currentDraftId.value) {
    await generateCurrentDraft();
    return;
  }
  try {
    loading.value = true;
    draftOpenMode.value = "history";
    await loadDraftInfo(currentDraftId.value);
    MsgSuccess("自动化草稿已刷新");
  } catch {
    NoticeError("自动化草稿刷新失败，请稍后重试");
  } finally {
    loading.value = false;
  }
};

const openHistoryDraft = async (row: any) => {
  if (!row?.id) {
    MsgWarning("缺少草稿编号，无法打开");
    return;
  }
  try {
    loading.value = true;
    draftOpenMode.value = "history";
    await router.replace({
      path: "/automation_draft",
      query: {
        testcase_id: String(row.testcase_id || currentTestcaseId.value),
        target_type: String(row.target_type || currentTargetType.value),
        draft_id: String(row.id)
      }
    });
    await loadDraftInfo(row.id);
    MsgSuccess("历史草稿已打开");
  } catch {
    NoticeError("历史草稿打开失败，请稍后重试");
  } finally {
    loading.value = false;
  }
};

const viewTargetAsset = async (row: any) => {
  if (!row?.target_route || !row?.target_route_query) {
    MsgWarning("当前草稿还没有可跳转的目标资产");
    return;
  }
  await router.push({
    path: row.target_route,
    query: buildTargetRouteQuery(row.target_route_query || {})
  });
};

const handleSave = async () => {
  if (!draftInfo.value?.id) {
    MsgWarning("当前没有可保存的自动化草稿");
    return;
  }

  let editedPayload = {};
  try {
    editedPayload = JSON.parse(draftJson.value || "{}");
  } catch {
    MsgWarning("草稿 JSON 格式不正确，请先修正");
    return;
  }

  try {
    saveLoading.value = true;
    const res: any = await saveAutomationDraftToAsset({
      draft_id: draftInfo.value.id,
      edited_payload: editedPayload
    });
    MsgSuccess(`保存成功，正在跳转到${targetLabelMap[draftInfo.value.target_type] || "目标"}编辑页`);
    await loadDraftInfo(draftInfo.value.id);
    await router.push({
      path: res.data.target_route,
      query: buildTargetRouteQuery(res.data.target_route_query || {})
    });
  } catch {
    NoticeError("保存自动化草稿失败，请检查草稿结构后重试");
  } finally {
    saveLoading.value = false;
  }
};

onMounted(async () => {
  if (currentDraftId.value) {
    try {
      loading.value = true;
      draftOpenMode.value = "history";
      await loadDraftInfo(currentDraftId.value);
      return;
    } catch {
      NoticeError("自动化草稿加载失败，已尝试重新生成");
    } finally {
      loading.value = false;
    }
  }
  await generateCurrentDraft();
});
</script>

<template>
  <div class="automation-draft-page koi-flex">
    <div class="page-main">
      <KoiCard>
        <div class="header-row">
          <div>
            <div class="page-title">自动化草稿确认</div>
            <div class="page-subtitle">
              {{ targetLabelMap[currentTargetType] || "目标" }} 草稿只作为初稿，保存前请人工校对
            </div>
          </div>
          <div class="header-actions">
            <el-button plain :loading="loading" @click="handleReloadDraft">刷新草稿</el-button>
            <el-button type="primary" :loading="saveLoading" @click="handleSave">
              保存到目标资产
            </el-button>
          </div>
        </div>

        <el-alert
          type="warning"
          :closable="false"
          title="AI 生成仅为初稿，当前页面负责确认结构、补充占位值并保存到现有资产体系。"
        />

        <div v-if="draftInfo" class="content-grid">
          <div class="left-panel">
            <el-descriptions border :column="2" class="draft-meta">
              <el-descriptions-item label="用例标题">
                {{ draftInfo.testcase?.title || "-" }}
              </el-descriptions-item>
              <el-descriptions-item label="所属模块">
                {{ draftInfo.testcase?.module || "-" }}
              </el-descriptions-item>
              <el-descriptions-item label="目标类型">
                {{ targetLabelMap[draftInfo.target_type] || draftInfo.target_type }}
              </el-descriptions-item>
              <el-descriptions-item label="保存状态">
                <el-tag :type="draftInfo.save_status === 'saved' ? 'success' : 'warning'">
                  {{ draftInfo.save_status === "saved" ? "已保存" : "未保存" }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="请求模式">
                {{ draftInfo.requested_mode || "-" }}
              </el-descriptions-item>
              <el-descriptions-item label="生效模式">
                {{ draftInfo.effective_mode || "-" }}
              </el-descriptions-item>
              <el-descriptions-item label="打开方式">
                {{ draftOpenModeLabel }}
              </el-descriptions-item>
              <el-descriptions-item label="草稿编号">
                {{ draftInfo.id || "-" }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="warning-panel">
              <div class="section-title">生成告警</div>
              <el-empty
                v-if="!(draftInfo.warnings || []).length"
                description="当前没有额外告警"
                :image-size="70"
              />
              <ul v-else class="warning-list">
                <li v-for="(item, index) in draftInfo.warnings" :key="`${index}-${item}`">
                  {{ item }}
                </li>
              </ul>
            </div>

            <div class="history-panel">
              <div class="section-title">历史草稿</div>
              <el-table v-loading="historyLoading" :data="historyList" size="small" border>
                <el-table-column prop="id" label="编号" width="80" />
                <el-table-column prop="target_type" label="目标类型" width="90">
                  <template #default="{ row }">
                    {{ targetLabelMap[row.target_type] || row.target_type }}
                  </template>
                </el-table-column>
                <el-table-column prop="save_status" label="状态" width="90">
                  <template #default="{ row }">
                    <el-tag :type="row.save_status === 'saved' ? 'success' : 'warning'">
                      {{ row.save_status === "saved" ? "已保存" : "未保存" }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="target_asset_id" label="目标资产" min-width="120" />
                <el-table-column label="操作" width="180">
                  <template #default="{ row }">
                    <div class="history-actions">
                      <el-button type="primary" link @click="openHistoryDraft(row)">打开</el-button>
                      <el-button
                        type="success"
                        link
                        :disabled="row.save_status !== 'saved'"
                        @click="viewTargetAsset(row)"
                      >
                        查看目标资产
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <div class="right-panel">
            <div class="section-title">结构化草稿</div>
            <el-input
              v-model="draftJson"
              type="textarea"
              resize="none"
              :rows="28"
              class="draft-editor"
              placeholder="这里展示结构化自动化草稿 JSON，可在保存前人工修订。"
            />
          </div>
        </div>

        <el-empty v-else description="正在准备自动化草稿" :image-size="90" />
      </KoiCard>
    </div>
  </div>
</template>

<style scoped lang="scss">
.automation-draft-page {
  width: 100%;
}

.page-main {
  width: 100%;
}

.header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.page-subtitle {
  margin-top: 6px;
  color: var(--el-text-color-secondary);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.content-grid {
  display: grid;
  grid-template-columns: 420px minmax(0, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.warning-panel,
.history-panel {
  padding: 14px;
  border: 1px solid var(--el-border-color);
  border-radius: 10px;
  background: var(--el-bg-color-page);
}

.warning-list {
  margin: 0;
  padding-left: 18px;
  color: var(--el-text-color-regular);
  line-height: 1.7;
}

.history-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.draft-editor :deep(textarea) {
  min-height: 620px;
  font-family: Consolas, "Courier New", monospace;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .header-row {
    flex-direction: column;
  }
}
</style>
