<script lang="ts" setup>
import {
  api_project,
  api_service,
  api_tree,
  add_menu,
  edit_menu,
  del_menu,
  copy_menu,
  api_info,
  save_api,
  save_api_case,
  api_env,
  api_send,
  api_tree_list,
  api_db_list,
  save_env,
  req_history,
  params_select,
  api_edit_history
} from "@/api/api_api/api.ts";
import { ref, onMounted, watch } from "vue";
import { ElTree } from "element-plus";
import VueJsonPretty from "vue-json-pretty";
import "vue-json-pretty/lib/styles.css";
import jsonE from "@/components/CodeEditor/jsonE.vue";
import { MsgBox, MsgSuccess, MsgError } from "@/utils/koi";
import api_var from "@/views/api_view/api_var.vue";
import Api_detail from "./api_detail.vue";
import encryption from "../utility/encryption.vue";
import time_change from "../utility/time_change.vue";
import api_code from "./api_code.vue";
import api_function from "./api_function.vue";
import api_db from "./api_db.vue";
import api_params from "./api_params.vue";

const project_list = ref<any>([]);
const service_list = ref<any>([]);
const project_searchParams = ref({
  currentPage: 1,
  pageSize: 18,
  search: {}
});
const project_total = ref(0);
const service_total = ref(0);
const show_type = ref("project");
const service_searchParams = ref({
  currentPage: 1,
  pageSize: 18,
  search: {
    api_project_id: null
  }
});
const filterText = ref<any>("");
const api_project_id = ref<any>(null);
const api_service_id = ref<any>(null);
const tree_data = ref<any>([]);
const add_koiDialogRef = ref();
const edit_koiDialogRef = ref();
const title = ref<any>("");
const add_form = ref<any>({});
const tab_active = ref<any>("");
const tab_list = ref<any>([]);
const env_list = ref<any>([]);
const env_id = ref<any>(null);
const tool_active = ref<any>("second");

const getProjectList = async () => {
  show_type.value = "project";
  const res: any = await api_project(project_searchParams.value);
  project_list.value = res.data.content;
  project_total.value = res.data.total;
};

const into_Service = async (id: any) => {
  api_project_id.value = id;
  await getService();
};

const back_project = async () => {
  await getProjectList();
};

const getService = async () => {
  show_type.value = "service";
  service_searchParams.value.search.api_project_id = api_project_id.value;
  const res: any = await api_service(service_searchParams.value);
  service_list.value = res.data.content;
  service_total.value = res.data.total;
};

const get_env = async () => {
  const res: any = await api_env({});
  env_list.value = res.data;
  env_id.value = res.data[0].id;
};

const get_env_list = async () => {
  const res: any = await api_env({});
  env_list.value = res.data;
};

const api_loading = ref<any>(false);
const loading_text = ref<any>("");
const into_Api = async (service_id: any) => {
  loading_text.value = "接口数据量较大，正在加载接口数据，请稍后...";
  api_loading.value = true;
  api_service_id.value = service_id;
  await get_tree();
  await get_env();
  await get_params();
  show_type.value = "api";
  api_loading.value = false;
};

const treeRef = ref<InstanceType<typeof ElTree>>();
watch(filterText, val => {
  treeRef.value!.filter(val);
});

const get_tree = async () => {
  const res: any = await api_tree({
    search: {
      api_service_id: api_service_id.value
    }
  });
  tree_data.value = res.data;
};
const AddMenu = async (data: any) => {
  add_form.value = {
    pid: data.id,
    name: "",
    type: 1,
    api_service_id: api_service_id.value
  };
  title.value = "添加菜单";
  add_koiDialogRef.value.koiOpen();
};
const add_menu_confirm = async () => {
  const res: any = await add_menu(add_form.value);
  await get_tree();
  add_koiDialogRef.value.koiQuickClose(res.message);
};

const add_menu_cancel = async () => {
  add_koiDialogRef.value.koiClose("已取消");
};
const EditMenu = async (data: any) => {
  add_form.value = data;
  title.value = "编辑菜单";
  edit_koiDialogRef.value.koiOpen();
};
const edit_menu_confirm = async () => {
  const res: any = await edit_menu(add_form.value);
  await get_tree();
  edit_koiDialogRef.value.koiQuickClose(res.message);
};
const edit_menu_cancel = async () => {
  edit_koiDialogRef.value.koiQuickClose("已取消");
};
const CopyMenu = async (data: any) => {
  MsgBox("您确认复制该目录：" + data.name + "么？").then(async () => {
    const res: any = await copy_menu(data);
    MsgSuccess(res.message);
    await get_tree();
  });
};
const DelMenu = async (data: any) => {
  MsgBox("您确认需要删除该目录：" + data.name + "么？").then(async () => {
    const res: any = await del_menu(data);
    MsgSuccess(res.message);
    await get_tree();
  });
};

const method_list = ref([
  { name: "GET", value: 1 },
  { name: "POST", value: 2 },
  { name: "PUT", value: 3 },
  { name: "DELETE", value: 4 },
  { name: "PATCH", value: 5 },
  { name: "OPTIONS", value: 6 }
]);
const req_active = ref<any>("body");
const res_active = ref<any>("res");
const api_form = ref<any>({});
const file_path = ref<any>([]);
const menu_click = async (data: any) => {
  const newTabName = data.name;
  const index = tab_list.value.findIndex((item: any) => item.title === newTabName);
  if (index === -1) {
    if (data.type == 0) {
      console.log(data);
    } else if (data.type == 1) {
      console.log(data);
    } else if (data.type == 2) {
      const res: any = await api_info(data);
      data.api_info = res.data;
      await add_tab(data);
    } else if (data.type == 3) {
      const res: any = await api_info(data);
      data.api_info = res.data;
      await add_tab(data);
    }
  } else {
    tab_active.value = data.name;
  }
  history_searchParams.value = {
    currentPage: 1,
    pageSize: 10,
    search: {}
  };
};

const add_tab = async (data: any) => {
  data.api_info.req.body = JSON.stringify(data.api_info.req.body, null, 2);
  api_form.value = {
    title: data.name,
    name: data.name,
    content: data.api_info,
    id: data.id,
    type: data.type,
    api_id: data.api_id,
    res: {
      code: 0,
      size: 0,
      res_time: 0,
      before: [],
      after: [],
      assert: []
    }
  };
  tab_list.value.push(api_form.value);
  tab_active.value = data.name;
};

const removeTab = async (targetName: any) => {
  history_searchParams.value = {
    currentPage: 1,
    pageSize: 10,
    search: {}
  };
  const tabs = tab_list.value;
  let activeName = tab_active.value;
  if (activeName === targetName) {
    tab_list.value.forEach((tab: any, index: any) => {
      if (tab.name === targetName) {
        const nextTab = tabs[index + 1] || tabs[index - 1];
        if (nextTab) {
          activeName = nextTab.name;
          tabs.splice(1, index);
        }
      }
    });
  }
  tab_active.value = activeName;
  tab_list.value = tabs.filter((tab: any) => tab.name !== targetName);
};

const tab_click = async (targetName: any) => {
  history_searchParams.value = {
    currentPage: 1,
    pageSize: 10,
    search: {}
  };
  tab_list.value.forEach((tab: any) => {
    if (tab.name === targetName.props.name) {
      if (tab.type == 2 || tab.type == 3) {
        api_form.value = tab;
      }
    }
  });
};

// 添加url参数
const add_params = async (params: any) => {
  params.push({
    key: "",
    value: "",
    status: true
  });
};
const remove_params = async (params: any, index: any) => {
  params.splice(index, 1);
};

const call_back_1 = async (fileMap: any) => {
  file_path.value.push(fileMap.file_url + "/" + fileMap.filename);
};

const add_file = () => {
  api_form.value.content.req.file_path = file_path.value;
};

const tree_list = ref([]);
const val_type_list = ref([
  { name: "环境变量", value: 1 },
  { name: "全局变量", value: 2 }
]);
const res_type_list = ref([
  { name: "响应结果-JSON", value: 1 },
  { name: "请求头-Headers", value: 2 },
  { name: "请求头-Body", value: 3 },
  { name: "Headers-响应结果", value: 4 },
  { name: "自定义目标值", value: 5 }
]);

const tips = ref<any>(
  '路径示例，结果={"code": 200, "info": {"username": "admin"}, "list": [{"id": 1},{"id": 2}]}\n' +
  "例子：code：$.code, username：$.info.username，数组：$.list[0].id / $.list[1].id分别等于1 / 2"
);
const redis_example_list = ref<any>([]);
const local_db_list = ref<any>([]);
const env_koiDialogRef = ref();
const get_api_tree_list = async () => {
  const res: any = await api_tree_list({});
  tree_list.value = res.data;
};

const get_db_list = async () => {
  const res: any = await api_db_list({});
  local_db_list.value = res.data.content;
};

const params_list = ref<any>([]);
const get_params = async () => {
  const res: any = await params_select({});
  params_list.value = res.data;
};

const env_active = ref<any>("overall");
const Editenv = async () => {
  await get_env_list();
  env_list.value.forEach((item: any) => {
    if (item.id === env_id.value) {
      env_active.value = item.name;
    }
  });
  title.value = "编辑环境";
  env_koiDialogRef.value.koiOpen();
};

const add_env_config = async (data: any) => {
  data.push({
    name: "",
    value: ""
  });
};

const add_env_confirm = async () => {
  const res: any = await save_env({ env_list: env_list.value });
  MsgSuccess(res.message);
  await get_env_list();
};

const add_env_cancel = async () => {
  env_koiDialogRef.value.koiQuickClose("已关闭");
};

const add_before = async (type: any) => {
  const before = {
    title: "",
    type: type,
    api_id: [],
    env_id: [],
    wait_time: 1,
    env_type: 1,
    value: "",
    name: "",
    code: ""
  };
  api_form.value.content.req.before.push(before);
};

const add_after = async (type: any) => {
  const after = {
    type: type,
    wait_time: 1,
    env_type: 1,
    res_type: 1,
    value: "",
    name: ""
  };
  api_form.value.content.req.after.push(after);
};

const add_assert = async (type: any) => {
  const assert = {
    redis_type: "",
    redis_example: "",
    redis: [],
    local_db: null,
    local_db_table: "",
    local_db_where: "",
    local_db_assert: [],
    type: type,
    res_type: 1,
    value: "",
    name: ""
  };
  api_form.value.content.req.assert.push(assert);
};


// 保存接口
const saveApi = async (api: any) => {
  const req = api.content;
  req.id = api.api_id;
  const res: any = await save_api(req);
  MsgSuccess(res.message);
};

const add_case_koiDialogRef = ref();
const api_case_form = ref<any>({});
const saveApiCase = async (api: any) => {
  api_case_form.value = api;
  title.value = "保存为用例"
  add_case_koiDialogRef.value.koiOpen();
};

const add_case_confirm = async () => {
  const req = api_case_form.value.content;
  req.name = add_form.value.name;
  req.id = api_case_form.value.api_id;
  const res: any = await save_api_case(req);
  add_case_koiDialogRef.value.koiQuickClose(res.message);
  await get_tree();
};

const add_case_cancel = async () => {
  add_case_koiDialogRef.value.koiQuickClose("已关闭");
};

const loading = ref<any>(false);
const SendRequest = async (api: any) => {
  loading.value = true;
  const req = api.content;
  req.id = api.api_id;
  req.env_id = env_id.value;
  const res: any = await api_send(req);
  loading.value = false;
  api.res = res.data;
  api.res.body = JSON.parse(api.res.body);
};

const markdown_koiDialogRef = ref();
const markdown_info = ref<any>({});
const view_document = async (markdown: any) => {
  markdown_info.value = markdown;
  markdown_koiDialogRef.value.koiOpen();
};

const history_list = ref<any>([]);
const history_searchParams = ref<any>({
  currentPage: 1,
  pageSize: 10,
  search: {}
});
const history_total = ref<any>(0);
const history_koiDialogRef = ref();
const api_history = async (api: any) => {
  history_searchParams.value.search.api_id = api.api_id;
  const res: any = await req_history(history_searchParams.value);
  history_list.value = res.data.content;
  history_total.value = res.data.total;
  title.value = "请求历史记录";
  history_koiDialogRef.value.koiOpen();
};

const edit_history_list = ref<any>([]);
const edit_history_koiDrawerRef = ref();
const edit_history = async (api: any) => {
  const res: any = await api_edit_history({
    api_id: api.api_id
  });
  edit_history_list.value = res.data;
  title.value = "编辑记录";
  edit_history_koiDrawerRef.value.koiOpen();
};

const history_koiDrawerRef = ref();
const history_detail = ref<any>({});
const view_detail = async (row: any) => {
  history_detail.value = row;
  history_koiDrawerRef.value.koiOpen();
};
// 初始化数据
onMounted(() => {
  getProjectList();
  get_api_tree_list();
  get_db_list();
});
</script>

<template>
  <div style="">
    <div v-loading="api_loading" :element-loading-text="loading_text">
      <KoiCard style="height: 805px">
        <div v-show="show_type === 'project'" style="">
          <el-row :gutter="15">
            <el-col style="padding-block-end: 5px" :span="3" :lg="4" :md="3" :sm="3" :xs="3"
              v-for="(item, index) in project_list" :key="index">
              <el-card class="rounded-md" shadow="hover">
                <div class="flex justify-center">
                  <el-image :src="item.img" style="border-radius: 10px; width: 120px; height: 120px"
                    @click.native="into_Service(item.id)" />
                </div>
                <div class="flex justify-center" style="padding-top: 10px">
                  <span>{{ item.name }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>
          <div class="h-20px"></div>
          <div class="flex justify-center">
            <el-pagination v-model:current-page="project_searchParams.currentPage"
              v-model:page-size="project_searchParams.pageSize" :total="project_total" :page-sizes="[18, 36, 50]"
              layout="total, sizes, prev, pager, next, jumper" @size-change="getProjectList"
              @current-change="getProjectList" />
          </div>
        </div>
        <div v-show="show_type === 'service'" style="">
          <el-button type="text" @click="back_project"><el-icon>
              <Back />
            </el-icon>返回选择项目</el-button>
          <div class="h-5px"></div>
          <el-row :gutter="15">
            <el-col style="padding-block-end: 5px" :span="3" :lg="4" :md="3" :sm="3" :xs="3"
              v-for="(item, index) in service_list" :key="index">
              <el-card class="rounded-md" shadow="hover">
                <div class="flex justify-center">
                  <el-image :src="item.img" style="border-radius: 10px; width: 120px; height: 120px"
                    @click="into_Api(item.id)" />
                </div>
                <div class="flex justify-center" style="padding-top: 10px">
                  <span>{{ item.name }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>
          <div class="h-20px"></div>
          <div class="flex justify-center">
            <el-pagination v-model:current-page="service_searchParams.currentPage"
              v-model:page-size="service_searchParams.pageSize" :total="service_total" :page-sizes="[18, 36, 50]"
              layout="total, sizes, prev, pager, next, jumper" @size-change="getService" @current-change="getService" />
          </div>
        </div>
        <div v-show="show_type === 'api'">
          <div style="width: 97.7%; border: 1px solid #e4e7ed; border-radius: 5px; padding: 5px">
            <el-button type="primary" @click="back_project" plain><el-icon>
                <Back />
              </el-icon>返回选择项目</el-button>
            <el-button type="info" style="float: right" plain icon="View" @click="Editenv"></el-button>
            <el-select v-model="env_id" placeholder="选择域名" style="width: 10%; float: right; padding-left: 50px">
              <el-option v-for="(env, index) in env_list" :key="index" :label="'环境：' + env.name" :value="env.id">
              </el-option>
            </el-select>
            <el-popover :width="800" trigger="click">
              <template #reference>
                <el-button type="text" style="float: right" icon="CircleCloseFilled">错误码管理</el-button>
              </template>
              <div>
                <api_code />
              </div>
            </el-popover>
            <el-popover :width="1000" trigger="click">
              <template #reference>
                <el-button type="text" style="float: right" icon="Tools">公共函数</el-button>
              </template>
              <div>
                <api_function />
              </div>
            </el-popover>
            <el-popover :width="1300" trigger="click">
              <template #reference>
                <el-button type="text" style="float: right" icon="Coin">直连数据库</el-button>
              </template>
              <div>
                <api_db />
              </div>
            </el-popover>
            <el-popover :width="1000" trigger="click">
              <template #reference>
                <el-button type="text" style="float: right" icon="Key">参数依赖</el-button>
              </template>
              <div>
                <api_params />
              </div>
            </el-popover>
            <el-popover :width="800" trigger="click">
              <template #reference>
                <el-button type="text" style="float: right" icon="Mouse">工具箱</el-button>
              </template>
              <div>
                <el-tabs v-model="tool_active" class="demo-tabs">
                  <el-tab-pane label="在线加解密" name="second">
                    <encryption />
                  </el-tab-pane>
                  <el-tab-pane label="时间戳转换" name="third">
                    <time_change />
                  </el-tab-pane>
                </el-tabs>
              </div>
            </el-popover>
          </div>
          <div style="width: 100%">
            <div
              style="width: 22%; border: 1px solid #e4e7ed; padding: 5px; border-radius: 5px; height: 750px; float: left">
              <el-select v-model="api_service_id" placeholder="请选择服务" style="margin-block-end: 10px; width: 85%"
                @change="into_Api">
                <el-option v-for="item in service_list" :key="item.id" :label="'服务：' + item.name" :value="item.id">
                </el-option>
              </el-select>
              <div>
                <el-input v-model="filterText" class="w-60 mb-2" placeholder="Filter keyword" style="width: 85%" />
                <el-button type="text" style="padding-left: 10px" icon="Refresh" @click="get_tree()" />
              </div>
              <div style="overflow-y: auto; height: 685px">
                <el-tree ref="treeRef" :data="tree_data" :props="{ children: 'children', label: 'name' }"
                  style="width: 100%" :default-expand-all="true">
                  <template #default="{ node, data }">
                    <span class="custom-tree-node" @click="menu_click(data)" style="width: 100%">
                      <span style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap"
                        v-if="data.type === 0"><el-icon style="padding-right: 5px">
                          <HomeFilled />
                        </el-icon>{{ node.label }}</span>
                      <span v-if="data.type === 1"
                        style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap"><el-icon
                          style="padding-right: 5px">
                          <Folder />
                        </el-icon>{{ node.label + "(" + data.children.length + ")" }}</span>
                      <span style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap"
                        v-if="data.type === 2">
                        <SvgIcon style="padding-right: 5px" name="API3" width="15" height="14"> </SvgIcon>{{ node.label
                        }}
                      </span>
                      <span v-if="data.type === 3"
                        style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap"><el-icon
                          style="padding-right: 5px">
                          <Link />
                        </el-icon>{{ node.label }}</span>
                    </span>
                    <span v-if="data.type === 0" class="right" style="padding-right: 10px; padding-top: 5px">
                      <el-dropdown placement="bottom">
                        <el-icon>
                          <MoreFilled />
                        </el-icon>
                        <span class="el-dropdown-link" style="font-size: 20px" />
                        <template #dropdown>
                          <el-dropdown-menu class="header-new-drop">
                            <el-dropdown-item icon="CirclePlus" @click="AddMenu(data)">新建子菜单</el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </span>
                    <span v-if="data.type === 1" class="right" style="padding-right: 10px; padding-top: 5px">
                      <el-dropdown placement="bottom">
                        <el-icon>
                          <MoreFilled />
                        </el-icon>
                        <span class="el-dropdown-link" style="font-size: 20px" />
                        <template #dropdown>
                          <el-dropdown-menu class="header-new-drop">
                            <el-dropdown-item icon="CirclePlus" @click="AddMenu(data)">新建子菜单</el-dropdown-item>
                            <el-dropdown-item icon="Edit" @click="EditMenu(data)">重命名</el-dropdown-item>
                            <el-dropdown-item icon="Remove" @click="DelMenu(data)">删除</el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </span>
                    <span v-if="data.type === 2" class="right" style="padding-right: 10px; padding-top: 5px">
                      <el-dropdown placement="bottom">
                        <el-icon>
                          <MoreFilled />
                        </el-icon>
                        <span class="el-dropdown-link" style="font-size: 20px" />
                        <template #dropdown>
                          <el-dropdown-menu class="header-new-drop">
                            <el-dropdown-item icon="CopyDocument" @click="CopyMenu(data)">复制</el-dropdown-item>
                            <el-dropdown-item icon="Edit" @click="EditMenu(data)">重命名</el-dropdown-item>
                            <el-dropdown-item icon="Remove" @click="DelMenu(data)">删除</el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </span>
                    <span v-if="data.type === 3" class="right" style="padding-right: 10px; padding-top: 5px">
                      <el-dropdown placement="bottom">
                        <el-icon>
                          <MoreFilled />
                        </el-icon>
                        <span class="el-dropdown-link" style="font-size: 20px" />
                        <template #dropdown>
                          <el-dropdown-menu class="header-new-drop">
                            <el-dropdown-item icon="CopyDocument" @click="CopyMenu(data)">复制</el-dropdown-item>
                            <el-dropdown-item icon="Edit" @click="EditMenu(data)">重命名</el-dropdown-item>
                            <el-dropdown-item icon="Remove" @click="DelMenu(data)">删除</el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </span>
                  </template>
                </el-tree>
              </div>
            </div>
            <div
              style="width: 75%; border: 1px solid #e4e7ed; padding: 5px; border-radius: 5px; height: 750px; float: left">
              <div>
                <el-tabs v-model="tab_active" type="card" closable class="demo-tabs" @tab-remove="removeTab"
                  @tab-click="tab_click">
                  <el-tab-pane v-for="(item, index) in tab_list" :key="index" :label="item.title" :name="item.name">
                    <template #label>
                      <span v-if="item.type === 1"><el-icon style="padding-right: 5px">
                          <Folder />
                        </el-icon>{{ item.title }}</span>
                      <span v-if="item.type === 2">
                        <SvgIcon style="padding-right: 5px" name="API3" width="15" height="14"> </SvgIcon>{{ item.title
                        }}
                      </span>
                      <span v-if="item.type === 3"><el-icon style="padding-right: 5px">
                          <Link />
                        </el-icon>{{ item.title }}</span>
                    </template>
                    <div v-show="item.type === 1"></div>
                    <div v-loading="loading" element-loading-text="正在请求接口..." v-show="item.type !== 1">
                      <div style="border: 1px solid #e4e7ed; width: 98%; padding: 5px; border-radius: 5px">
                        <div>
                          <el-select v-model="item.content.req.method" placeholder="选择请求方法" style="width: 10%">
                            <el-option v-for="(method, index) in method_list" :key="index" :label="method.name"
                              :value="method.value">
                            </el-option>
                          </el-select>
                          <el-input v-model="item.content.url" placeholder="请输入请求地址" clearable
                            style="width: 40%; margin-left: 10px; margin-right: 10px">
                          </el-input>
                          <el-button type="primary" icon="Position" plain @click="SendRequest(item)">发送请求</el-button>
                          <el-dropdown placement="top" style="padding-left: 10px">
                            <el-button type="warning" icon="Download" plain>保存项<el-icon
                                class="el-icon--right"><arrow-down /></el-icon>
                            </el-button>
                            <template #dropdown>
                              <el-dropdown-menu>
                                <el-dropdown-item @click="saveApi(item)">直接保存</el-dropdown-item>
                                <el-dropdown-item @click="saveApiCase(item)">保存为用例</el-dropdown-item>
                              </el-dropdown-menu>
                            </template>
                          </el-dropdown>
                          <el-button type="info" icon="Refresh" plain @click="view_document(item.content.document)"
                            style="float: right">接口文档</el-button>
                          <el-button type="info" icon="Timer" plain @click="api_history(item)"
                            style="float: right">调试记录</el-button>
                          <el-button type="info" icon="Timer" plain @click="edit_history(item)"
                            style="float: right">编辑记录</el-button>
                        </div>
                      </div>
                      <div
                        style="border: 1px solid #e4e7ed; border-radius: 5px; width: 98%; padding-left: 10px; height: 320px">
                        <el-tabs v-model="req_active" class="demo-tabs">
                          <el-tab-pane label="Params" name="params">
                            <template #label>
                              <el-badge :show-zero="false" :value="item.content.req.params.length" :offset="[13, 2]"
                                type="primary">
                                Params
                              </el-badge>
                            </template>
                            <div style="width: 100%; overflow: auto; height: 250px">
                              <div style="width: 100%; padding-block-end: 5px">
                                <el-button type="primary" icon="Plus" plain
                                  @click="add_params(item.content.req.params)">添加url参数</el-button>
                              </div>
                              <div v-for="(params, index) in item.content.req.params" :key="index"
                                style="padding-block-end: 5px">
                                <el-checkbox v-model="params.status" />
                                <el-input v-model="params.key" placeholder="请输入参数key"
                                  style="width: 40%; padding-left: 10px">
                                </el-input>
                                <el-input v-model="params.value" placeholder="请输入参数value"
                                  style="width: 40%; padding-left: 10px; padding-right: 10px">
                                </el-input>
                                <el-button type="danger" icon="Delete" plain
                                  @click="remove_params(item.content.req.params, index)">删除</el-button>
                              </div>
                            </div>
                          </el-tab-pane>
                          <el-tab-pane label="Header" name="header">
                            <template #label>
                              <el-badge :show-zero="false" :value="item.content.req.header.length" :offset="[13, 2]"
                                type="primary">
                                Header
                              </el-badge>
                            </template>
                            <div style="width: 100%; overflow: auto; height: 250px">
                              <div style="width: 100%; padding-block-end: 5px">
                                <el-button type="primary" icon="Plus" plain
                                  @click="add_params(item.content.req.header)">添加Header配置</el-button>
                              </div>
                              <div v-for="(header, index) in item.content.req.header" :key="index"
                                style="padding-block-end: 5px">
                                <el-checkbox v-model="header.status" />
                                <el-input v-model="header.key" placeholder="请输入参数key"
                                  style="width: 40%; padding-left: 10px">
                                </el-input>
                                <el-input v-model="header.value" placeholder="请输入参数value"
                                  style="width: 40%; padding-left: 10px; padding-right: 10px">
                                </el-input>
                                <el-button type="danger" icon="Delete" plain
                                  @click="remove_params(item.content.req.header, index)">删除</el-button>
                              </div>
                            </div>
                          </el-tab-pane>
                          <el-tab-pane label="Body" name="body">
                            <div style="width: 100%; height: 260px">
                              <div style="width: 13%; float: right; padding-right: 40px; padding-left: 5px">
                                <el-select style="width: 120%; padding-block-end: 30px"
                                  v-model="item.content.req.params_id" clearable placeholder="非必选：选择参数依赖">
                                  <el-option v-for="(params, index) in params_list" :key="index" :label="params.name"
                                    :value="params.id">
                                  </el-option>
                                </el-select>
                                <el-radio-group v-model="item.content.req.body_type">
                                  <el-radio :value="1" size="small">None</el-radio>
                                  <el-radio :value="2" size="small">raw-JSON</el-radio>
                                  <el-radio :value="3" size="small">form-data</el-radio>
                                  <el-radio :value="4" size="small">form-urlencoded</el-radio>
                                  <el-radio :value="5" size="small">binary</el-radio>
                                </el-radio-group>
                              </div>
                              <div v-if="item.content.req.body_type === 2" style="width: 83%; float: left">
                                <jsonE v-model:value="item.content.req.body" :height="'260px'" />
                                <!-- <jsonEditor v-model:code="item.content.req.body" :height="'260'" @call_back="body_back" /> -->
                              </div>
                              <div v-if="item.content.req.body_type === 3" style="width: 83%; float: left">
                                <div style="width: 100%; padding-block-end: 5px">
                                  <el-button type="primary" icon="Plus" plain
                                    @click="add_params(item.content.req.form_data)">添加formdata配置</el-button>
                                </div>
                                <div v-for="(form, index) in item.content.req.form_data" :key="index"
                                  style="padding-block-end: 5px">
                                  <el-checkbox v-model="form.status" />
                                  <el-input v-model="form.key" placeholder="请输入参数key"
                                    style="width: 40%; padding-left: 10px">
                                  </el-input>
                                  <el-input v-model="form.value" placeholder="请输入参数value"
                                    style="width: 40%; padding-left: 10px; padding-right: 10px">
                                  </el-input>
                                  <el-button type="danger" icon="Delete" plain
                                    @click="remove_params(item.content.req.form_data, index)">删除</el-button>
                                </div>
                              </div>
                              <div v-if="item.content.req.body_type === 4" style="width: 83%; float: left">
                                <div style="width: 100%; padding-block-end: 5px">
                                  <el-button type="primary" icon="Plus" plain
                                    @click="add_params(item.content.req.form_urlencoded)">添加formdata配置</el-button>
                                </div>
                                <div v-for="(form, index) in item.content.req.form_urlencoded" :key="index"
                                  style="padding-block-end: 5px">
                                  <el-checkbox v-model="form.status" />
                                  <el-input v-model="form.key" placeholder="请输入参数key"
                                    style="width: 40%; padding-left: 10px">
                                  </el-input>
                                  <el-input v-model="form.value" placeholder="请输入参数value"
                                    style="width: 40%; padding-left: 10px; padding-right: 10px">
                                  </el-input>
                                  <el-button type="danger" icon="Delete" plain
                                    @click="remove_params(item.content.req.form_urlencoded, index)">删除</el-button>
                                </div>
                              </div>
                              <div v-if="item.content.req.body_type === 5"
                                style="height: 260px; overflow: auto; width: 83%">
                                <div style="width: 40%; float: left">
                                  <div v-for="(file, index) in item.content.req.file_path" :key="index">
                                    <el-tag type="success">{{ "已上传成功：" + file }}</el-tag>
                                    <el-button style="padding-left: 10px; color: rgb(219 97 120)" type="text"
                                      icon="Delete" circle
                                      @click="remove_params(item.content.req.file_path, index)"></el-button>
                                  </div>
                                </div>
                                <div style="width: 50%; float: right">
                                  <el-button plain icon="Back" type="danger" style="float: left"
                                    @click="add_file">二次确认上传</el-button>
                                  <KoiUploadFiles v-model="file_path" :multiple="true" :limit="9"
                                    :file-name="item.content.req.file_path" @fileSuccess="call_back_1"
                                    :acceptType="['*.*']" :acceptTypes="'所有文件类型;'" />
                                </div>
                              </div>
                            </div>
                          </el-tab-pane>
                          <el-tab-pane name="before">
                            <template #label>
                              <el-badge :show-zero="false" :value="item.content.req.before.length" :offset="[10, 2]"
                                type="primary">
                                前置操作
                              </el-badge>
                            </template>
                            <div>
                              <el-dropdown @command="add_before">
                                <el-button type="primary" plain icon="Plus">
                                  添加前置操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
                                </el-button>
                                <template #dropdown>
                                  <el-dropdown-menu>
                                    <el-dropdown-item divided :command="1">
                                      <SvgIcon style="padding-right: 5px" name="API3" width="14" height="14"> </SvgIcon>
                                      预请求接口
                                    </el-dropdown-item>
                                    <el-dropdown-item divided :command="2"><el-icon>
                                        <Operation />
                                      </el-icon>预设变量</el-dropdown-item>
                                    <el-dropdown-item divided :command="3"><el-icon>
                                        <Clock />
                                      </el-icon>等待时间</el-dropdown-item>
                                    <!-- <el-dropdown-item divided :command="4"
                                      ><el-icon><EditPen /></el-icon>自定义脚本</el-dropdown-item
                                    > -->
                                  </el-dropdown-menu>
                                </template>
                              </el-dropdown>
                              <div class="h-5px"></div>
                              <div style="padding: 5px; height: 220px; overflow-y: auto">
                                <el-collapse accordion>
                                  <el-collapse-item v-for="(pre, index) in item.content.req.before" :key="index">
                                    <template #title>
                                      <span>
                                        <el-button style="color: rgb(219 97 120)" type="text" icon="Delete"
                                          @click="remove_params(item.content.req.before, index)"></el-button>
                                        <span v-if="pre.type === 1">
                                          <SvgIcon style="padding-right: 5px" name="API3" width="14" height="14">
                                          </SvgIcon>
                                          <span>{{ index + 1 + ". 预请求接口：" + pre.title }}</span>
                                        </span>
                                        <span v-if="pre.type === 2">
                                          <el-icon class="header-icon">
                                            <Operation />
                                          </el-icon>
                                          {{ index + 1 + ". 预设变量：" + pre.name + " 赋值等于 " + pre.value }}
                                        </span>
                                        <span v-if="pre.type === 3">
                                          <el-icon class="header-icon" style="">
                                            <Clock />
                                          </el-icon>
                                          {{ index + 1 + ". 设置等待时长：" + pre.wait_time + "秒" }}
                                        </span>
                                        <span v-if="pre.type === 4">
                                          <el-icon class="header-icon">
                                            <EditPen />
                                          </el-icon>
                                          {{ index + 1 + ". 自定义脚本" + pre.title }}
                                        </span>
                                      </span>
                                    </template>
                                    <div v-if="pre.type === 1">
                                      <div>
                                        <el-form inline>
                                          <el-form-item label="操作名称：">
                                            <el-input style="width: 300px" v-model="pre.title"
                                              placeholder="请输入前置名称"></el-input>
                                          </el-form-item>
                                          <el-form-item label="选择环境：">
                                            <el-select placeholder="请选择环境地址" v-model="pre.env_id" style="width: 300px">
                                              <el-option v-for="(env, index) in env_list" :key="index" :label="env.name"
                                                :value="env.id"></el-option>
                                            </el-select>
                                          </el-form-item>
                                          <el-form-item label="选择接口：">
                                            <el-cascader :options="tree_list" v-model="pre.api_id"
                                              :props="{ value: 'id', label: 'name', children: 'children' }"
                                              style="width: 705px"></el-cascader>
                                          </el-form-item>
                                        </el-form>
                                      </div>
                                    </div>
                                    <div v-if="pre.type === 2">
                                      <el-form inline>
                                        <el-form-item label="变量名：">
                                          <el-input style="width: 200px" v-model="pre.name"
                                            placeholder="请输入变量名"></el-input>
                                        </el-form-item>
                                        <el-form-item label="变量类型：">
                                          <el-select placeholder="请选择变量类型" v-model="pre.env_type" style="width: 200px">
                                            <el-option v-for="(type, index) in val_type_list" :key="index"
                                              :label="type.name" :value="type.value"></el-option>
                                          </el-select>
                                        </el-form-item>
                                        <el-form-item label="预期值：">
                                          <el-input style="width: 200px" v-model="pre.value"
                                            placeholder="请输入预期值"></el-input>
                                        </el-form-item>
                                      </el-form>
                                    </div>
                                    <div v-if="pre.type === 3">
                                      <div>
                                        <el-form inline>
                                          <el-form-item label="等待时间(秒)：">
                                            <el-input-number style="width: 200px" :min="0" :max="60"
                                              v-model="pre.wait_time" placeholder="请输入等待时间"></el-input-number>
                                          </el-form-item>
                                        </el-form>
                                      </div>
                                    </div>
                                    <div v-if="pre.type === 4">
                                      <div>
                                        <div>
                                          <pythoneditor v-model:value="pre.code" />
                                        </div>
                                        <div style="float: right"></div>
                                      </div>
                                    </div>
                                  </el-collapse-item>
                                </el-collapse>
                              </div>
                            </div>
                          </el-tab-pane>
                          <el-tab-pane name="after">
                            <template #label>
                              <el-badge :show-zero="false" :value="item.content.req.after.length" :offset="[10, 2]"
                                type="primary">
                                后置操作
                              </el-badge>
                            </template>
                            <div>
                              <el-dropdown @command="add_after">
                                <el-button type="primary" plain icon="Plus">
                                  添加后置操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
                                </el-button>
                                <template #dropdown>
                                  <el-dropdown-menu>
                                    <el-dropdown-item divided :command="1"><el-icon>
                                        <Operation />
                                      </el-icon>提取变量</el-dropdown-item>
                                    <el-dropdown-item divided :command="2"><el-icon>
                                        <Clock />
                                      </el-icon>等待时间</el-dropdown-item>
                                  </el-dropdown-menu>
                                </template>
                              </el-dropdown>
                              <div class="h-5px"></div>
                              <div style="padding: 5px; height: 220px; overflow-y: auto">
                                <el-collapse accordion>
                                  <el-collapse-item v-for="(after, index) in item.content.req.after" :key="index">
                                    <template #title>
                                      <span>
                                        <el-button style="color: rgb(219 97 120)" type="text" icon="Delete"
                                          @click="remove_params(item.content.req.after, index)"></el-button>
                                        <span v-if="after.type === 1">
                                          <el-icon class="header-icon">
                                            <Operation />
                                          </el-icon>
                                          {{
                                            index + 1 + ". 提取变量：提取 ' " + after.name + " ' 赋值给 ' " + after.value + " '"
                                          }}
                                        </span>
                                        <span v-if="after.type === 2">
                                          <el-icon class="header-icon" style="">
                                            <Clock />
                                          </el-icon>
                                          {{ index + 1 + ". 设置等待时长：" + after.wait_time + "秒" }}
                                        </span>
                                      </span>
                                    </template>
                                    <div v-if="after.type === 1">
                                      <el-form inline>
                                        <el-form-item>
                                          <template #label>
                                            <el-tooltip :content="tips" raw-content>
                                              <el-button type="text" style="color: #000" icon="InfoFilled"></el-button>
                                            </el-tooltip>
                                            路径:
                                          </template>
                                          <el-input style="width: 300px" v-model="after.name"
                                            placeholder="请输入路径"></el-input>
                                        </el-form-item>
                                        <el-form-item label="提取目标:">
                                          <el-select placeholder="请选择提取目标" v-model="after.res_type"
                                            style="width: 300px">
                                            <el-option v-for="(res, index) in res_type_list" :key="index"
                                              :label="res.name" :value="res.value"></el-option>
                                          </el-select>
                                        </el-form-item>
                                        <el-form-item label="变量类型:">
                                          <el-select placeholder="请选择变量类型" v-model="after.env_type"
                                            style="width: 300px">
                                            <el-option v-for="(type, index) in val_type_list" :key="index"
                                              :label="type.name" :value="type.value"></el-option>
                                          </el-select>
                                        </el-form-item>
                                        <el-form-item label="变量名:">
                                          <el-input style="width: 300px" v-model="after.value"
                                            placeholder="请输入变量名"></el-input>
                                        </el-form-item>
                                      </el-form>
                                    </div>
                                    <div v-if="after.type === 2">
                                      <div>
                                        <el-form inline>
                                          <el-form-item label="等待时间(秒)：">
                                            <el-input-number style="width: 200px" :min="0" :max="60"
                                              v-model="after.wait_time" placeholder="请输入等待时间"></el-input-number>
                                          </el-form-item>
                                        </el-form>
                                      </div>
                                    </div>
                                  </el-collapse-item>
                                </el-collapse>
                              </div>
                            </div>
                          </el-tab-pane>
                          <el-tab-pane name="assert">
                            <template #label>
                              <el-badge :show-zero="false" :value="item.content.req.assert.length" :offset="[10, 2]"
                                type="primary">
                                断言
                              </el-badge>
                            </template>
                            <div>
                              <el-dropdown @command="add_assert">
                                <el-button type="primary" plain icon="Plus">
                                  添加断言<el-icon class="el-icon--right"><arrow-down /></el-icon>
                                </el-button>
                                <template #dropdown>
                                  <el-dropdown-menu>
                                    <el-dropdown-item divided :command="1"><el-icon>
                                        <CircleCheck />
                                      </el-icon>响应结果断言</el-dropdown-item>
                                    <el-dropdown-item divided :command="4"><el-icon>
                                        <Coin />
                                      </el-icon>直连-数据库断言</el-dropdown-item>
                                  </el-dropdown-menu>
                                </template>
                              </el-dropdown>
                              <div class="h-5px"></div>
                              <div style="padding: 5px; height: 220px; overflow-y: auto">
                                <el-collapse accordion>
                                  <el-collapse-item v-for="(assert, index) in item.content.req.assert" :key="index">
                                    <template #title>
                                      <span>
                                        <el-button style="color: rgb(219 97 120)" type="text" icon="Delete"
                                          @click="remove_params(item.content.req.assert, index)"></el-button>
                                        <span v-if="assert.type === 1">
                                          <el-icon class="header-icon">
                                            <CircleCheck />
                                          </el-icon>
                                          {{
                                            index + 1 + ". 响应断言：断言 ' " + assert.name + " ' 等于 ' " + assert.value + " '"
                                          }}
                                        </span>
                                        <span v-if="assert.type === 4">
                                          <el-icon class="header-icon">
                                            <Coin />
                                          </el-icon>
                                          {{
                                            index +
                                            1 +
                                            ". 直连-数据库断言：查询表 ' " +
                                            assert.local_db_table +
                                            " ' 条件： " +
                                            "' " +
                                            assert.local_db_where +
                                            " '"
                                          }}
                                        </span>
                                      </span>
                                    </template>
                                    <div v-if="assert.type === 1">
                                      <el-form inline>
                                        <el-form-item>
                                          <template #label>
                                            <el-tooltip :content="tips" raw-content>
                                              <el-button type="text" style="color: #000" icon="InfoFilled"></el-button>
                                            </el-tooltip>
                                            路径:
                                          </template>
                                          <el-input style="width: 220px" v-model="assert.name"
                                            placeholder="请输入路径"></el-input>
                                        </el-form-item>
                                        <el-form-item label="断言对象:">
                                          <el-select placeholder="请选择断言对象" v-model="assert.res_type"
                                            style="width: 220px">
                                            <el-option v-for="(res, index) in res_type_list" :key="index"
                                              :label="res.name" :value="res.value"></el-option>
                                          </el-select>
                                        </el-form-item>
                                        <el-form-item label="预期值:">
                                          <el-input style="width: 220px" v-model="assert.value"
                                            placeholder="请输入预期值"></el-input>
                                        </el-form-item>
                                      </el-form>
                                    </div>
                                    <div v-if="assert.type == 4">
                                      <div style="width: 100%">
                                        <div style="width: 40%; float: left; padding-right: 50px">
                                          <el-form>
                                            <el-form-item label="添加直连-数据库断言配置:">
                                              <el-button type="primary" plain icon="Plus"
                                                @click="add_redis_assert(assert.local_db_assert)">添加直连-数据库断言配置</el-button>
                                            </el-form-item>
                                            <el-form-item label="选择数据库:">
                                              <el-select v-model="assert.local_db">
                                                <el-option v-for="(db, index) in local_db_list" :key="index"
                                                  :label="db.name" :value="db.id"></el-option>
                                              </el-select>
                                            </el-form-item>
                                            <el-form-item label="数据库表:">
                                              <el-input v-model="assert.local_db_table"
                                                placeholder="请输入数据库表名"></el-input>
                                            </el-form-item>
                                            <el-form-item label="条件(where):">
                                              <el-input v-model="assert.local_db_where"
                                                placeholder="请输入筛选条件，与where条件一致，例：game_id=50001 and xxx=xxx"></el-input>
                                            </el-form-item>
                                          </el-form>
                                        </div>
                                        <div style="
                                            width: 50%;
                                            float: left;
                                            border: 1px solid #e4e7ed;
                                            padding: 5px;
                                            height: 150px;
                                            overflow-y: auto;
                                            border-radius: 5px;
                                          ">
                                          <div v-for="(form, index) in assert.local_db_assert" :key="index"
                                            style="padding-block-end: 5px">
                                            <el-input v-model="form.name" placeholder="请输入表字段名"
                                              style="width: 30%; padding-left: 10px">
                                            </el-input>
                                            <el-select placeholder="请断言目标" v-model="form.type"
                                              style="width: 25%; padding-left: 10px ">
                                              <el-option v-for="(res, index) in res_type_list" :key="index"
                                                :label="res.name" :value="res.value"></el-option>
                                            </el-select>
                                            <el-input v-model="form.value" placeholder="请输入预期值"
                                              style="width: 30%; padding-left: 10px; padding-right: 10px">
                                            </el-input>
                                            <el-button type="danger" icon="Delete" plain
                                              @click="remove_params(assert.local_db_assert, index)">删除</el-button>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </el-collapse-item>
                                </el-collapse>
                              </div>
                            </div>
                          </el-tab-pane>
                          <el-tab-pane label="配置" name="config">
                            <div>
                              <el-form v-model="item.content.req.config" label-position="right">
                                <el-form-item label="重试次数(次)：">
                                  <el-input-number v-model="item.content.req.config.retry"></el-input-number>
                                </el-form-item>
                                <el-form-item label="接口连接超时(秒)：">
                                  <el-input-number v-model="item.content.req.config.req_timeout"></el-input-number>
                                </el-form-item>
                                <el-form-item label="结果读取超时(秒)：">
                                  <el-input-number v-model="item.content.req.config.res_timeout"></el-input-number>
                                </el-form-item>
                              </el-form>
                            </div>
                          </el-tab-pane>
                        </el-tabs>
                      </div>
                      <div
                        style="border: 1px solid #e4e7ed; border-radius: 5px; width: 98%; padding-left: 10px; height: 320px">
                        <el-tabs v-model="res_active" class="demo-tabs">
                          <el-tab-pane label="响应-结果" name="res">
                            <div>
                              <vue-json-pretty v-model:data="item.res.body" :height="260" :showIcon="true"
                                :showLine="true" :virtual="true" :showSelectController="true" />
                            </div>
                          </el-tab-pane>
                          <el-tab-pane label="响应-Header" name="res_log">
                            <div>
                              <vue-json-pretty v-model:data="item.res.header" :height="260" :showIcon="true"
                                :showLine="true" :virtual="true" :showSelectController="true" />
                            </div>
                          </el-tab-pane>
                          <el-tab-pane name="before_res">
                            <template #label>
                              <el-badge :show-zero="false" :value="item.res.before.length" :offset="[10, 2]"
                                type="danger">前置操作结果</el-badge>
                            </template>
                            <div style="padding-left: 10px; height: 260px; overflow-y: auto">
                              <el-collapse>
                                <el-collapse-item v-for="(before, index) in item.res.before">
                                  <template #title>
                                    <span v-if="before.status === 0" style="color: rgb(219, 97, 120)">{{
                                      index + 1 + ". " + before.message
                                    }}</span>
                                    <span v-if="before.status === 1" style="color: rgb(46, 134, 234)">{{
                                      index + 1 + ". " + before.message
                                    }}</span>
                                  </template>
                                  <div v-if="before.type === 1">
                                    <vue-json-pretty v-model:data="before.content.body" :height="160" :showIcon="true"
                                      :showLine="true" :virtual="true" :showSelectController="true" />
                                  </div>
                                </el-collapse-item>
                              </el-collapse>
                            </div>
                          </el-tab-pane>
                          <el-tab-pane name="after_res">
                            <template #label>
                              <el-badge :show-zero="false" :value="item.res.after.length" :offset="[10, 2]"
                                type="danger">后置操作结果</el-badge>
                            </template>
                            <div style="padding-left: 10px; height: 260px; overflow-y: auto">
                              <el-collapse>
                                <el-collapse-item v-for="(after, index) in item.res.after">
                                  <template #title>
                                    <span v-if="after.status === 0" style="color: rgb(219, 97, 120)">{{
                                      index + 1 + ". " + after.message
                                    }}</span>
                                    <span v-if="after.status === 1" style="color: rgb(46, 134, 234)">{{
                                      index + 1 + ". " + after.message
                                    }}</span>
                                  </template>
                                </el-collapse-item>
                              </el-collapse>
                            </div>
                          </el-tab-pane>
                          <el-tab-pane label="断言结果" name="assert_res">
                            <template #label>
                              <el-badge :show-zero="false" :value="item.res.assert.length" :offset="[10, 2]"
                                type="danger">断言结果</el-badge>
                            </template>
                            <div style="padding-left: 10px; height: 260px; overflow-y: auto">
                              <el-collapse>
                                <el-collapse-item v-for="(assert, index) in item.res.assert">
                                  <template #title>
                                    <span v-if="assert.status === 0" style="color: rgb(219, 97, 120)">{{
                                      index + 1 + ". " + assert.message
                                    }}</span>
                                    <span v-if="assert.status === 1" style="color: rgb(46, 134, 234)">{{
                                      index + 1 + ". " + assert.message
                                    }}</span>
                                  </template>
                                </el-collapse-item>
                              </el-collapse>
                            </div>
                          </el-tab-pane>
                          <el-tab-pane disabled style="float: right">
                            <template #label>
                              <div class="tab-info">
                                <i class="el-icon-monitor" style="font-size: 16px" />
                                <span v-if="item.res.code === 0 || item.res.code === 200" slot="code"
                                  class="code">状态码：{{ item.res.code }}</span>
                                <span v-if="item.res.code !== 0 && item.res.code !== 200" slot="code" class="code"
                                  style="color: rgb(219, 97, 120)">状态码：{{ item.res.code }}</span>
                              </div>
                            </template>
                          </el-tab-pane>
                          <el-tab-pane disabled>
                            <template #label>
                              <div class="tab-info">
                                <i class="el-icon-document" style="font-size: 16px" />
                                <span v-if="item.res.code === 0 || item.res.code === 200" slot="size"
                                  class="size">资源大小：{{ item.res.size }} B</span>
                                <span v-if="item.res.code !== 0 && item.res.code !== 200" slot="size" class="size"
                                  style="color: rgb(219, 97, 120)">资源大小：{{ item.res.size }} B</span>
                              </div>
                            </template>
                          </el-tab-pane>
                          <el-tab-pane disabled>
                            <template #label>
                              <div class="tab-info">
                                <i class="el-icon-time" style="font-size: 16px" />
                                <span v-if="item.res.code === 0 || item.res.code === 200" slot="size"
                                  class="size">响应时间：{{ item.res.res_time }} ms</span>
                                <span v-if="item.res.code !== 0 && item.res.code !== 200" slot="size" class="size"
                                  style="color: rgb(219, 97, 120)">响应时间：{{ item.res.res_time }} ms</span>
                              </div>
                            </template>
                          </el-tab-pane>
                        </el-tabs>
                      </div>
                    </div>
                    <div v-show="item.type === 3"></div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </div>
          </div>
        </div>
      </KoiCard>
    </div>
    <div>
      <KoiDialog ref="env_koiDialogRef" :title="title" @koi-confirm="add_env_confirm" @koi-cancel="add_env_cancel"
        :before-close-check="false" :height="640" :width="900">
        <template #content>
          <el-tabs v-model="env_active" tab-position="left">
            <el-tab-pane label="全局变量：" name="overall">
              <div>
                <api_var />
              </div>
            </el-tab-pane>
            <el-tab-pane name="env" disabled></el-tab-pane>
            <el-tab-pane v-for="(env, index) in env_list" :label="env.name" :name="env.name" :key="index">
              <div>
                <el-form ref="formRef" label-width="80px" status-icon inline>
                  <el-form-item label="名称：" prop="roleName">
                    <el-input v-model="env.name" placeholder="请输入名称" clearable />
                  </el-form-item>
                  <el-form-item label="环境配置：">
                    <div style="padding-block-end: 5px">
                      <el-button type="primary" plain icon="Plus" @click="add_env_config(env.config)">添加环境配置</el-button>
                    </div>
                    <div style="padding-block-end: 5px" v-for="(config, index) in env.config" :key="index">
                      <el-input v-model="config.name" placeholder="请输入变量名" style="width: 200px"> </el-input>
                      <el-input v-model="config.value" placeholder="请输入域名"
                        style="width: 300px; padding-left: 10px; padding-right: 10px">
                      </el-input>
                      <el-button type="danger" icon="Delete" plain
                        @click="remove_params(env.config, index)">删除</el-button>
                    </div>
                  </el-form-item>
                  <el-form-item label="环境变量：">
                    <div style="padding-block-end: 5px">
                      <el-button type="primary" plain icon="Plus"
                        @click="add_env_config(env.variable)">添加环境变量配置</el-button>
                    </div>
                    <div style="padding-block-end: 5px" v-for="(vars, index) in env.variable" :key="index">
                      <el-input v-model="vars.name" placeholder="请输入变量名" style="width: 200px"> </el-input>
                      <el-input v-model="vars.value" placeholder="请输入域名"
                        style="width: 300px; padding-left: 10px; padding-right: 10px">
                      </el-input>
                      <el-button type="danger" icon="Delete" plain
                        @click="remove_params(env.variable, index)">删除</el-button>
                    </div>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
        </template>
      </KoiDialog>
    </div>
    <div>
      <KoiDialog ref="add_koiDialogRef" :title="title" @koi-confirm="add_menu_confirm" @koi-cancel="add_menu_cancel"
        :height="100">
        <template #content>
          <el-form ref="formRef" :model="add_form" label-width="80px" status-icon>
            <el-form-item label="名称：" prop="roleName">
              <el-input v-model="add_form.name" placeholder="请输入名称" clearable />
            </el-form-item>
            <el-form-item label="类型：" prop="roleCode">
              <el-radio-group v-model="add_form.type">
                <el-radio :value="1">文件夹</el-radio>
                <el-radio :label="2">接口</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </template>
      </KoiDialog>
    </div>
    <div>
      <KoiDialog ref="edit_koiDialogRef" :title="title" @koi-confirm="edit_menu_confirm" @koi-cancel="edit_menu_cancel"
        :height="100">
        <template #content>
          <el-form ref="formRef" :model="add_form" label-width="80px" status-icon>
            <el-form-item label="名称：" prop="roleName">
              <el-input v-model="add_form.name" placeholder="请输入名称" clearable />
            </el-form-item>
            <el-form-item label="类型：" prop="roleCode">
              <el-radio-group disabled v-model="add_form.type">
                <el-radio :value="1">文件夹</el-radio>
                <el-radio :label="2">接口</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </template>
      </KoiDialog>
    </div>
    <div>
      <KoiDialog ref="history_koiDialogRef" :title="title" :height="600" :before-close-check="false"
        :footer-hidden="true" :width="1500">
        <template #content>
          <div style="">
            <div class="h-10px"></div>
            <el-table border :data="history_list" style="border-radius: 5px">
              <el-table-column prop="id" label="ID" width="100"></el-table-column>
              <el-table-column label="url">
                <template #default="{ row }">{{ row.req.url }}</template>
              </el-table-column>
              <el-table-column label="请求方法" width="80">
                <template #default="{ row }">
                  <span>
                    <el-tag v-if="row.req.method === 1" type="success">GET</el-tag>
                    <el-tag v-if="row.req.method === 2" type="danger">POST</el-tag>
                    <el-tag v-if="row.req.method === 3" type="warning">PUT</el-tag>
                    <el-tag v-if="row.req.method === 4" type="info">DELETE</el-tag>
                    <el-tag v-if="row.req.method === 5" type="info">PATCH</el-tag>
                    <el-tag v-if="row.req.method === 6" type="info">OPTIONS</el-tag>
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="请求结果" prop="res" :show-overflow-tooltip="true">
                <template #default="{ row }">{{ row.res }}</template>
              </el-table-column>
              <el-table-column label="请求时间" prop="create_time" width="180"></el-table-column>
              <el-table-column label="操作人" prop="username" width="100"></el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="{ row }">
                  <el-button type="primary" icon="DocumentCopy" plain @click="view_detail(row)">查看详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="h-10px"></div>
            <el-pagination background v-model:current-page="history_searchParams.currentPage"
              v-model:page-size="history_searchParams.pageSize" v-show="history_total > 0" :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper" :total="history_total" @size-change="api_history"
              @current-change="api_history" />
          </div>
        </template>
      </KoiDialog>
    </div>
    <div>
      <KoiDrawer ref="history_koiDrawerRef" :title="'请求详情'" :footer-hidden="true" :size="1100"
        :beforeCloseCheck="false">
        <template #content>
          <div>
            <Api_detail :res="history_detail.res" :req="history_detail.req" :env_list="env_list" :tree_list="tree_list"
              :redis_example_list="redis_example_list" :local_db_list="local_db_list" />
          </div>
        </template>
      </KoiDrawer>
    </div>
    <div>
      <KoiDrawer ref="edit_history_koiDrawerRef" :title="title" :footer-hidden="true" :size="500"
        :beforeCloseCheck="false">
        <template #content>
          <div>
            <el-timeline style="width: 80%">
              <el-timeline-item center v-for="(edit, index) in edit_history_list" :key="index" type="info" size="large"
                icon="EditPen" :timestamp="'更新人' + edit.username + '-编辑时间：' + edit.create_time" placement="top">
                <div>
                  <el-table border :data="edit.edit">
                    <el-table-column label="字段名" prop="field" :show-overflow-tooltip="true"></el-table-column>
                    <el-table-column label="字段名" prop="type" width="60">
                      <template #default="{ row }">
                        <el-tag v-if="row.type === 'add'" type="success">新增</el-tag>
                        <el-tag v-if="row.type === 'delete'" type="danger">删除</el-tag>
                        <el-tag v-if="row.type === 'edit'" type="primary">编辑</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="更新值" :show-overflow-tooltip="true">
                      <template #default="{ row }">
                        {{ row.new }}
                      </template>
                    </el-table-column>
                    <el-table-column label="初始值" :show-overflow-tooltip="true">
                      <template #default="{ row }">
                        {{ row.old }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </template>
      </KoiDrawer>
    </div>
    <div>
      <KoiDialog ref="add_case_koiDialogRef" :title="title" @koi-confirm="add_case_confirm"
        @koi-cancel="add_case_cancel" :height="100">
        <template #content>
          <el-form ref="formRef" :model="add_form" label-width="80px" status-icon>
            <el-form-item label="名称：" prop="roleName">
              <el-input v-model="add_form.name" placeholder="请输入名称" clearable />
            </el-form-item>
          </el-form>
        </template>
      </KoiDialog>
    </div>
    <div>
      <KoiDialog ref="markdown_koiDialogRef" :title="'接口文档：' + markdown_info.name" :height="682"
        :before-close-check="false" :footer-hidden="true" :width="1200">
        <template #content>
          <div>
            <div style="padding: 10px">
              <h2>{{ "接口名称：" + markdown_info.name }}</h2>
              <h4 class="tip">
                <span class="doc-label">URL：{{ markdown_info.url }}</span>
              </h4>
              <h4>
                请求方法：
                <span v-if="markdown_info.httpMethod === 'GET'"><el-tag size="small" type="success"
                    style="border-radius: 30px">GET</el-tag></span>
                <span v-if="markdown_info.httpMethod === 'POST'"><el-tag size="small" type="danger"
                    style="border-radius: 30px">POST</el-tag></span>
                <span v-if="markdown_info.httpMethod === 'PUT'"><el-tag size="small" type="info"
                    style="border-radius: 30px">PUT</el-tag></span>
                <span v-if="markdown_info.httpMethod === 'DELETE'"><el-tag size="small" type="warning"
                    style="border-radius: 30px">DELETE</el-tag></span>
              </h4>
              <h4 class="doc-descr"><span class="doc-label">描述：</span></h4>
              <li>{{ markdown_info.description }}</li>
              <h4>
                <span class="doc-label">ContentType：</span><span class="content">{{ markdown_info.contentType }}</span>
              </h4>
              <h4 class="doc-descr"><span class="doc-label">路径参数：</span></h4>
              <el-table :data="markdown_info.queryParams" style="width: 100%" row-key="name" border default-expand-all
                :tree-props="{ children: 'children', hasChildren: 'hasChildren' }">
                <el-table-column label="名称">
                  <template #default="{ row }">
                    {{ row.name }}
                  </template>
                </el-table-column>
                <el-table-column label="类型">
                  <template #default="{ row }">
                    {{ row.type }}
                  </template>
                </el-table-column>
                <el-table-column label="必填">
                  <template #default="{ row }">
                    <span v-if="row.required === 1"><el-tag size="small" type="danger">是</el-tag></span>
                    <span v-if="row.required === 0"><el-tag size="small" type="info">否</el-tag></span>
                  </template>
                </el-table-column>
                <el-table-column label="最大长度">
                  <template #default="{ row }">
                    {{ row.maxLength }}
                  </template>
                </el-table-column>
                <el-table-column label="描述" align="left" :show-overflow-tooltip="true">
                  <template #default="{ row }">
                    {{ row.description }}
                  </template>
                </el-table-column>
                <el-table-column label="示例值" align="left" :show-overflow-tooltip="true">
                  <template #default="{ row }">
                    {{ row.example }}
                  </template>
                </el-table-column>
              </el-table>
              <h4 class="doc-descr"><span class="doc-label">请求头：</span></h4>
              <el-table :data="markdown_info.headerParams" style="width: 100%; margin-bottom: 20px" row-key="name"
                border default-expand-all :tree-props="{ children: 'children', hasChildren: 'hasChildren' }">
                <el-table-column label="名称">
                  <template #default="{ row }">
                    {{ row.name }}
                  </template>
                </el-table-column>
                <el-table-column label="类型">
                  <template #default="{ row }">
                    {{ row.type }}
                  </template>
                </el-table-column>
                <el-table-column label="必填">
                  <template #default="{ row }">
                    <span v-if="row.required === 1"><el-tag size="small" type="danger">是</el-tag></span>
                    <span v-if="row.required === 0"><el-tag size="small" type="info">否</el-tag></span>
                  </template>
                </el-table-column>
                <el-table-column label="最大长度">
                  <template #default="{ row }">
                    {{ row.maxLength }}
                  </template>
                </el-table-column>
                <el-table-column label="描述" align="left" :show-overflow-tooltip="true">
                  <template #default="{ row }">
                    {{ row.description }}
                  </template>
                </el-table-column>
                <el-table-column label="示例值" align="left" :show-overflow-tooltip="true">
                  <template #default="{ row }">
                    {{ row.example }}
                  </template>
                </el-table-column>
              </el-table>
              <h4 class="doc-descr"><span class="doc-label">Body：</span></h4>
              <el-table :data="markdown_info.requestParams" style="width: 100%; margin-bottom: 20px" row-key="name"
                border default-expand-all :tree-props="{ children: 'children', hasChildren: 'hasChildren' }">
                <el-table-column label="名称">
                  <template #default="{ row }">
                    {{ row.name }}
                  </template>
                </el-table-column>
                <el-table-column label="类型">
                  <template #default="{ row }">
                    {{ row.type }}
                  </template>
                </el-table-column>
                <el-table-column label="必填">
                  <template #default="{ row }">
                    <span v-if="row.required === 1"><el-tag size="small" type="danger">是</el-tag></span>
                    <span v-if="row.required === 0"><el-tag size="small" type="info">否</el-tag></span>
                  </template>
                </el-table-column>
                <el-table-column label="最大长度">
                  <template #default="{ row }">
                    {{ row.maxLength }}
                  </template>
                </el-table-column>
                <el-table-column label="描述" align="left" :show-overflow-tooltip="true">
                  <template #default="{ row }">
                    {{ row.description }}
                  </template>
                </el-table-column>
                <el-table-column label="示例值" align="left" :show-overflow-tooltip="true">
                  <template #default="{ row }">
                    {{ row.example }}
                  </template>
                </el-table-column>
              </el-table>
              <h4 class="doc-descr"><span class="doc-label">响应参数：</span></h4>
              <el-table :data="markdown_info.responseParams" style="width: 100%; margin-bottom: 20px" row-key="name"
                border default-expand-all :tree-props="{ children: 'children', hasChildren: 'hasChildren' }">
                <el-table-column label="名称">
                  <template #default="{ row }">
                    {{ row.name }}
                  </template>
                </el-table-column>
                <el-table-column label="类型">
                  <template #default="{ row }">
                    {{ row.type }}
                  </template>
                </el-table-column>
                <el-table-column label="描述" align="left" :show-overflow-tooltip="true">
                  <template #default="{ row }">
                    {{ row.description }}
                  </template>
                </el-table-column>
                <el-table-column label="示例值" align="left" :show-overflow-tooltip="true">
                  <template #default="{ row }">
                    {{ row.example }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </template>
      </KoiDialog>
    </div>
  </div>
</template>

<style>
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 15px;
  padding-right: 2px;
}

.el-collapse-item__content {
  padding-bottom: 5px !important;
}

.el-collapse-item__header {
  height: 35px !important;
}

.code,
.size {
  font-size: 14px;
  color: rgb(45, 23, 241);
  margin-left: 5px;
}
</style>
