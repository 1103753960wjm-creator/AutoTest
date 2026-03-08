<template>
  <!-- 头像 -->
  <el-image class="w-34px h-34px rounded-full select-none user-avatar" :src="avatar">
    <template #error>
      <el-image class="w-34px h-34px rounded-full select-none user-avatar" :src="errorAvatar"></el-image>
    </template>
  </el-image>
  <el-dropdown class="m-l-10px" :hide-on-click="false" @command="handleCommand">
    <div class="koi-dropdown">
      <div class="max-w-113px text-14px m-r-6px line-clamp-1 select-none">{{ user.username }}</div>
      <el-icon><arrow-down /></el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="koiMine">{{ $t("header.personalCenter") }}</el-dropdown-item>
        <el-dropdown-item command="logout">{{ $t("header.logout") }}</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { SessionStorage, LocalStorage } from "@/utils/storage.ts";
import { LOGIN_URL } from "@/config";
import { useRouter } from "vue-router";

const router = useRouter();

// 退出登录
const handleLayout = () => {
  SessionStorage.clear();
  // 如果不想要保存上次登录设置的全局颜色、布局等，则将下方第一行清空全部代码打开。
  // LocalStorage.clear();
  LocalStorage.remove("user");
  LocalStorage.remove("keepAlive");
  LocalStorage.remove("tabs");
  // 退出登录。必须使用replace把页面缓存刷掉。
  window.location.replace(LOGIN_URL);
};
const user = JSON.parse(LocalStorage.get("user"));

// 用户头像
const avatar = ref(user.avatar);
const errorAvatar = "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";
// 下拉折叠
const handleCommand = (command: string | number) => {
  switch (command) {
    case "koiMine":
      router.push("/system/personage");
      break;
    case "logout":
      handleLayout();
      break;
  }
};
</script>

<style lang="scss" scoped>
// dropdown字体颜色
.koi-dropdown {
  color: var(--el-color-primary);
  white-space: nowrap; /* 不换行 */
  cursor: pointer;
  outline: none; // 去除伪元素
  display: flex;
  align-items: center;
}
</style>
