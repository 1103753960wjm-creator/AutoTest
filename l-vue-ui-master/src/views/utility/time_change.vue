<script setup lang="ts">
import { ref, onMounted } from "vue";

const currentTime = ref<any>("");
const currentTimestamp = ref<any>("");

const getCurrentTime = () => {
  const date = new Date();
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const seconds = date.getSeconds();
  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  currentTimestamp.value = Date.now().toString();
};

const timestamp_input = ref<any>("");
const timestamp_output = ref<any>("");

const time_conversion = () => {
  const timestamp = parseInt(timestamp_input.value);
  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const seconds = date.getSeconds();
  timestamp_output.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

const time_input = ref<any>("");
const time_output = ref<any>("");

const timestamp_conversion = () => {
  const date = new Date(time_input.value);
  const timestamp = date.getTime();
  time_output.value = timestamp.toString();
};

onMounted(() => {
  getCurrentTime();
});
</script>

<template>
  <div style="padding: 10px;">
    <div>
      <koiCard>
        <div>
          <h4>当前北京时间：{{ currentTime }}</h4>
          <h4>当前时间戳：{{ currentTimestamp }}
          <el-button style="margin-left: 70px;" type="primary" icon="Refresh" @click="getCurrentTime">刷新当前时间
          </el-button></h4>
        </div>
        <div>
          <h3>北京时间转换时间戳：</h3>
          <el-input style="width: 300px; padding-right: 10px;" v-model="time_input" placeholder="请输入北京时间" />
          <el-button type="primary" @click="timestamp_conversion">转换</el-button>
          <el-input style="width: 300px; padding-left: 10px;" v-model="time_output" placeholder="响应结果" />
        </div>
        <div>
          <h3>时间戳转换北京时间：</h3>
          <el-input style="width: 300px; padding-right: 10px;" v-model="timestamp_input" placeholder="请输入时间戳" />
          <el-button type="primary" @click="time_conversion">转换</el-button>
          <el-input style="width: 300px; padding-left: 10px;" v-model="timestamp_output" placeholder="响应结果" />
        </div>
        <div class="h-10px"></div>
      </koiCard>
    </div>
  </div>
</template>

<style lang="less" scoped></style>
