<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { get_action_log_list, user_select } from '@/api/api_user/user';
import jsonEditor from "@/components/CodeEditor/jsonEditor.vue";
import moment from 'moment';

const shortcuts = ref<any>([
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setDate(start.getDate() - 7)
      return [start, end]
    },
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 1)
      return [start, end]
    },
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 3)
      return [start, end]
    },
  },
])

const searchParams = ref({
  search: {
    log_api__contains: '',
    create_time__range: <any>[],
    user_id: ""
  },
  currentPage: 1,
  pageSize: 10
});

const tableData = ref([]);
const total = ref(0);
const get_action_log = async () => {
  const res = await get_action_log_list(searchParams.value);
  tableData.value = res.data.content;
  total.value = res.data.total;
};

const reset_search = async () => {
  searchParams.value.search.log_api__contains = '';
  searchParams.value.search.user_id = '';
  await get_action_log();
};

const view_koiDialogRef = ref<any>(null);
const title = ref<string>("");
const config_field = ref<any>({});
const view_action_log = (row: any) => {
  title.value = "操作结果详情";
  view_koiDialogRef.value.koiOpen();
  config_field.value = {
    "url": row.log_api,
    "body": row.log_content,
    "status": row.log_status,
    "result": row.log_result
  };
};

const change_time = async (value: any) => {
  const start: string = value[0] + " 00:00:00"
  const end: string = value[1] + " 23:59:59"
  searchParams.value.search.create_time__range = [start, end];
}

const user_list = ref<any>([]);
const get_user_list = async () => {
  const res: any = await user_select({});
  user_list.value = res.data;
};

const change_user = async () => {
  await get_action_log();
};
onMounted(() => {
  const today: any = moment();
  const start: string = today.startOf('day').format('YYYY-MM-DD 00:00:00');
  const end: any = today.endOf('day').format('YYYY-MM-DD 23:59:59');
  const list = [start, end]
  searchParams.value.search.create_time__range = list
  get_action_log();
  get_user_list();
});

</script>

<template>
  <div style="padding: 10px;">
    <KoiCard>
      <div>
        <el-form :inline="true">
          <el-form-item>
            <div class="block">
              <el-date-picker v-model="searchParams.search.create_time__range" type="daterange" :shortcuts="shortcuts"
                range-separator="至" start-placeholder="开始时间" end-placeholder="结束时间" value-format="YYYY-MM-DD"
                @change="change_time" />
            </div>
          </el-form-item>
          <el-form-item label="操作人：">
            <div class="block">
              <el-select v-model="searchParams.search.user_id" placeholder="请选择用户" clearable style="width: 120px;"
                @change="change_user">
                <el-option v-for="item in user_list" :key="item.id" :label="item.name" :value="item.id">
                </el-option>
              </el-select>
            </div>
          </el-form-item>
          <el-form-item label="操作接口：">
            <el-input placeholder="请输入操作接口" v-model="searchParams.search.log_api__contains" clearable
              style="width: 200px"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="search" plain v-debounce="get_action_log">搜索</el-button>
            <el-button type="danger" icon="refresh" plain v-throttle="reset_search">重置</el-button>
          </el-form-item>
        </el-form>
        <div class="h-10px" />
        <el-table border :data="tableData" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80px" />
          <el-table-column prop="username" label="操作用户" width="80px" />
          <el-table-column prop="log_ip" label="IP来源" width="100px" />
          <el-table-column prop="log_api" label="操作接口" />
          <el-table-column prop="log_content" label="操作内容" :show-overflow-tooltip="true">
            <template #default="{ row }">
              {{ row.log_content }}
            </template>
          </el-table-column>
          <el-table-column label="操作状态" width="80px">
            <template #default="{ row }">
              <el-tag type="success" v-if="row.log_status == 200">{{ row.log_status }}</el-tag>
              <el-tag type="danger" v-else>{{ row.log_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="log_result" label="操作结果" :show-overflow-tooltip="true">
            <template #default="{ row }">
              {{ row.log_result }}
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="操作时间" width="150px" />
          <el-table-column prop="create_time" label="操作" width="150px">
            <template #default="{ row }">
              <el-button type="primary" plain @click="view_action_log(row)">查看结果详情</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="h-10px" />
        <el-pagination v-model:current-page="searchParams.currentPage" v-model:page-size="searchParams.pageSize"
          :total="total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper"
          @size-change="get_action_log" @current-change="get_action_log" />
      </div>
      <div>
        <koiDialog ref="view_koiDialogRef" :before-close-check="false" :title="title" :height="640" width="85%"
          :footer-hidden="true">
          <template #content>
            <div style="width: 100%">
              <el-form>
                <el-form-item>
                  <div style="width: 100%; height: 400px">
                    <jsonEditor :code="JSON.stringify(config_field, null, 4)" :height="'550'" />
                  </div>
                </el-form-item>
              </el-form>
            </div>
          </template>
        </koiDialog>
      </div>
    </KoiCard>
  </div>
</template>
