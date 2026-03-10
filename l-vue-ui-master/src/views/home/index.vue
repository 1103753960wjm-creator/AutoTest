<template>
  <div class="overflow-x-hidden">
    <!-- 顶部卡片：用户信息 -->
    <el-card class="rounded-md" shadow="hover">
      <div class="flex flex-items-center" v-waterMarker="{ text: 'KKchan', textColor: '#D9D9D9' }">
        <img class="w-80px h-80px rounded-full select-none user-avatar" src="@/assets/images/logo/logo.webp"
          alt="avatar" />
        <div class="p-l-20px">
          <div class="font-bold p-b-8px whitespace-nowrap">
            <span>{{ "用户：" + username }}</span>
          </div>
          <div class="font-bold whitespace-nowrap">欢迎来到测试工作台。🚀</div>
        </div>
      </div>
    </el-card>

    <!-- 顶部 4 个核心数据卡片 -->
    <el-row :gutter="20" class="m-t-5px">
      <el-col :span="6" :lg="6" :md="12" :sm="12" :xs="24" v-for="(card, index) in mockCards" :key="index" class="m-t-5px">
        <el-card class="rounded-md" shadow="hover">
          <div class="flex justify-between">
            <span class="text-sm font-bold">{{ card.title }}</span>
            <el-tag :type="card.tagType" size="small">{{ card.unit }}</el-tag>
          </div>
          <div class="text-2xl m-t-15px font-bold" :class="card.tagType === 'danger' ? 'text-red-500' : ''">
            {{ card.value }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主体 7:3 布局 -->
    <el-row :gutter="20" class="m-t-5px">
      <!-- 左侧核心区 (70%): 近期失败任务 -->
      <el-col :span="16" :lg="16" :md="24" :sm="24" :xs="24" class="m-t-5px">
        <el-card class="rounded-md" shadow="hover" style="height: 100%;">
          <template #header>
            <span class="font-bold text-red-500">🔴 我的排障台 - 近期失败任务</span>
          </template>
          <el-table :data="mockFailedTasks" style="width: 100%" border size="small" stripe>
            <el-table-column prop="time" label="运行时间" width="150" />
            <el-table-column prop="taskName" label="失败任务" min-width="120" show-overflow-tooltip />
            <el-table-column prop="reason" label="异常原因" min-width="180" show-overflow-tooltip>
              <template #default="scope">
                <el-tag type="danger" size="small">[Fail]</el-tag>
                <span class="m-l-5px text-xs text-gray-500">{{ scope.row.reason }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default>
                <el-button link type="primary" size="small">查看报告</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧辅助区 (30%): 快捷发射台 -->
      <el-col :span="8" :lg="8" :md="24" :sm="24" :xs="24" class="m-t-5px">
        <el-card class="rounded-md" shadow="hover" style="height: 100%;">
          <template #header> 
            <span class="font-bold">🚀 快捷发射台</span> 
          </template>
          <div class="quick-launch-grid">
            <el-button type="primary" class="launch-btn" plain>
              <template #icon><el-icon><Plus /></el-icon></template>
              用例生成
            </el-button>
            <el-button type="success" class="launch-btn" plain>
              <template #icon><el-icon><VideoPlay /></el-icon></template>
              接口管理
            </el-button>
            <el-button type="warning" class="launch-btn" plain>
              <template #icon><el-icon><Monitor /></el-icon></template>
              需求资产
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts" name="homePage">
import { ref, onMounted } from "vue";
import { getDayText } from "@/utils/random.ts";
import { NoticeSuccess } from "@/utils/koi.ts";
import { LocalStorage } from "@/utils/storage.ts";
import { Plus, VideoPlay, Monitor } from "@element-plus/icons-vue";

const getLocalUser = () => {
  const userText = LocalStorage.get("user");
  if (!userText) {
    return { username: "未知用户" };
  }
  try {
    return JSON.parse(userText);
  } catch {
    return { username: "未知用户" };
  }
};

const user = getLocalUser();
const avatar = ref<any>("");
const username = user.username || "未知用户";

onMounted(() => {
  NoticeSuccess(getDayText(), "欢迎回来~");
  avatar.value = "@/assets/images/logo/logo.webp";
});

// Mock Data：顶部数据卡片
const mockCards = ref([
  { title: "今日运行任务数", value: "128", unit: "次", tagType: "primary" },
  { title: "当前占用设备数", value: "4", unit: "台", tagType: "warning" },
  { title: "累计沉淀用例数", value: "3,240", unit: "条", tagType: "success" },
  { title: "待处理告警/失败", value: "12", unit: "个", tagType: "danger" },
]);

// Mock Data：近期失败任务
const mockFailedTasks = ref([
  { time: "2026-03-10 14:30", taskName: "支付核心链路回归 P0", reason: "500 Internal Server Error (Gateway)" },
  { time: "2026-03-10 12:15", taskName: "APP 登录流程埋点测试", reason: "ElementNotVisibleException: #loginBtn" },
  { time: "2026-03-10 09:40", taskName: "商品详情页并发性能压测", reason: "TimeoutError: response > 3000ms" },
  { time: "2026-03-10 02:00", taskName: "夜间全站全量回归", reason: "AssertionError: expected 'success' but got 'null'" },
]);
</script>

<style lang="scss" scoped>
.m-t-15px {
  margin-top: 15px;
}
.text-red-500 {
  color: #f56c6c;
}
.text-gray-500 {
  color: #909399;
}
.quick-launch-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.launch-btn {
  width: 100%;
  justify-content: flex-start;
  padding-left: 20px;
  height: 40px;
  font-size: 14px;
}
</style>
