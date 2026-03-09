<script setup lang="ts">
import { onMounted, ref } from "vue";
import { get_web_result_list } from "@/api/api_web/web.ts";
import { REPORT_BASE_URL } from "@/config/index.ts";

const table_list = ref<any>([]);
const loading = ref<any>(false);
const customColors = ref<any>([
  { color: "#ea2e2e", percentage: 99.99 },
  { color: "#81d36f", percentage: 100 }
]);
// 搜索区域展示
const showSearch = ref<boolean>(true);
// 查询参数
const searchParams = ref({
  currentPage: 1, // 第几页
  pageSize: 10, // 每页显示多少条
  search: {
    task_name__icontains: ""
  }
});
//总数
const total = ref<number>(0);

const result_list = async () => {
  loading.value = true;
  const res: any = await get_web_result_list(searchParams.value);
  table_list.value = res.data.content;
  total.value = res.data.total;
  loading.value = false;
};

const reset_search = async () => {
  searchParams.value = {
    currentPage: 1, // 第几页
    pageSize: 10, // 每页显示多少条
    search: {
      task_name__icontains: ""
    }
  };
  await result_list();
};

const view_report = async (result_id: any) => {
  // 待修改：前端地址ip:port
  window.open(`${REPORT_BASE_URL}/web_report?result_id=${result_id}`);
};
// 生命周期钩子
onMounted(() => {
  result_list();
});
</script>

<template>
  <div style="padding: 10px">
    <koiCard>
      <div>
        <el-form v-show="showSearch" :inline="true">
          <el-form-item label="任务名称：" prop="userName">
            <el-input placeholder="请输入任务名称" v-model="searchParams.search.task_name__icontains" clearable
              style="width: 200px"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="search" plain v-debounce="result_list">搜索</el-button>
            <el-button type="danger" icon="refresh" plain v-throttle="reset_search">重置</el-button>
          </el-form-item>
        </el-form>
        <el-table v-loading="loading" border :data="table_list" empty-text="暂时没有数据哟🌻">
          <el-table-column type="selection" align="center" />
          <el-table-column label="序号" prop="id" align="center" type="index"></el-table-column>
          <el-table-column label="任务名称" prop="task_name" align="center" :show-overflow-tooltip="true"></el-table-column>
          <el-table-column label="测试用例" width="180px" align="center">
            <template #default="{ row }">
              <el-popover placement="top" :width="300" trigger="hover">
                <div>
                  <el-steps direction="vertical" :active="99">
                    <el-step v-for="step in row.script_list" :key="step.id" :title="step.name"></el-step>
                  </el-steps>
                </div>
                <template #reference>
                  <el-button type="text">用例详情</el-button>
                </template>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column label="执行浏览器" prop="browser_list" width="180px" align="center">
            <template #default="{ row }">
              <el-popover placement="top" trigger="hover">
                <div v-for="(browser, index) in row.browser_list" :key="index" style="padding-block-end: 3px">
                  <span v-if="browser === 1" style="padding-right: 5px"><el-tag size="mini" type="danger">Google
                      Chrome</el-tag></span>
                  <span v-if="browser === 2" style="padding-right: 5px"><el-tag size="mini" type="warning">Mozilla
                      Firefox</el-tag></span>
                  <span v-if="browser === 3" style="padding-right: 5px"><el-tag size="mini" type="primary">Microsoft
                      Edge</el-tag></span>
                  <span v-if="browser === 4"><el-tag size="mini" type="success">Safari</el-tag></span>
                </div>
                <template #reference>
                  <el-button type="text">浏览器详情</el-button>
                </template>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column label="任务状态" prop="status" width="180px" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.status === 1" type="success">执行完成</el-tag>
              <el-tag v-else type="danger">任务执行中</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="通过率" prop="percent" width="180px" align="center">
            <template #default="{ row }">
              <el-progress :percentage="row.percent" :color="customColors"></el-progress>
            </template>
          </el-table-column>
          <el-table-column label="执行人" prop="username" width="180px" align="center"></el-table-column>
          <el-table-column label="开始时间" prop="start_time" width="180px" align="center"></el-table-column>
          <el-table-column label="结束时间" prop="end_time" width="180px" align="center"></el-table-column>
          <el-table-column label="操作" align="center" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.status === 1" type="text" plain
                @click="view_report(row.result_id)">查看测试报告</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="h-10px"></div>
        <el-pagination background v-model:current-page="searchParams.currentPage"
          v-model:page-size="searchParams.pageSize" v-show="total > 0" :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="result_list"
          @current-change="result_list" />
      </div>
    </koiCard>
  </div>
</template>

<style scoped lang="scss"></style>
