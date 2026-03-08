<script lang="ts" setup>
import { ref, onMounted } from "vue";
import {
  api_tree_list,
  get_api_case,
  api_script_list,
  add_api_script,
  edit_api_script,
  del_api_script,
  api_env,
  params_select,
  api_service_list,
  run_api_script,
  get_api_script_log,
  get_api_script_result,
  // redis_common,
  api_db_list
} from "@/api/api_api/api";
import { MsgBox, MsgError, MsgSuccess } from "@/utils/koi";
import { LocalStorage } from "@/utils/storage.ts";
import Api_detail from "./api_detail.vue";

const searchParams = ref({
  search: {
    name__icontains: "",
    type__icontains: ""
  },
  currentPage: 1,
  pageSize: 10
});
const table_data = ref([]);
const total = ref(0);
const reset_search = () => {
  searchParams.value = {
    search: {
      name__icontains: "",
      type__icontains: ""
    },
    currentPage: 1,
    pageSize: 10
  };
};
const add_koiDialogRef = ref();
const edit_koiDialogRef = ref();
const title = ref("");
const add_form = ref<any>({
  name: "",
  description: "",
  type: 1,
  config: {
    params_id: null,
    env_id: null,
    cn_service: [],
    hw_service: []
  },
  script: []
});
const env_list = ref([{ name: "", id: null }]);
const params_list = ref<any>([]);

const get_script_list = async () => {
  const res: any = await api_script_list(searchParams.value);
  table_data.value = res.data.content;
  total.value = res.data.total;
};

const tree_list = ref<any>([]);
const script_select = ref<any>({});
const get_api_tree_list = async () => {
  const res: any = await api_tree_list({});
  tree_list.value = res.data;
};

const get_api_script = async () => {
  const res: any = await get_api_case({
    script: script_select.value
  });
  add_form.value.script = [...add_form.value.script, ...res.data];
  script_select.value = {};
};

const get_env_list = async () => {
  const res: any = await api_env({});
  env_list.value = res.data;
};

const get_params = async () => {
  const res: any = await params_select({});
  params_list.value = res.data;
};

const on_menu_allowDrop = (moveNode: any, inNode: any, type: any) => {
  // 不允许同一层级内的inner操作
  if (inNode.data.type == 3) {
    return type !== "inner";
  } else {
    console.log(moveNode);
    return type;
  }
};

const cn_service = ref<any>([]);
const hw_service = ref<any>([]);
const type_list = ref<any>([
  { name: "国内", value: 1 },
  { name: "海外", value: 2 }
]);
const get_api_list = async () => {
  const cn: any = await api_service_list({ project_id: 1 });
  const hw: any = await api_service_list({ project_id: 2 });
  cn_service.value = cn.data;
  hw_service.value = hw.data;
};
const defaultProps = {
  children: "children",
  label: "name"
};
const Add = async () => {
  await get_api_tree_list();
  title.value = "新增测试场景";
  add_koiDialogRef.value.koiOpen();
};

const add_confirm = async () => {
  const res: any = await add_api_script(add_form.value);
  add_koiDialogRef.value.koiQuickClose(res.message);
  await get_script_list();
};

const add_cancel = () => {
  add_koiDialogRef.value.koiQuickClose("已取消");
};

const select_list = ref<any>([]);
const result_id = ref<any>(null);
const run_form = ref<any>({});
const run_koiDialogRef = ref();
const handleSelectionChange = (selection: any) => {
  select_list.value = selection.sort((a: any, b: any) => a.step - b.step);
};

const run_script = async (row: any) => {
  run_form.value = {
    name: row.name,
    config: {
      env_id: null,
      params_id: null
    },
    run_list: [row]
  };
  title.value = "请配置调试信息";
  run_koiDialogRef.value.koiOpen();
};

const batch_run_script = async () => {
  run_form.value = {
    name: "",
    config: {
      env_id: null,
      params_id: null
    },
    run_list: select_list.value
  };
  title.value = "请配置调试信息";
  run_koiDialogRef.value.koiOpen();
};

const res_koiDialogRef = ref();
const user = JSON.parse(LocalStorage.get("user"));
const run_confirm = async () => {
  run_result_log.value = [];
  run_result_list.value = [];
  run_count.value = 0;
  run_fail.value = 0;
  start_time.value = "";
  end_time.value = "";
  run_type.value = "正在执行";
  if (run_form.value.config.env_id == null || run_form.value.name === "") {
    MsgError("请选择环境");
    return;
  }
  env_list.value.forEach((item: any) => {
    if (run_form.value.config.env_id === item.id) {
      run_env.value = item.name;
    }
  });
  title.value = run_form.value.name + " - " + run_type.value;
  result_id.value = Date.now();
  run_form.value.result_id = result_id.value;
  try {
    res_koiDialogRef.value.koiOpen();
  } catch (error) {
    console.log(error);
  }
  await startPolling();
  const res: any = await run_api_script(run_form.value);
  MsgSuccess(res.message);
};

const run_cancel = async () => {
  run_koiDialogRef.value.koiQuickClose("已取消");
};

const Edit = async (row: any) => {
  await get_api_tree_list();
  title.value = "编辑脚本：" + row.name;
  add_form.value = row;
  edit_koiDialogRef.value.koiOpen();
};

const edit_confirm = async () => {
  const res: any = await edit_api_script(add_form.value);
  edit_koiDialogRef.value.koiQuickClose(res.message);
  await get_script_list();
};

const edit_cancel = async () => {
  edit_koiDialogRef.value.koiQuickClose("已取消");
};

const Delete = async (row: any) => {
  MsgBox("您确认需要删除： " + row.name + " 么？").then(async () => {
    const res: any = await del_api_script({ id: row.id });
    MsgSuccess(res.message);
    await get_script_list();
  });
};

const del_script = (node: any, data: any) => {
  const parent = node.parent;
  const children: any[] = parent.data.children || parent.data;
  const index = children.findIndex(d => d.id === data.id);
  children.splice(index, 1);
  add_form.value.script = [...add_form.value.script];
};

const interval = ref<any>(null); // 保存轮询的定时器 ID

// 开始轮询
const startPolling = async () => {
  if (interval.value) return; // 避免重复启动
  interval.value = setInterval(get_result, 1500); // 每5秒轮询一次
};

// 停止轮询
const stopPolling = () => {
  if (interval.value) {
    clearInterval(interval.value);
    interval.value = null;
  }
};

const get_result = async () => {
  await get_script_log();
  await get_script_result();
};

const run_result_list = ref<any>([]);
const run_count = ref<any>(0);
const run_fail = ref<any>(0);
const start_time = ref<any>("");
const end_time = ref<any>("");
const run_type = ref<any>("");
const run_env = ref<any>("");
const get_script_result = async () => {
  const res: any = await get_api_script_result({
    result_id: result_id.value
  });
  run_result_list.value = res.data;
  run_count.value = run_result_list.value.length;
  if (run_result_list.value.length > 0) {
    start_time.value = start_time.value = run_result_list.value[run_result_list.value.length - 1].create_time;
  }
  run_fail.value = 0;
  run_result_list.value.forEach((item: any) => {
    if (item.status == 0) {
      run_fail.value = run_fail.value + 1;
    }
    if (item.name == "执行结束") {
      run_type.value = "执行结束";
      run_count.value = run_count.value - 1;
      stopPolling();
      end_time.value = item.create_time;
      return;
    }
  });
};
const run_result_log = ref<any>([]);
const get_script_log = async () => {
  const res: any = await get_api_script_log({
    result_id: result_id.value
  });
  run_result_log.value = res.data;
};
const getIcon = (status: any) => {
  if (status === 1) {
    return "Check";
  } else {
    return "Close";
  }
};
const colors = (status: any) => {
  if (status === 1) {
    return "#0bbd87";
  } else {
    return "#d70e0e";
  }
};

const get_colors = (status: any) => {
  if (status === 1) {
    return "color: #0bbd87";
  } else {
    return "color: #d70e0e";
  }
};

const get_log_style = (data: any) => {
  if (data.includes("失败")) {
    return "color: #d70e0e";
  }
};
// const redis_example_list = ref<any>([]);
const local_db_list = ref<any>([]);
// const get_redis_example = async (env: any) => {
//   const res: any = await redis_common({
//     env: add_form.value.config.env_id
//   });
//   redis_example_list.value = res.data.data;
// };
const get_db_list = async () => {
  const res: any = await api_db_list({});
  local_db_list.value = res.data.content;
};
const detail_koiDrawerRef = ref();
const detail = ref<any>({});
const view_result = async (api: any) => {
  //   await get_redis_example();
  await get_db_list();
  console.log(api);
  detail.value = api;
  detail_koiDrawerRef.value.koiOpen();
};

onMounted(() => {
  get_script_list();
  get_env_list();
  get_params();
  get_api_list();
});
</script>

<template>
  <div style="padding: 10px">
    <koiCard>
      <div>
        <el-form inline>
          <el-form-item label="地区：">
            <el-select placeholder="请选择地区" v-model="searchParams.search.type__icontains" clearable style="width: 130px">
              <el-option v-for="item in type_list" :key="item.value" :label="item.name" :value="item.value"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="任务名称：" prop="userName">
            <el-input
              placeholder="请输入任务名称"
              v-model="searchParams.search.name__icontains"
              clearable
              style="width: 300px"
            ></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="search" plain v-debounce="get_script_list">搜索</el-button>
            <el-button type="danger" icon="refresh" plain v-throttle="reset_search">重置</el-button>
            <el-button type="success" icon="plus" plain @click="Add">新增测试场景</el-button>
            <el-button v-if="select_list.length > 0" type="warning" icon="Promotion" plain @click="batch_run_script"
              >批量执行</el-button
            >
          </el-form-item>
        </el-form>
        <div class="h-10px"></div>
        <el-table :data="table_data" stripe border @selection-change="handleSelectionChange" style="width: 100%">
          <el-table-column type="selection" align="center" />
          <el-table-column prop="id" label="ID" width="80"></el-table-column>
          <el-table-column prop="name" label="名称"></el-table-column>
          <el-table-column label="用例集" width="100">
            <template #default="{ row }">
              <el-popover placement="top" :width="300" trigger="hover">
                <div>
                  <el-steps direction="vertical" :active="99">
                    <el-step v-for="step in row.script" :key="step.api_id" :title="step.name"></el-step>
                  </el-steps>
                </div>
                <template #reference>
                  <el-button type="text">用例详情</el-button>
                </template>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column label="地区" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.type === 1" type="success">国内</el-tag>
              <el-tag v-if="row.type === 2" type="warning">海外</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="跟随 CI 执行" :show-overflow-tooltip="true">
            <template #default="{ row }">
              <span v-if="row.type === 1">{{ row.config.cn_service }}</span>
              <span v-if="row.type === 2">{{ row.config.hw_service }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" :show-overflow-tooltip="true"></el-table-column>
          <el-table-column prop="username" label="最后更新人" width="100"></el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="140"></el-table-column>
          <el-table-column prop="update_time" label="更新时间" width="140"></el-table-column>
          <el-table-column label="操作" align="center" width="250">
            <template #default="scope">
              <el-button type="success" size="small" plain @click="run_script(scope.row)">立即运行</el-button>
              <el-button type="primary" size="small" plain @click="Edit(scope.row)">编辑</el-button>
              <el-button type="danger" size="small" plain @click="Delete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="h-10px"></div>
        <el-pagination
          background
          v-model:current-page="searchParams.currentPage"
          v-model:page-size="searchParams.pageSize"
          v-show="total > 0"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="get_script_list"
          @current-change="get_script_list"
        />
      </div>
      <div>
        <KoiDialog
          ref="add_koiDialogRef"
          :title="title"
          @koi-confirm="add_confirm"
          @koi-cancel="add_cancel"
          :height="630"
          :width="'700'"
        >
          <template #content>
            <el-form ref="formRef" :model="add_form" label-width="80px" status-icon inline>
              <el-form-item label="名称：">
                <el-radio-group v-model="add_form.type">
                  <el-radio :value="1">国内</el-radio>
                  <el-radio :value="2">海外</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="名称：">
                <el-input v-model="add_form.name" placeholder="请输入名称" clearable style="width: 400px" />
              </el-form-item>
              <el-form-item label="描述：">
                <el-input v-model="add_form.description" placeholder="请输入描述" style="width: 400px" />
              </el-form-item>
              <el-form-item v-if="add_form.type === 1" label="CI执行：">
                <el-select
                  v-model="add_form.config.cn_service"
                  collapse-tags
                  collapse-tags-tooltip
                  :max-collapse-tags="5"
                  multiple
                  placeholder="选择服务"
                  style="width: 400px"
                >
                  <el-option v-for="(env, index) in cn_service" :key="index" :label="'服务：' + env.name" :value="env.name">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item v-if="add_form.type === 2" label="CI执行：">
                <el-select
                  v-model="add_form.config.hw_service"
                  collapse-tags
                  collapse-tags-tooltip
                  :max-collapse-tags="3"
                  multiple
                  placeholder="选择服务"
                  style="width: 400px"
                >
                  <el-option v-for="(env, index) in hw_service" :key="index" :label="'服务：' + env.name" :value="env.name">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="参数依赖：">
                <el-select style="width: 400px" clearable v-model="add_form.config.params_id" placeholder="请选择参数依赖（非必选）">
                  <el-option v-for="(item, index) in params_list" :key="index" :label="item.name" :value="item.id"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="选择用例：">
                <el-cascader
                  v-model="script_select"
                  placeholder="请选择用例"
                  style="width: 400px; padding-right: 10px"
                  :options="tree_list"
                  filterable
                  collapse-tags
                  :props="{ value: 'api_id', label: 'name', children: 'children', multiple: true }"
                >
                  <template #default="{ node, data }">
                    <el-icon v-if="data.type === 0" style="padding-right: 5px">
                      <HomeFilled />
                    </el-icon>
                    <el-icon v-if="data.type === 1" style="padding-right: 5px">
                      <Folder />
                    </el-icon>
                    <SvgIcon v-if="data.type === 2" style="padding-right: 5px" name="API3" width="15" height="14"></SvgIcon>
                    <el-icon v-if="data.type === 3" style="padding-right: 5px">
                      <Link />
                    </el-icon>
                    <span>{{ data.name }}</span>
                    <span v-if="!node.isLeaf">({{ data.children.length }})</span>
                  </template>
                </el-cascader>
                <el-button type="primary" icon="plus" plain @click="get_api_script">确认添加</el-button>
              </el-form-item>
              <el-form-item label="脚本：">
                <div style="border: 1px solid #e4e7ed; width: 400px; height: 350px; overflow-y: auto; padding: 10px">
                  <el-tree
                    ref="treeRef"
                    :data="add_form.script"
                    :props="defaultProps"
                    default-expand-all
                    :allow-drop="on_menu_allowDrop"
                    draggable
                  >
                    <template #default="{ node, data }">
                      <span class="custom-tree-node" style="width: 100%">
                        <div style="border: 1px solid #3e7be5; border-radius: 5px; width: 93%; color: #3e7be5">
                          <span>
                            <el-icon style="padding-right: 3px; padding-left: 5px">
                              <Link />
                            </el-icon>
                            {{ data.name }}
                            <el-button
                              type="text"
                              style="float: right"
                              plain
                              icon="Delete"
                              @click="del_script(node, data)"
                            ></el-button>
                          </span>
                        </div>
                      </span>
                    </template>
                  </el-tree>
                </div>
              </el-form-item>
            </el-form>
          </template>
        </KoiDialog>
      </div>
      <div>
        <KoiDialog ref="edit_koiDialogRef" :title="title" @koi-confirm="edit_confirm" @koi-cancel="edit_cancel" :height="630">
          <template #content>
            <el-form ref="formRef" :model="add_form" label-width="80px" status-icon inline>
              <el-form-item label="名称：">
                <el-radio-group v-model="add_form.type">
                  <el-radio :value="1">国内</el-radio>
                  <el-radio :value="2">海外</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="名称：">
                <el-input v-model="add_form.name" placeholder="请输入名称" clearable style="width: 400px" />
              </el-form-item>
              <el-form-item label="描述：">
                <el-input v-model="add_form.description" placeholder="请输入描述" style="width: 400px" />
              </el-form-item>
              <el-form-item v-if="add_form.type === 1" label="CI执行：">
                <el-select
                  v-model="add_form.config.cn_service"
                  collapse-tags
                  collapse-tags-tooltip
                  :max-collapse-tags="5"
                  multiple
                  placeholder="选择服务"
                  style="width: 400px"
                >
                  <el-option v-for="(env, index) in cn_service" :key="index" :label="'服务：' + env.name" :value="env.name">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item v-if="add_form.type === 2" label="CI执行：">
                <el-select
                  v-model="add_form.config.hw_service"
                  collapse-tags
                  collapse-tags-tooltip
                  :max-collapse-tags="3"
                  multiple
                  placeholder="选择服务"
                  style="width: 400px"
                >
                  <el-option v-for="(env, index) in hw_service" :key="index" :label="'服务：' + env.name" :value="env.name">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="参数依赖：">
                <el-select style="width: 400px" clearable v-model="add_form.config.params_id" placeholder="请选择参数依赖（非必选）">
                  <el-option v-for="(item, index) in params_list" :key="index" :label="item.name" :value="item.id"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="选择用例：">
                <el-cascader
                  v-model="script_select"
                  placeholder="请选择用例"
                  style="width: 400px; padding-right: 10px"
                  :options="tree_list"
                  filterable
                  collapse-tags
                  :props="{ value: 'api_id', label: 'name', children: 'children', multiple: true }"
                >
                  <template #default="{ node, data }">
                    <el-icon v-if="data.type === 0" style="padding-right: 5px">
                      <HomeFilled />
                    </el-icon>
                    <el-icon v-if="data.type === 1" style="padding-right: 5px">
                      <Folder />
                    </el-icon>
                    <SvgIcon v-if="data.type === 2" style="padding-right: 5px" name="API3" width="15" height="14"></SvgIcon>
                    <el-icon v-if="data.type === 3" style="padding-right: 5px">
                      <Link />
                    </el-icon>
                    <span>{{ data.name }}</span>
                    <span v-if="!node.isLeaf">({{ data.children.length }})</span>
                  </template>
                </el-cascader>
                <el-button type="primary" icon="plus" plain @click="get_api_script">确认添加</el-button>
              </el-form-item>
              <el-form-item label="脚本：">
                <div style="border: 1px solid #e4e7ed; width: 400px; height: 350px; overflow-y: auto; padding: 10px">
                  <el-tree
                    ref="treeRef"
                    :data="add_form.script"
                    :props="defaultProps"
                    default-expand-all
                    :allow-drop="on_menu_allowDrop"
                    draggable
                  >
                    <template #default="{ node, data }">
                      <span class="custom-tree-node" style="width: 100%">
                        <div style="border: 1px solid #3e7be5; border-radius: 5px; width: 93%; color: #3e7be5">
                          <span>
                            <el-icon style="padding-right: 3px; padding-left: 5px">
                              <Link />
                            </el-icon>
                            {{ data.name }}
                            <el-button
                              type="text"
                              style="float: right"
                              plain
                              icon="Delete"
                              @click="del_script(node, data)"
                            ></el-button>
                          </span>
                        </div>
                      </span>
                    </template>
                  </el-tree>
                </div>
              </el-form-item>
            </el-form>
          </template>
        </KoiDialog>
      </div>
      <div>
        <KoiDialog
          ref="run_koiDialogRef"
          :title="title"
          @koi-confirm="run_confirm"
          @koi-cancel="run_cancel"
          :height="150"
          width="400px"
          :before-close-check="false"
        >
          <template #content>
            <el-form ref="formRef" :model="run_form" label-width="80px" status-icon>
              <el-form-item label="任务名称：" prop="roleName">
                <el-input v-model="run_form.name" placeholder="请输入名称" clearable />
              </el-form-item>
              <el-form-item label="执行环境：">
                <el-select v-model="run_form.config.env_id" placeholder="选择域名" style="width: 200px">
                  <el-option v-for="(env, index) in env_list" :label="env.name" :value="env.id" :key="index"> </el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="参数依赖：">
                <el-select style="width: 200px" v-model="run_form.config.params_id" clearable placeholder="非必选：选择参数依赖">
                  <el-option v-for="(params, index) in params_list" :key="index" :label="params.name" :value="params.id">
                  </el-option>
                </el-select>
              </el-form-item>
            </el-form>
          </template>
        </KoiDialog>
      </div>
      <div>
        <KoiDialog
          ref="res_koiDialogRef"
          :title="title"
          :height="680"
          width="81%"
          :footer-hidden="true"
          :before-close-check="false"
        >
          <template #content>
            <div style="width: 100%">
              <div>
                <KoiCard>
                  <div>
                    <el-descriptions column="4">
                      <el-descriptions-item label="任务名称：">{{ run_form.name }}</el-descriptions-item>
                      <el-descriptions-item label="执行人：">{{ user.username }}</el-descriptions-item>
                      <el-descriptions-item label="开始时间：">{{ start_time }}</el-descriptions-item>
                      <el-descriptions-item label="结束时间：">{{ end_time }}</el-descriptions-item>
                      <el-descriptions-item label="执行环境：">{{ run_env }}</el-descriptions-item>
                      <el-descriptions-item label="执行总数：">{{ run_count }}</el-descriptions-item>
                      <el-descriptions-item label="通过数：">{{ run_count - run_fail }}</el-descriptions-item>
                      <el-descriptions-item label="失败数：">{{ run_fail }}</el-descriptions-item>
                    </el-descriptions>
                  </div>
                </KoiCard>
              </div>
              <div style="padding-top: 5px">
                <KoiCard style="height: 560px">
                  <div style="width: 100%">
                    <div>
                      <KoiCard style="width: 30%; float: left; height: 530px; overflow: auto">
                        <el-timeline style="width: 80%">
                          <el-timeline-item
                            center
                            v-for="(res, index) in run_result_list"
                            :key="index"
                            :icon="getIcon(res.status)"
                            type="primary"
                            :color="colors(res.status)"
                            size="large"
                            :timestamp="'执行时间：' + res.create_time"
                            placement="top"
                          >
                            <KoiCard :style="get_colors(res.status)">
                              <span v-if="res.name !== '执行结束'">{{ "接口：" + res.name }}</span>
                              <span v-if="res.name === '执行结束'">{{ res.name }}</span>
                              <span v-if="res.name !== '执行结束'">
                                <span style="padding-right: 10px">{{ "code：" + res.res.code }}</span>
                                <span style="padding-right: 10px">{{ "size：" + res.res.size }}B</span>
                                <span>{{ "time：" + res.res.res_time }}ms</span>
                              </span>
                              <span v-if="res.name !== '执行结束'">
                                <div>
                                  <el-button icon="View" type="text" style="float: right" @click="view_result(res)">
                                    查看详情
                                  </el-button>
                                </div>
                              </span>
                            </KoiCard>
                          </el-timeline-item>
                        </el-timeline>
                      </KoiCard>
                    </div>
                    <div>
                      <KoiCard style="width: 67%; float: left; height: 530px; overflow: auto">
                        <div>
                          <li v-if="run_type !== '执行结束'" style="margin-bottom: 7px; color: #0bbd87">执行日志获取中...</li>
                          <li v-for="(log, index) in run_result_log" :key="index" :style="get_log_style(log)">{{ log }}</li>
                        </div>
                      </KoiCard>
                    </div>
                  </div>
                </KoiCard>
              </div>
            </div>
          </template>
        </KoiDialog>
      </div>
      <div>
        <KoiDrawer ref="detail_koiDrawerRef" :title="detail.name" :footer-hidden="true" :size="1100" :beforeCloseCheck="false">
          <template #content>
            <div>
              <Api_detail
                :res="detail.res"
                :req="detail.req"
                :env_list="env_list"
                :tree_list="tree_list"
                :local_db_list="[{ name: 'test', id: 1 }]"
                :redis_example_list="['common']"
              />
            </div>
          </template>
        </KoiDrawer>
      </div>
    </koiCard>
  </div>
</template>

<style lang="scss" scoped>
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 2px;
}

.el-tree-node__content {
  margin-bottom: 5px;
  height: 28px;
}

.el-tree {
  --el-tree-node-content-height: 30px;
}
</style>
