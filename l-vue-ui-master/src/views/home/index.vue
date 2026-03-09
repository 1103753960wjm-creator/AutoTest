<template>
  <div class="overflow-x-hidden">
    <el-card class="rounded-md" shadow="hover">
      <div style="float: right">
      </div>
      <div class="flex flex-items-center" v-waterMarker="{ text: 'L-Tester', textColor: '#D9D9D9' }">
        <img class="w-80px h-80px rounded-full select-none user-avatar" src="@/assets/images/logo/logo.webp"
          alt="avatar" />
        <div class="p-l-20px">
          <div class="font-bold p-b-8px whitespace-nowrap">
            <span>{{ "用户：" + username }}</span>
          </div>
          <div class="font-bold whitespace-nowrap">欢迎来到 L-Tester 测试平台。🌻
          </div>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" class="m-t-5px">
      <KoiCard></KoiCard>
      <el-col :span="24" class="m-t-5px">
        <el-card class="rounded-md" shadow="hover">
          <template #header> 🦀自动化执行统计 </template>
          <Count></Count>
        </el-card>
      </el-col>
      <el-col :span="12" :lg="12" :md="12" :sm="24" :xs="24" class="m-t-5px">
        <el-card class="rounded-md" shadow="hover">
          <template #header> 🐻地区异常订单排行 </template>
          <KoiLeftChart></KoiLeftChart>
        </el-card>
      </el-col>
      <el-col :span="12" :lg="12" :md="12" :sm="24" :xs="24" class="m-t-5px">
        <el-card class="rounded-md" shadow="hover">
          <template #header> 🐻‍❄️近10日订单量 </template>
          <KoiRightChart></KoiRightChart>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" class="m-t-5px">
      <el-col :span="12" :lg="12" :md="12" :sm="24" :xs="24">
        <el-card class="rounded-md" shadow="hover">
          <KoiTimeline1></KoiTimeline1>
        </el-card>
      </el-col>
      <el-col :span="12" :lg="12" :md="12" :sm="24" :xs="24">
        <el-card class="rounded-md" shadow="hover">
          <KoiTimeline2></KoiTimeline2>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts" name="homePage">
import { getDayText } from "@/utils/random.ts";
import { NoticeSuccess } from "@/utils/koi.ts";
import { ref } from "vue";
import KoiCard from "./components/KoiCard.vue";
import Count from "./components/count.vue";
import KoiLeftChart from "./components/KoiLeftChart.vue";
import KoiRightChart from "./components/KoiRightChart.vue";
import KoiTimeline1 from "./components/KoiTimeline1.vue";
import KoiTimeline2 from "./components/KoiTimeline2.vue";
import { onMounted } from "vue";
import { LocalStorage } from "@/utils/storage.ts";

onMounted(() => {
  // 时间问候语
  NoticeSuccess(getDayText(), "欢迎回来~");
  avatar.value = "@/assets/images/logo/logo.webp";
});

const getLocalUser = () => {
  const userText = LocalStorage.get("user");
  if (!userText) {
    return {
      username: "未知用户"
    };
  }
  try {
    return JSON.parse(userText);
  } catch {
    return {
      username: "未知用户"
    };
  }
};

const user = getLocalUser();

// 头像
const avatar = ref<any>("");

const username = user.username || "未知用户";
</script>

<style lang="scss" scoped></style>
