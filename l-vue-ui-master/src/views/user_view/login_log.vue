<script setup lang="ts">
import { get_login_log_list } from '@/api/api_user/user';
import { onMounted, ref } from 'vue';

// 查询参数
const searchParams = ref({
  currentPage: 1, // 第几页
  pageSize: 10, // 每页显示多少条
  search: {
    login_user: ""
  }
});

const reset_search = async () => {
  searchParams.value = {
    currentPage: 1, // 第几页
    pageSize: 10, // 每页显示多少条
    search: {
      login_user: ""
    }
  };
};

const tableData = ref<any>([]);
const total = ref<number>(0);
const get_login_log = async () => {
  const res = await get_login_log_list(searchParams.value);
  tableData.value = res.data.content;
  total.value = res.data.total;
}

onMounted(() => {
  get_login_log();
});

</script>

<template>
  <div style="padding: 10px;">
    <KoiCard>
      <div>
        <el-form :inline="true">
            <el-form-item label="登录用户：">
              <el-input placeholder="请输入用户名称" v-model="searchParams.search.login_user" clearable
                style="width: 200px"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" icon="search" plain v-debounce="get_login_log">搜索</el-button>
              <el-button type="danger" icon="refresh" plain v-throttle="reset_search">重置</el-button>
            </el-form-item>
          </el-form>
          <div class="h-10px" />
          <el-table border :data="tableData" style="width: 100%">
            <el-table-column prop="id" label="ID" />
            <el-table-column prop="login_user" label="登录账户" />
            <el-table-column prop="login_ip" label="IP来源" />
            <el-table-column prop="create_time" label="登录时间" />
            <el-table-column prop="login_result" label="登录结果" />
          </el-table>
          <div class="h-10px" />
          <el-pagination v-model:current-page="searchParams.currentPage" v-model:page-size="searchParams.pageSize"
            :total="total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper"
            @size-change="get_login_log" @current-change="get_login_log" />
      </div>
    </KoiCard>
  </div>
</template>

<style lang="less" scoped></style>
