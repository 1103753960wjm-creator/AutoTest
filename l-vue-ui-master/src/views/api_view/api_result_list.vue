<script setup lang="ts">
import { onMounted, ref } from "vue";
import { get_api_script_result_list } from "@/api/api_api/api";

const table_data = ref<any>([]);
const searchParams = ref({
  currentPage: 1,
  pageSize: 10,
  search: {
    name: ""
  }
});
const customColors = ref<any>([
  { color: "#ea2e2e", percentage: 99.99 },
  { color: "#81d36f", percentage: 100 }
]);
const total = ref(0);
const get_script_result_list = async () => {
  const res: any = await get_api_script_result_list(searchParams.value);
  table_data.value = res.data.content;
  total.value = res.data.total;
};

const reset_search = () => {
  searchParams.value.currentPage = 1;
  searchParams.value.pageSize = 10;
  searchParams.value.search.name = "";
  get_script_result_list();
};
const view_report = async (result_id: any) => {
  // 待修改：前端地址ip:port
  window.open("http://10.12.2.78:5730/_api_report?result_id=" + result_id);
};

onMounted(() => {
  get_script_result_list();
});
</script>

<template>
  <div style="padding: 10px">
    <koiCard>
      <div>
        <el-form :model="searchParams" inline>
          <el-form-item label="任务名称">
            <el-input style="width: 200px" v-model="searchParams.search.name" placeholder="请输入任务名称"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" plain @click="get_script_result_list">搜索</el-button>
            <el-button type="danger" plain @click="reset_search">重置</el-button>
          </el-form-item>
        </el-form>
        <el-table :data="table_data" border>
          <el-table-column prop="id" label="ID"></el-table-column>
          <el-table-column prop="name" label="任务名称"></el-table-column>
          <el-table-column prop="result.pass" label="用例详情">
            <template #default="{ row }">
              <el-popover placement="top" :width="350" trigger="hover">
                <div>
                  <el-steps direction="vertical" :active="99">
                    <el-step v-for="step in row.script" :key="step.id">
                      <template #title>
                        <span>{{ step.name }}</span>
                        <span style="float: right">{{ "(通过数：" + step.pass + " 失败数：" + step.fail + ")" }}</span>
                      </template>
                    </el-step>
                  </el-steps>
                </div>
                <template #reference>
                  <el-button type="text">用例详情</el-button>
                </template>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column label="通过率">
            <template #default="{ row }">
              <el-progress :percentage="row.result.percent" :color="customColors"></el-progress>
            </template>
          </el-table-column>
          <el-table-column prop="username" label="执行人"></el-table-column>
          <el-table-column prop="start_time" label="开始时间"></el-table-column>
          <el-table-column prop="end_time" label="结束时间"></el-table-column>
          <el-table-column prop="status" label="操作">
            <template #default="{ row }">
              <el-button type="primary" plain @click="view_report(row.result_id)">查看测试报告</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="h-10px"></div>
        <el-pagination v-model:current-page="searchParams.currentPage" v-model:page-size="searchParams.pageSize"
          :page-sizes="[10, 25, 50]" :background="true" layout="total, sizes, prev, pager, next, jumper" :total="total"
          @size-change="get_script_result_list" @current-change="get_script_result_list" />
      </div>
    </koiCard>
  </div>
</template>

<style scoped lang="scss"></style>
