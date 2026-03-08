<template>
  <!-- 注意：如果不进行操作数组，使用index当key没有问题，若是数组会用来增删改查则不能使用index当key。 -->
  <el-col :span="6" :lg="6" :md="12" :sm="12" :xs="24" v-for="(item, index) in cont_list" :key="index">
    <el-card class="rounded-md" shadow="hover">
      <div class="flex justify-between">
        <span class="text-sm">{{ item.title1 }}</span>
        <el-tag :type="index == 0 ? 'primary' : index == 1 ? 'success' : index == 2 ? 'warning' : 'danger'">{{
          item.unit
        }}</el-tag>
      </div>
      <div class="text-2xl">
        <CountTo :start-val="0" :end-val="item.value1" :duration="2000"></CountTo>
      </div>
      <el-divider direction="horizontal" content-position="left"></el-divider>
      <div class="flex justify-between">
        <span class="text-sm">{{ item.title2 }}</span>
        <span>
          <CountTo :start-val="0" :end-val="item.value2" :duration="2000"></CountTo>
        </span>
      </div>
    </el-card>
  </el-col>
</template>

<script setup lang="ts">
import { CountTo } from "vue3-count-to";
import { ref, onMounted } from "vue";
import { get_count } from "@/api/api_count/count";
const cont_list = ref<any>([]);

const get_count_list = async () => {
  const res: any = await get_count({});
  cont_list.value = res.data;
};

onMounted(() => {
  get_count_list();
});

</script>

<style lang="scss" scoped></style>
