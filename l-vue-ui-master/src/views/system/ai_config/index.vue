<script setup lang="ts" name="aiConfigPage">
import { onMounted, ref } from "vue";
import { MsgSuccess, NoticeError } from "@/utils/koi.ts";
import { getConfigInfo, saveConfig } from "@/api/api_ai/ai.ts";

const loading = ref(false);
const saveLoading = ref(false);
const currentStatus = ref<any>({
  configured_mode: "none",
  effective_mode: "none",
  used_fallback: false,
  provider: {
    provider_name: "template_rules",
    configured: true
  },
  providers: [],
  remote: {
    has_api_key: false
  }
});

const form = ref<any>({
  configured_mode: "none",
  local: {
    base_url: "",
    model: ""
  },
  remote: {
    base_url: "",
    model: "",
    api_key: ""
  }
});

const applyConfig = (data: any) => {
  currentStatus.value = data;
  form.value = {
    configured_mode: data.configured_mode || "none",
    local: {
      base_url: data.local?.base_url || "",
      model: data.local?.model || ""
    },
    remote: {
      base_url: data.remote?.base_url || "",
      model: data.remote?.model || "",
      api_key: ""
    }
  };
};

const loadConfig = async () => {
  try {
    loading.value = true;
    const res: any = await getConfigInfo({});
    applyConfig(res.data);
  } catch {
    NoticeError("AI 配置加载失败，请刷新页面后重试");
  } finally {
    loading.value = false;
  }
};

const handleSave = async () => {
  try {
    saveLoading.value = true;
    const payload = {
      configured_mode: form.value.configured_mode,
      local: {
        base_url: form.value.local.base_url,
        model: form.value.local.model
      },
      remote: {
        base_url: form.value.remote.base_url,
        model: form.value.remote.model,
        api_key: form.value.remote.api_key
      }
    };
    const res: any = await saveConfig(payload);
    applyConfig(res.data);
    MsgSuccess(res.message);
  } catch {
    NoticeError("AI 配置保存失败，请稍后重试");
  } finally {
    saveLoading.value = false;
  }
};

onMounted(() => {
  loadConfig();
});
</script>

<template>
  <div class="koi-flex">
    <KoiCard v-loading="loading">
      <el-alert
        title="当前阶段为平台级全局模式切换，保存后当前服务进程立即生效。"
        type="info"
        :closable="false"
        show-icon
      />

      <div class="h-16px"></div>

      <el-row :gutter="16">
        <el-col :xs="24" :sm="24" :md="12">
          <el-card shadow="never" class="status-card">
            <template #header>
              <span>当前运行状态</span>
            </template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="配置模式">
                <el-tag>{{ currentStatus.configured_mode || "none" }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="实际生效模式">
                <el-tag :type="currentStatus.effective_mode === currentStatus.configured_mode ? 'success' : 'warning'">
                  {{ currentStatus.effective_mode || "none" }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="当前 Provider">
                <span>{{ currentStatus.provider?.provider_name || "--" }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="是否回退到规则模式">
                <el-tag :type="currentStatus.used_fallback ? 'warning' : 'success'">
                  {{ currentStatus.used_fallback ? "是" : "否" }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="远程密钥状态">
                <el-tag :type="currentStatus.remote?.has_api_key ? 'success' : 'info'">
                  {{ currentStatus.remote?.has_api_key ? "已保存" : "未保存" }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12">
          <el-card shadow="never" class="status-card">
            <template #header>
              <span>可用模式概览</span>
            </template>
            <el-table :data="currentStatus.providers || []" border>
              <el-table-column label="模式" prop="mode" min-width="120" />
              <el-table-column label="Provider" prop="provider_name" min-width="180" />
              <el-table-column label="配置状态" min-width="100">
                <template #default="{ row }">
                  <el-tag :type="row.configured ? 'success' : 'info'">
                    {{ row.configured ? "可用" : "待配置" }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <div class="h-16px"></div>

      <el-card shadow="never">
        <template #header>
          <span>AI 模式配置</span>
        </template>

        <el-form :model="form" label-width="130px">
          <el-form-item label="平台运行模式">
            <el-radio-group v-model="form.configured_mode">
              <el-radio-button label="none">非大模型模式</el-radio-button>
              <el-radio-button label="local_llm">本地模型模式</el-radio-button>
              <el-radio-button label="remote_llm">接入大模型模式</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-divider content-position="left">本地模型配置</el-divider>

          <el-form-item label="本地接口地址">
            <el-input v-model="form.local.base_url" placeholder="例如：http://127.0.0.1:11434/v1" clearable />
          </el-form-item>
          <el-form-item label="本地模型名称">
            <el-input v-model="form.local.model" placeholder="例如：qwen2.5:7b" clearable />
          </el-form-item>

          <el-divider content-position="left">远程模型配置</el-divider>

          <el-form-item label="远程接口地址">
            <el-input v-model="form.remote.base_url" placeholder="例如：https://api.openai.com/v1" clearable />
          </el-form-item>
          <el-form-item label="远程模型名称">
            <el-input v-model="form.remote.model" placeholder="例如：gpt-4.1-mini" clearable />
          </el-form-item>
          <el-form-item label="远程密钥">
            <el-input
              v-model="form.remote.api_key"
              placeholder="留空则保留当前已保存密钥"
              show-password
              clearable
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="saveLoading" @click="handleSave">保存配置</el-button>
            <el-button icon="Refresh" plain @click="loadConfig">重新读取</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </KoiCard>
  </div>
</template>

<style scoped lang="scss">
.status-card {
  height: 100%;
}
</style>
