<template>
  <div class="p-4px">
    <el-button type="primary" icon="Present" plain v-debounce:1000="handleDebounce">防抖</el-button>
    <el-button type="warning" icon="AlarmClock" plain v-throttle:3000="handleThrottle">节流</el-button>
    <div class="h-20px"></div>
    <div class="h-20px"></div>
    <div class="w-500px h-60px bg-gray-100" v-waterMarker="{ text: 'ADMIN', textColor: '#D9D9D9' }">水印指令</div>
  </div>
</template>

<script setup lang="ts" name="controlsPage">
// @ts-ignore
import { MsgSuccess, MsgWarning } from "@/utils/koi.ts";

const handleDebounce = () => {
  MsgSuccess("防抖🌻");
};
const handleThrottle = () => {
  MsgWarning("节流🌻");
};
</script>

<style scoped></style>
