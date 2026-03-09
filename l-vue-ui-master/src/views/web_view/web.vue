<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { ElTree } from "element-plus";
import { MsgBox, MsgError, MsgSuccess, NoticeError } from "@/utils/koi.ts";
import {
  web_menu,
  get_web_script,
  menu_script_list,
  run_web_script,
  get_web_result,
  get_web_result_log,
  add_web_menu,
  del_web_menu,
  rename_web_menu,
  save_script,
  input_element
} from "@/api/api_web/web";
import { get_element_select } from "@/api/api_web/element";
import { LocalStorage } from "@/utils/storage.ts";

// 数据表格加载页面动画
const loading = ref(false);
const filterText = ref<any>("");
const treeRef = ref<InstanceType<typeof ElTree>>();
const tree_data = ref<any>();
const defaultProps = {
  children: "children",
  label: "name"
};
// 当前页面的脚本数据
const script_list = ref<any>([]);
const script_info = ref<any>({
  action: {
    type: 1
  }
});
const table_list = ref<any>([]);
const tab_active = ref("");
const tab_list = ref<any>([]);
const add_menu_form = ref<any>({});
const locator_list = ref<any>([
  { name: "定位器", value: 1 },
  { name: "选择器", value: 2 }
]);
const locator_selects = ref<any>([
  { label: "id", value: 1 },
  { label: "text", value: 2 },
  { label: "label", value: 3 },
  { label: "title", value: 4 },
  { label: "placeholder", value: 5 },
  { label: "alt", value: 6 },
  { label: "role", value: 7 }
]);
const role_list = ref<any>([
  { label: "button", value: "button" },
  { label: "link", value: "link" },
  { label: "tab", value: "tab" },
  { label: "tab", value: "tab" },
  { label: "tabpanel", value: "tabpanel" },
  { label: "textbox", value: "textbox" },
  { label: "checkbox", value: "checkbox" },
  { label: "radio", value: "radio" },
  { label: "combobox", value: "combobox" },
  { label: "listbox", value: "listbox" },
  { label: "menu", value: "menu" },
  { label: "menuitem", value: "menuitem" },
  { label: "alert", value: "alert" },
  { label: "status", value: "status" },
  { label: "progressbar", value: "progressbar" },
  { label: "spinbutton", value: "spinbutton" },
  { label: "heading", value: "heading" },
  { label: "heading", value: "heading" },
  { label: "tree", value: "tree" },
  { label: "treeitem", value: "treeitem" }
]);
const browser_list = ref<any>([
  { name: "Chrome", value: 1 },
  { name: "Firefox", value: 2 },
  { name: "Edge", value: 3 },
  { name: "Safari", value: 4 }
]);

// web目录
watch(filterText, val => {
  treeRef.value!.filter(val);
});

const filterNode = (value: string, data: any): boolean => {
  if (!value) return true;
  return data.name.includes(value);
};

const element_select_change = (selection: any) => {
  console.log(selection);
};

const get_web_menu = async () => {
  try {
    loading.value = true;
    const res: any = await web_menu({});
    tree_data.value = res.data;
    loading.value = false;
  } catch {
    NoticeError("数据查询失败，请刷新重试🌻");
  }
};

const web_menu_click = async (node: any) => {
  try {
    if (node.type == 1) {
      const res: any = await menu_script_list({ id: node.id });
      table_list.value = res.data;
      await addTab(node, res.data);
    } else if (node.type == 2) {
      const res: any = await get_web_script({ id: node.id });
      script_info.value = res.data.script[0];
      await addTab(node, res.data);
    }
  } catch {
    NoticeError("数据查询失败，请刷新重试🌻");
  }
};

const addTab = async (node: any, target: any) => {
  const newTabName = node.name;
  const index = tab_list.value.findIndex((item: any) => item.title === newTabName);
  script_list.value = target.script;
  if (index === -1) {
    tab_list.value.push({
      title: newTabName,
      name: newTabName,
      content: target,
      id: node.id,
      type: node.type
    });
  }
  tab_active.value = node.name;
};

const removeTab = async (targetName: string) => {
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

const select_list = ref<any>([]);
const handleSelectionChange = (selection: any) => {
  select_list.value = selection.sort((a: any, b: any) => a.step - b.step);
};
const menu_form = ref<any>({
  name: "",
  id: null
});
const title = ref<string>("");
const add_koiDialogRef = ref();
const rename_koiDialogRef = ref();

const add_menu = async (data: any) => {
  title.value = "新增子菜单";
  add_koiDialogRef.value.koiOpen();
  menu_form.value = data;
};

const check_children = async (data: any, menu: any) => {
  if ("children" in data) {
    data.children.push(menu);
  } else {
    data.children = [];
    data.children.push(menu);
  }
};

const add_menu_confirm = async () => {
  try {
    add_menu_form.value.pid = menu_form.value.id;
    const res: any = await add_web_menu(add_menu_form.value);
    await check_children(menu_form.value, res.data);
    add_koiDialogRef.value.koiQuickClose(res.message);
  } catch {
    NoticeError("保存失败，请重试🌻");
  }
};

const add_menu_cancel = async () => {
  add_koiDialogRef.value.koiClose();
};

const rename_menu = async (data: any) => {
  title.value = "重命名";
  rename_koiDialogRef.value.koiOpen();
  menu_form.value = data;
};

const edit_menu_confirm = async () => {
  try {
    add_menu_form.value.id = menu_form.value.id;
    const res: any = await rename_web_menu(add_menu_form.value);
    rename_koiDialogRef.value.koiQuickClose(res.message);
    menu_form.value.name = add_menu_form.value.name;
  } catch {
    NoticeError("保存失败，请重试🌻");
  } finally {
    add_menu_form.value = {};
  }
};

const edit_menu_cancel = async () => {
  rename_koiDialogRef.value.koiClose();
};

const on_menu_allowDrop = (moveNode: any, inNode: any, type: any) => {
  console.log(moveNode);
  // 不允许同一层级内的inner操作
  if (inNode.data.type == 2) {
    return type !== "inner";
  } else {
    return type;
  }
};

const del_menu = async (data: any) => {
  MsgBox("您确认需要该目录么？").then(async () => {
    const res: any = await del_web_menu({ id: data.id, type: data.type });
    MsgSuccess(res.message);
    await get_web_menu();
  });
};

const random_string = (data_length: any) => {
  return Array.from(crypto.getRandomValues(new Uint8Array(data_length)))
    .map(n => n.toString(36))
    .join("");
};

// 自动化脚本
const add_script = (command: any) => {
  const new_string = random_string(2);
  script_list.value.push({
    name: command.name + "-" + new_string,
    type: command.type,
    status: true,
    children: [],
    action: {
      type: 1,
      locator: 1,
      locator_select: 1,
      target_locator: 1,
      target_locator_select: 1,
      input: "",
      element: "",
      element_id: null,
      target: "",
      target_id: "",
      target_type: 1,
      assert: [],
      up_type: 1,
      sway_type: 1,
      wait_time: 1,
      before_wait: 1,
      after_wait: 1,
      role: "button",
      cookies: [],
      localstorage: [],
      timeout: 15
    }
  });
};
const config_active = ref("first");
const assert_list = ref<any>([
  { name: "元素存在", value: 1 },
  { name: "元素不存在", value: 2 },
  { name: "文本存在", value: 3 },
  { name: "文本不存在", value: 4 },
  { name: "页面属性", value: 5 },
  { name: "自定义断言", value: 6 },
  { name: "AI 断言", value: 7 }
]);
const browser_assert = ref<any>([
  { name: "网页地址", value: 1 },
  { name: "网页标题", value: 2 }
]);
const add_assert = async (data: any) => {
  data.push({
    type: 1, // 断言类型
    locator: 1, // 选择器，定位器
    locator_select: 1, // 定位器类型
    page_type: 1, // 页面属性
    element: "", // 目标值
    role: "button"
  });
};

const add_cookie = async (data: any) => {
  data.push({
    name: "",
    value: ""
  });
};

const del_cookie = async (data: any, index: any) => {
  data.splice(index, 1);
};

const add_localstorage = async (data: any) => {
  data.push({
    name: "",
    value: ""
  });
};

const del_localstorage = async (data: any, index: any) => {
  data.splice(index, 1);
};

const del_assert = async (data: any, index: any) => {
  data.splice(index, 1);
};

const web_script_click = async (node: any) => {
  script_info.value = node;
  console.log(script_info.value);
};

const save_web_script = async (id: any) => {
  const res: any = await save_script({
    id: id,
    script: script_list.value
  });
  if (res.code === 200) {
    MsgSuccess(res.message);
  } else {
    NoticeError("保存失败，请重试🌻");
  }
};

const Delete_row = (script_list: any, data: any) => {
  script_list.forEach((item: any, index: any) => {
    if (item.name === data.name) {
      script_list.splice(index, 1);
    } else if (item.children.length > 0) {
      Delete_row(item.children, data);
    }
  });
  return false;
};

const copy_row = async (script_list: any, data: any) => {
  const new_string = "copy";
  const new_data = {
    name: data.name + "-" + new_string,
    type: data.type,
    status: true,
    children: [],
    action: {
      ...data.action
    }
  };
  script_list.push(new_data);
};

const element_select_list = ref<any>([]);
const element_select = async () => {
  const res: any = await get_element_select({});
  element_select_list.value = res.data;
};
const file_name = ref<any>(null);
const file_url = ref<any>(null);
const upload_koiDialogRef = ref<any>(null);
const call_back = async (fileMap: any) => {
  MsgSuccess("上传文件成功");
  file_url.value = fileMap.file_url;
  file_name.value = fileMap.filename;
};

const file_script_path = ref<any>("");
const call_back_1 = async (fileMap: any) => {
  file_script_path.value = fileMap.file_url + "/" + fileMap.filename;
};

const add_file = (action: any) => {
  action.input = file_script_path.value;
};

const pid = ref<any>(null);
const upload_file = async (data: any) => {
  pid.value = data.id;
  upload_koiDialogRef.value.koiOpen();
  title.value = "上传文件";
};

const upload_file_confirm = async () => {
  const res: any = await input_element({
    file_url: file_url.value,
    file_name: file_name.value,
    pid: pid.value
  });
  if (res.code === 200) {
    upload_koiDialogRef.value.koiQuickClose(res.message);
    await get_web_menu();
  } else {
    NoticeError("上传失败，请重试🌻");
  }
};

const upload_file_cancel = async () => {
  upload_koiDialogRef.value.koiQuickClose("取消上传");
};

const run_script_form = ref<any>({
  task_name: "",
  browser: [],
  script: [],
  width: 1920,
  height: 1080,
  browser_type: 1
});
const run_koiDialogRef = ref<any>(null);
const result_id = ref<any>("");
const run_script = async (item: any) => {
  run_script_form.value.script = [];
  run_koiDialogRef.value.koiOpen();
  title.value = "请配置调试信息";
  const script = {
    id: item.id,
    name: item.name,
    type: item.type
  };
  run_script_form.value.script.push(script);
};
const run_browsers = ref<any>([]);
const run_browser_active = ref<any>("");
const res_koiDialogRef = ref();
const run_script_confirm = async () => {
  if (run_script_form.value.script.length === 0) {
    MsgError("请选择脚本");
    return;
  }
  if (!run_script_form.value.task_name) {
    MsgError("请输入任务名称");
    return;
  }
  if (run_script_form.value.browser.length === 0) {
    MsgError("请选择浏览器");
    return;
  } else if (run_script_form.value.browser.length > 1) {
    MsgError("抱歉，由于资源有限，单次仅支持一个浏览器执行~");
  } else {
    run_browsers.value = [];
    result_id.value = String(Date.now());
    run_script_form.value.result_id = result_id.value;
    await run_browser_show();
    run_browser_active.value = run_script_form.value.browser[0];
    title.value = "正在执行：" + run_script_form.value.task_name;
    res_koiDialogRef.value.koiOpen();
    await startPolling();
    const res: any = await run_web_script(run_script_form.value);
    console.log(res);
    if (res.code === 10001) {
      MsgError(res.message);
      res_koiDialogRef.value.koiQuickClose(res.message);
      stopPolling();
    }
  }
};

const run_browser_show = async () => {
  run_script_form.value.browser.forEach((item: any) => {
    browser_list.value.forEach((browser: any) => {
      if (browser.value === item) {
        run_browsers.value.push({
          name: browser.name,
          value: browser.value
        });
      }
    });
  });
};

const interval = ref<any>(null); // 保存轮询的定时器 ID
// 开始轮询
const startPolling = async () => {
  if (interval.value) return; // 避免重复启动
  interval.value = setInterval(get_run_result, 2000); // 每5秒轮询一次
};

// 停止轮询
const stopPolling = () => {
  if (interval.value) {
    clearInterval(interval.value);
    interval.value = null;
  }
};

const change_browser = async () => {
  loading.value = true;
  await startPolling();
  loading.value = false;
};

const get_run_result = async () => {
  run_type.value = "正在执行";
  await get_result();
  await get_result_log();
};
const user = JSON.parse(LocalStorage.get("user"));
const web_result = ref<any>([]);
const web_result_log = ref<any>([]);
const run_type = ref<any>("");
const run_count = ref<any>(0);
const run_fail = ref<any>(0);
const start_time = ref<any>("");
const end_time = ref<any>("");
const pre_video = ref<any>("");
const img_show = ref<any>(false);
const pre_img = ref<any>("");
const trace = ref<any>("");
const get_result = async () => {
  const res: any = await get_web_result({
    result_id: result_id.value,
    browser: run_browser_active.value
  });
  web_result.value = res.data;
  run_count.value = web_result.value.length;
  if (web_result.value.length > 0) {
    start_time.value = start_time.value = web_result.value[web_result.value.length - 1].create_time;
  }
  let fail: number = 0;
  web_result.value.forEach((item: any) => {
    if (item.status == 0) {
      fail = fail + 1;
    }
    if (item.name == "执行结束") {
      stopPolling();
      run_count.value = run_count.value - 1;
      run_type.value = "执行结束";
      end_time.value = item.create_time;
      pre_video.value = item.video;
      trace.value = item.trace;
    }
  });
  run_fail.value = fail
};

const get_result_log = async () => {
  const res: any = await get_web_result_log({
    result_id: result_id.value,
    browser: run_browser_active.value
  });
  web_result_log.value = res.data;
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
  } else if (data.includes("补救")) {
    return "color: #1605ef";
  }
};

const pre_view = async (img: any) => {
  pre_img.value = [img];
  img_show.value = true;
};

const close_img = async () => {
  img_show.value = false;
};

const view_video = async () => {
  window.open(pre_video.value);
};

const run_script_cancel = async () => {
  run_koiDialogRef.value.koiQuickClose("取消调试");
};

const batch_run_script = async () => {
  run_script_form.value.script = [];
  run_koiDialogRef.value.koiOpen();
  title.value = "请配置调试信息";
  run_script_form.value.script = select_list.value;
};

const download_report = async () => {
  window.open(trace.value);
  await view_trace();
};

const view_trace = async () => {
  window.open("https://trace.playwright.dev/");
};

onMounted(() => {
  get_web_menu();
  element_select();
});
</script>

<template>
  <div>
    <div style="width: 100%">
      <KoiCard style="width: 20%; float: left; height: 800px">
        <div style="width: 100%">
          <div>
            <el-input v-model="filterText" style="margin-bottom: 5px; width: 90%; padding-right: 10px"
              placeholder="请输入节点名称" />
            <el-button type="text" style="padding-left: 5px" icon="Refresh" @click="get_web_menu()" />
          </div>
          <el-tree ref="treeRef" class="filter-tree" :data="tree_data" :props="defaultProps" default-expand-all
            :filter-node-method="filterNode" @node-click="web_menu_click" :allow-drop="on_menu_allowDrop" draggable>
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <span v-if="data.type === 0">
                  <el-icon style="padding-right: 3px">
                    <HomeFilled />
                  </el-icon>
                  {{ node.label }}
                </span>
                <span v-if="data.type === 1">
                  <el-icon style="padding-right: 3px">
                    <Folder />
                  </el-icon>
                  {{ node.label }}
                </span>
                <span v-if="data.type === 2">
                  <el-icon style="padding-right: 3px">
                    <ChromeFilled />
                  </el-icon>
                  {{ node.label }}
                </span>
                <span v-if="data.type === 0" class="right" style="padding-right: 10px">
                  <el-dropdown placement="bottom">
                    <el-icon>
                      <MoreFilled />
                    </el-icon>
                    <span class="el-dropdown-link" style="font-size: 20px" />
                    <template #dropdown>
                      <el-dropdown-menu class="header-new-drop">
                        <el-dropdown-item icon="CirclePlus" @click="add_menu(data)">新建子菜单</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
                <span v-if="data.type === 1" class="right" style="padding-right: 10px">
                  <el-dropdown placement="bottom">
                    <el-icon>
                      <MoreFilled />
                    </el-icon>
                    <span class="el-dropdown-link" style="font-size: 20px" />
                    <template #dropdown>
                      <el-dropdown-menu class="header-new-drop">
                        <el-dropdown-item icon="CirclePlus" @click="add_menu(data)">新建子菜单</el-dropdown-item>
                        <el-dropdown-item icon="Upload" @click="upload_file(data)">上传</el-dropdown-item>
                        <el-dropdown-item icon="Edit" @click="rename_menu(data)">重命名</el-dropdown-item>
                        <el-dropdown-item icon="Remove" @click="del_menu(data)">删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
                <span v-if="data.type === 2" class="right" style="padding-right: 10px">
                  <el-dropdown placement="bottom">
                    <el-icon>
                      <MoreFilled />
                    </el-icon>
                    <span class="el-dropdown-link" style="font-size: 20px" />
                    <template #dropdown>
                      <el-dropdown-menu class="header-new-drop">
                        <el-dropdown-item icon="Edit" @click="rename_menu(data)">重命名</el-dropdown-item>
                        <el-dropdown-item icon="Remove" @click="del_menu(data)">删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
              </span>
            </template>
          </el-tree>
        </div>
      </KoiCard>
      <KoiCard style="width: 77%; float: left; height: 800px">
        <div>
          <el-tabs v-model="tab_active" type="card" closable class="demo-tabs" @tab-remove="removeTab">
            <el-tab-pane v-loading="loading" v-for="(item, index) in tab_list" :key="index" :label="item.title"
              :name="item.name">
              <template #label>
                <span v-if="item.type == 1"><el-icon style="padding-right: 5px">
                    <Folder />
                  </el-icon>{{ item.name }}</span>
                <span v-if="item.type == 2"><el-icon style="padding-right: 5px">
                    <ChromeFilled />
                  </el-icon>{{ item.name }}</span>
              </template>
              <div v-if="item.type == 1">
                <div>
                  <KoiCard style="height: 700px">
                    <div>
                      <div style="float: right; padding-left: 10px; padding-right: 10px; padding-block-end: 10px">
                        <el-button type="primary" @click="batch_run_script()">立即调试</el-button>
                      </div>
                      <el-table v-loading="loading" border :data="table_list" empty-text="暂时没有数据哟🌻"
                        @selection-change="handleSelectionChange">
                        <el-table-column type="selection" align="center" />
                        <el-table-column label="序号" prop="id" align="center" type="index"></el-table-column>
                        <el-table-column label="脚本名称" prop="name" align="center"
                          :show-overflow-tooltip="true"></el-table-column>
                        <el-table-column label="类型" align="center">
                          <template #default="{ row }">
                            <el-tag v-if="row.type == 1">文件夹</el-tag>
                            <el-tag v-if="row.type == 2">脚本</el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column label="顺序" align="center">
                          <template #default="{ row }">
                            <el-input-number :min="1" :max="100" v-model="row.step" />
                          </template>
                        </el-table-column>
                      </el-table>
                    </div>
                  </KoiCard>
                </div>
              </div>
              <div v-if="item.type == 2" style="padding: 5px; height: 100%">
                <div style="padding-block-end: 5px">
                  <KoiCard style="height: 20%">
                    <div>
                      <el-descriptions title="脚本信息：" column="4">
                        <el-descriptions-item label="类型：">Web自动化</el-descriptions-item>
                        <el-descriptions-item label="脚本名称：">{{ item.name }}</el-descriptions-item>
                        <el-descriptions-item label="最后更新人： ">{{ item.content.username }}</el-descriptions-item>
                        <el-descriptions-item label="最后更新时间：">
                          {{ item.content.update_time }}
                        </el-descriptions-item>
                      </el-descriptions>
                    </div>
                  </KoiCard>
                </div>
                <div style="height: 79%">
                  <KoiCard>
                    <div style="padding-block-end: 5px">
                      <div style="float: right">
                        <el-button type="success" @click="save_web_script(item.id)">保存</el-button>
                      </div>
                      <div style="float: right; padding-left: 10px; padding-right: 10px">
                        <el-button type="primary" @click="run_script(item)">立即调试</el-button>
                      </div>
                      <div style="float: right">
                        <el-button type="primary" @click="run_script(item)">AI脚本一键录入</el-button>
                      </div>
                      <div style="float: left; padding-right: 10px">
                        <el-dropdown @command="add_script">
                          <el-button type="info">
                            浏览器操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item divided :command="{ type: 0, name: '首次打开网页' }">
                                首次打开网页
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 13, name: '打开新窗口' }">
                                打开新窗口
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 14, name: '切换上一个窗口' }">
                                切换上一个窗口
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 15, name: '切换下一个窗口' }">
                                切换下一个窗口
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 20, name: '刷新当前页' }">
                                刷新当前页
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 21, name: '关闭标签页' }">
                                关闭标签页
                              </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                      <div style="float: left">
                        <el-dropdown @command="add_script">
                          <el-button type="primary">
                            AI + 自定义<el-icon class="el-icon--right"><arrow-down /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item :command="{ type: 19, name: 'AI 步骤' }"> AI 步骤 </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 17, name: '自定义步骤' }">
                                自定义步骤
                              </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                      <div style="float: left; padding-left: 10px">
                        <el-dropdown @command="add_script">
                          <el-button type="primary">
                            鼠标操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item divided :command="{ type: 1, name: '左键点击' }"> 左键点击 </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 16, name: '右键点击' }"> 右键点击 </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 2, name: '双击事件' }"> 双击事件 </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 3, name: '长按事件' }"> 长按事件 </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 4, name: '拖拽事件' }"> 拖拽事件 </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                      <div style="float: left; padding-left: 10px">
                        <el-dropdown @command="add_script">
                          <el-button type="success">
                            输入操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item divided :command="{ type: 5, name: '直接输入' }"> 直接输入 </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 6, name: '补充输入' }"> 补充输入 </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 7, name: '清空文本' }"> 清空文本 </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                      <div style="float: left; padding-left: 10px">
                        <el-dropdown @command="add_script">
                          <el-button type="warning">
                            滑动操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item divided :command="{ type: 8, name: '上下滑动' }"> 上下滑动 </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                      <div style="float: left; padding-left: 10px">
                        <el-dropdown @command="add_script">
                          <el-button type="info">
                            文件操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item divided :command="{ type: 18, name: '上传文件' }"> 上传文件 </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                      <div style="float: left; padding-left: 10px">
                        <el-dropdown @command="add_script">
                          <el-button type="danger">
                            逻辑事件<el-icon class="el-icon--right"><arrow-down /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item divided :command="{ type: 10, name: 'if 事件' }"> if 事件
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 11, name: 'for 循环' }"> for 循环
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ type: 12, name: '等待事件' }"> 等待事件 </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                    </div>
                    <div>
                      <div style="width: 100%">
                        <div style="
                            height: 530px;
                            width: 50%;
                            float: left;
                            border: 1px solid #e4e7ed;
                            border-radius: 5px;
                            padding: 10px;
                            overflow: auto;
                          ">
                          <el-tree ref="step_treeRef" :data="item.content.script" :props="defaultProps"
                            default-expand-all :allow-drop="on_menu_allowDrop" @node-click="web_script_click" draggable>
                            <template #default="{ data }">
                              <el-card :class="['step-card', `step-card-${data.type}`]">
                                <div slot="header" class="card-header">
                                  <el-row :gutter="2" type="flex" align="middle" justify="center">
                                    <el-col :span="18" class="card-main-content">
                                      <div class="card-content-wrapper">
                                        <!--api展示-->
                                        <div class="card-inner">
                                          <div class="card-left">
                                            <span class="step-icon" :style="{ color: 'rgb(97, 100, 159)' }">1</span>
                                            <span class="method-tag">
                                              <span>
                                                <b style="color: #49cc90;">{{ data.name }}</b>
                                              </span>
                                            </span>
                                          </div>
                                        </div>
                                      </div>
                                    </el-col>
                                    <el-col :span="6">
                                      <div class="card-actions">
                                        <el-switch v-model="data.status" inline-prompt
                                          style="--el-switch-on-color: #53a8ff; --el-switch-off-color: #f56c6c" />
                                        <el-button icon="document" @click="copy_row(item.content.script, data)" circle
                                          class="action-button" />
                                        <el-button icon="delete" type="danger" @click="Delete_row(item.content.script, data)" circle
                                          class="action-button" />
                                      </div>
                                    </el-col>
                                  </el-row>
                                </div>
                              </el-card>
                              <!-- <div :style="step_style(data.type)">
                                <div>
                                  <div>
                                    <div>
                                      <el-icon v-if="data.type === 0" :style="icon_style">
                                        <ChromeFilled />
                                      </el-icon>
                                      <el-icon v-if="data.type === 1" :style="icon_style">
                                        <Pointer />
                                      </el-icon>
                                      <SvgIcon v-if="data.type === 2" name="db_click3" :style="icon_style" width="15"
                                        height="14"></SvgIcon>
                                      <SvgIcon v-if="data.type === 3" name="long_click3" :style="icon_style" width="15"
                                        height="14"></SvgIcon>
                                      <el-icon v-if="data.type === 4" :style="icon_style">
                                        <Rank />
                                      </el-icon>
                                      <el-icon v-if="data.type === 5" :style="icon_style">
                                        <EditPen />
                                      </el-icon>
                                      <el-icon v-if="data.type === 6" :style="icon_style">
                                        <Edit />
                                      </el-icon>
                                      <el-icon v-if="data.type === 7" :style="icon_style">
                                        <Delete />
                                      </el-icon>
                                      <el-icon v-if="data.type === 8" :style="icon_style">
                                        <Sort />
                                      </el-icon>
                                      <el-icon v-if="data.type === 9" :style="icon_style">
                                        <Switch />
                                      </el-icon>
                                      <el-icon v-if="data.type === 10" :style="icon_style">
                                        <Finished />
                                      </el-icon>
                                      <el-icon v-if="data.type === 11" :style="icon_style">
                                        <Refresh />
                                      </el-icon>
                                      <el-icon v-if="data.type === 12" :style="icon_style">
                                        <Timer />
                                      </el-icon>
                                      <el-icon v-if="data.type === 13" :style="icon_style">
                                        <Open />
                                      </el-icon>
                                      <el-icon v-if="data.type === 14" :style="icon_style">
                                        <Back />
                                      </el-icon>
                                      <el-icon v-if="data.type === 15" :style="icon_style">
                                        <Right />
                                      </el-icon>
                                      <el-icon v-if="data.type === 17" :style="icon_style">
                                        <User />
                                      </el-icon>
                                      <el-icon v-if="data.type === 18" :style="icon_style">
                                        <Document />
                                      </el-icon>
                                      <el-icon v-if="data.type === 19" :style="icon_style">
                                        <MostlyCloudy />
                                      </el-icon>
                                      <el-icon v-if="data.type === 20" :style="icon_style">
                                        <RefreshRight />
                                      </el-icon>
                                      <el-icon v-if="data.type === 21" :style="icon_style">
                                        <CircleCloseFilled />
                                      </el-icon>
                                      <SvgIcon v-if="data.type === 16" name="click_right" :style="icon_style" width="16"
                                        height="14"></SvgIcon>
                                      <el-button type="text" icon="Remove"
                                        @click="Delete_row(item.content.script, data)"
                                        style="float: right; padding-right: 10px; padding-top: 4px; color: #eb5d5dcc">
                                      </el-button>
                                      <el-button type="text" icon="DocumentCopy"
                                        @click="copy_row(item.content.script, data)"
                                        style="float: right; padding-right: 10px; padding-top: 4px">
                                      </el-button>
                                      <el-switch style="float: right; padding-right: 10px" v-model="data.status" />
                                      <span class="span" v-if="data.type === 0">{{ data.name + "，网址：" + data.action.element }}</span>
                                      <span class="span" v-if="data.type === 13">{{ data.name + "，网址：" + data.action.element }}</span> -->
                              <!-- <span v-if="data.type !== 19" class="span">{{ data.name }}</span>
                                      <span v-if="data.type === 19" class="span">{{ "AI操作：" + data.action.element
                                      }}</span>
                                    </div>
                                  </div>
                                </div>
                              </div> -->
                            </template>
                          </el-tree>
                        </div>
                        <div style="
                            height: 530px;
                            width: 46%;
                            float: right;
                            border: 1px solid #e4e7ed;
                            border-radius: 5px;
                            padding: 10px;
                            overflow-y: auto;
                          ">
                          <el-form>
                            <el-form-item v-if="script_info.type !== 19" label="名称：">
                              <el-input v-model="script_info.name"></el-input>
                            </el-form-item>
                            <el-form-item v-if="
                              script_info.type === 0 ||
                              script_info.type === 1 ||
                              script_info.type === 2 ||
                              script_info.type === 3 ||
                              script_info.type === 5 ||
                              script_info.type === 6 ||
                              script_info.type === 7 ||
                              script_info.type === 13 ||
                              script_info.type === 16 ||
                              script_info.type === 17
                            " label="定位：">
                              <el-radio-group v-model="script_info.action.type">
                                <el-radio :value="1">自定义</el-radio>
                                <el-radio :value="2">元素库</el-radio>
                              </el-radio-group>
                            </el-form-item>
                            <el-form-item v-if="
                              script_info.action.type !== 2 &&
                              script_info.type !== 0 &&
                              script_info.type !== 4 &&
                              script_info.type !== 8 &&
                              script_info.type !== 9 &&
                              script_info.type !== 10 &&
                              script_info.type !== 11 &&
                              script_info.type !== 12 &&
                              script_info.type !== 13 &&
                              script_info.type !== 14 &&
                              script_info.type !== 15 &&
                              script_info.type !== 19 &&
                              script_info.type !== 20 &&
                              script_info.type !== 21 &&
                              script_info.type !== 17
                            " label="选择器：">
                              <el-select v-model="script_info.action.locator" style="width: 22%" filterable>
                                <el-option v-for="item in locator_list" :key="item.value" :label="item.name"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select v-if="script_info.action.locator === 2"
                                v-model="script_info.action.locator_select" style="width: 22%; padding-left: 15px"
                                filterable>
                                <el-option v-for="item in locator_selects" :key="item.value" :label="item.label"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select
                                v-if="script_info.action.locator_select === 7 && script_info.action.locator === 2"
                                v-model="script_info.action.role" style="width: 22%; padding-left: 15px" filterable>
                                <el-option v-for="(item, index) in role_list" :key="index" :label="item.label"
                                  :value="item.value"></el-option>
                              </el-select>
                            </el-form-item>
                            <el-form-item
                              v-if="script_info.action.type !== 2 && (script_info.type === 0 || script_info.type === 13)"
                              label="网址：">
                              <el-input v-model="script_info.action.element" placeholder="请输入网址"></el-input>
                            </el-form-item>
                            <el-form-item v-if="
                              script_info.type !== 0 &&
                              script_info.type !== 4 &&
                              script_info.type !== 8 &&
                              script_info.type !== 9 &&
                              script_info.type !== 10 &&
                              script_info.type !== 11 &&
                              script_info.type !== 12 &&
                              script_info.type !== 13 &&
                              script_info.type !== 14 &&
                              script_info.type !== 15 &&
                              script_info.type !== 20 &&
                              script_info.type !== 19 &&
                              script_info.type !== 21 &&
                              script_info.action.type === 1
                            " label="元素值：">
                              <textarea
                                v-if="(script_info.type !== 19 && script_info.action.locator === 1) || script_info.type == 17"
                                v-model="script_info.action.element"
                                style="padding: 5px; border: 1px solid var(--el-border-color); width: 98%; height: 80px"
                                placeholder="请输入元素值，多个元素地址用英文逗号”,“隔开"></textarea>
                              <el-input v-if="script_info.action.locator === 2" v-model="script_info.action.element"
                                placeholder="请输入元素值"></el-input>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 19" label="脚本内容：">
                              <textarea v-model="script_info.action.element"
                                style="padding: 5px; border: 1px solid var(--el-border-color); width: 98%; height: 80px"
                                placeholder="例如：用户名输入框输入'admin'"></textarea>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 4" label="起始定位：">
                              <el-radio-group v-model="script_info.action.type">
                                <el-radio :value="1">自定义</el-radio>
                                <el-radio :value="2">元素库</el-radio>
                              </el-radio-group>
                            </el-form-item>
                            <el-form-item v-if="script_info.action.type === 1 && script_info.type === 4" label="选择器：">
                              <el-select v-model="script_info.action.locator" style="width: 22%" filterable>
                                <el-option v-for="item in locator_list" :key="item.value" :label="item.name"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select v-if="script_info.action.locator === 2"
                                v-model="script_info.action.locator_select" style="width: 22%; padding-left: 15px"
                                filterable>
                                <el-option v-for="item in locator_selects" :key="item.value" :label="item.label"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select
                                v-if="script_info.action.locator_select === 7 && script_info.action.locator === 2"
                                v-model="script_info.action.role" style="width: 22%; padding-left: 15px" filterable>
                                <el-option v-for="(item, index) in role_list" :key="index" :label="item.label"
                                  :value="item.value"></el-option>
                              </el-select>
                            </el-form-item>
                            <el-form-item v-if="script_info.action.type === 2 && script_info.type === 4" label="选择元素：">
                              <el-cascader v-model="script_info.action.element_id" placeholder="请选择元素"
                                style="width: 350px" :options="element_select_list" filterable
                                :props="{ value: 'element_id', label: 'name', children: 'children' }"
                                @change="element_select_change">
                                <template #default="{ node, data }">
                                  <el-icon v-if="data.type === 0" style="padding-right: 5px">
                                    <HomeFilled />
                                  </el-icon>
                                  <el-icon v-if="data.type === 1" style="padding-right: 5px">
                                    <Folder />
                                  </el-icon>
                                  <el-icon v-if="data.type === 2" style="padding-right: 5px">
                                    <ElementPlus />
                                  </el-icon>
                                  <span>{{ data.name }}</span>
                                  <span v-if="!node.isLeaf">({{ data.children.length }})</span>
                                </template>
                              </el-cascader>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 4 && script_info.action.type === 1" label="起始地址：">
                              <el-input v-model="script_info.action.element"></el-input>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 4" label="目标定位：">
                              <el-radio-group v-model="script_info.action.target_type">
                                <el-radio :value="1">自定义</el-radio>
                                <el-radio :value="2">元素库</el-radio>
                              </el-radio-group>
                            </el-form-item>
                            <el-form-item v-if="script_info.action.target_type === 1 && script_info.type === 4"
                              label="选择器：">
                              <el-select v-model="script_info.action.target_locator" style="width: 22%" filterable>
                                <el-option v-for="item in locator_list" :key="item.value" :label="item.name"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select v-if="script_info.action.target_locator === 2"
                                v-model="script_info.action.target_locator_select"
                                style="width: 22%; padding-left: 15px" filterable>
                                <el-option v-for="item in locator_selects" :key="item.value" :label="item.label"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select v-if="script_info.action.target_locator_select === 7"
                                v-model="script_info.action.role" style="width: 22%; padding-left: 15px" filterable>
                                <el-option v-for="(item, index) in role_list" :key="index" :label="item.label"
                                  :value="item.value"></el-option>
                              </el-select>
                            </el-form-item>
                            <el-form-item v-if="script_info.action.target_type === 2 && script_info.type === 4"
                              label="选择元素：">
                              <el-cascader v-model="script_info.action.target_id" placeholder="请选择元素"
                                style="width: 350px" :options="element_select_list" filterable
                                :props="{ value: 'element_id', label: 'name', children: 'children' }"
                                @change="element_select_change">
                                <template #default="{ node, data }">
                                  <el-icon v-if="data.type === 0" style="padding-right: 5px">
                                    <HomeFilled />
                                  </el-icon>
                                  <el-icon v-if="data.type === 1" style="padding-right: 5px">
                                    <Folder />
                                  </el-icon>
                                  <el-icon v-if="data.type === 2" style="padding-right: 5px">
                                    <ElementPlus />
                                  </el-icon>
                                  <span>{{ data.name }}</span>
                                  <span v-if="!node.isLeaf">({{ data.children.length }})</span>
                                </template>
                              </el-cascader>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 4 && script_info.action.target_type === 1"
                              label="目标地址：">
                              <el-input v-model="script_info.action.target"></el-input>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 8" label="滑动方向：">
                              <el-radio-group v-model="script_info.action.up_type">
                                <el-radio :value="1">向上</el-radio>
                                <el-radio :value="2">向下</el-radio>
                              </el-radio-group>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 9" label="滑动方向：">
                              <el-radio-group v-model="script_info.action.sway_type">
                                <el-radio :value="1">向左</el-radio>
                                <el-radio :value="2">向右</el-radio>
                              </el-radio-group>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 8 || script_info.type === 9" label="像素：">
                              <el-input v-model="script_info.action.element"></el-input>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 10">
                              <el-select v-model="script_info.action.type" style="width: 17%; padding-block-end: 5px"
                                filterable>
                                <el-option v-for="item in assert_list" :key="item.value" :label="item.name"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select v-if="script_info.action.type === 1 || script_info.action.type === 2"
                                v-model="script_info.action.locator"
                                style="width: 15%; padding-block-end: 5px; padding-left: 5px" filterable>
                                <el-option v-for="item in locator_list" :key="item.value" :label="item.name"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select v-if="script_info.action.type === 5" v-model="script_info.action.target_type"
                                style="width: 20%; padding-block-end: 5px; padding-left: 5px" filterable>
                                <el-option v-for="item in browser_assert" :key="item.value" :label="item.name"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select v-if="
                                script_info.action.locator === 2 &&
                                (script_info.action.type === 1 || script_info.action.type === 2)
                              " v-model="script_info.action.locator_select"
                                style="width: 15%; padding-block-end: 5px; padding-left: 5px" filterable>
                                <el-option v-for="item in locator_selects" :key="item.value" :label="item.label"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-select
                                v-if="script_info.action.locator_select === 7 && script_info.action.locator === 2"
                                v-model="script_info.action.input"
                                style="width: 18%; padding-left: 5px; padding-block-end: 5px">
                                <el-option v-for="(item, index) in role_list" :key="index" :label="item.label"
                                  :value="item.value"></el-option>
                              </el-select>
                              <el-input v-model="script_info.action.element"
                                style="width: 30%; padding-left: 5px; padding-block-end: 5px"
                                placeholder="请输入断言内容"></el-input>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 12" label="等待时长：">
                              <el-input-number v-model="script_info.action.element"></el-input-number>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 11" label="循环次数：">
                              <el-input-number v-model="script_info.action.element"></el-input-number>
                            </el-form-item>
                            <el-form-item
                              v-if="script_info.action.type === 2 && script_info.type !== 4 && script_info.type !== 10"
                              label="选择元素：">
                              <el-cascader v-model="script_info.action.element_id" placeholder="请选择元素"
                                style="width: 350px" :options="element_select_list" filterable
                                :props="{ value: 'element_id', label: 'name', children: 'children' }"
                                @change="element_select_change">
                                <template #default="{ node, data }">
                                  <el-icon v-if="data.type === 0" style="padding-right: 5px">
                                    <HomeFilled />
                                  </el-icon>
                                  <el-icon v-if="data.type === 1" style="padding-right: 5px">
                                    <Folder />
                                  </el-icon>
                                  <el-icon v-if="data.type === 2" style="padding-right: 5px">
                                    <ElementPlus />
                                  </el-icon>
                                  <span>{{ data.name }}</span>
                                  <span v-if="!node.isLeaf">({{ data.children.length }})</span>
                                </template>
                              </el-cascader>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 5 || script_info.type === 6" label="输入值：">
                              <el-input v-model="script_info.action.input"></el-input>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 0 || script_info.type === 13">
                              <div style="width: 100%">
                                <el-button type="text" icon="CirclePlus"
                                  @click="add_cookie(script_info.action.cookies)">添加cookies配置项</el-button>
                                <el-form>
                                  <el-form-item v-for="(ck, index) in script_info.action.cookies" :key="index">
                                    <el-input v-model="ck.name" placeholder="请输入key"
                                      style="width: 30%; padding-block-end: 5px"></el-input>
                                    <el-input v-model="ck.value" placeholder="请输入value"
                                      style="width: 63%; padding-block-end: 5px; padding-left: 5px"></el-input>
                                    <el-button type="text"
                                      style="color: #f16666; padding-left: 5px; padding-block-end: 10px" icon="Remove"
                                      circle @click="del_cookie(script_info.action.cookies, index)"></el-button>
                                  </el-form-item>
                                </el-form>
                              </div>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 0 || script_info.type === 13">
                              <div style="width: 100%">
                                <el-button type="text" icon="CirclePlus"
                                  @click="add_localstorage(script_info.action.localstorage)">添加localstorage配置项</el-button>
                                <el-form>
                                  <el-form-item v-for="(local, index) in script_info.action.localstorage" :key="index">
                                    <el-input v-model="local.name" placeholder="请输入key"
                                      style="width: 30%; padding-block-end: 5px"></el-input>
                                    <el-input v-model="local.value" placeholder="请输入value"
                                      style="width: 63%; padding-block-end: 5px; padding-left: 5px"></el-input>
                                    <el-button type="text"
                                      style="color: #f16666; padding-left: 5px; padding-block-end: 10px" icon="Remove"
                                      circle
                                      @click="del_localstorage(script_info.action.localstorage, index)"></el-button>
                                  </el-form-item>
                                </el-form>
                              </div>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 21" label="请选择：">
                              <el-radio-group v-model="script_info.action.target">
                                <el-radio value="now">当前标签页</el-radio>
                                <el-radio value="previous">关闭上一个标签页</el-radio>
                                <el-radio value="next">关闭下一个标签页</el-radio>
                                <el-radio value="customize">自定义</el-radio>
                              </el-radio-group>
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 21 && script_info.action.target === 'customize'"
                              label="请选择第几个标签页：">
                              <el-input-number v-model="script_info.action.element" :min="0" :max="10" />
                            </el-form-item>
                            <el-form-item v-if="script_info.type === 18" label="上传文件:">
                              {{ "（已上传成功：" + script_info.action.input + "）" }}
                              <div style="width: 100%; display: flex; justify-content: center; height: 220px">
                                <KoiUploadFiles v-model="script_info.action.input" :file-name="script_info.action.input"
                                  @fileSuccess="call_back_1" />
                                <el-button plain type="primary" @click="add_file(script_info.action)">确认上传</el-button>
                              </div>
                            </el-form-item>
                            <el-form-item>
                              <div style="width: 100%">
                                <el-tabs v-model="config_active" class="demo-tabs">
                                  <el-tab-pane label="配置项" name="first">
                                    <el-form label-position="right">
                                      <el-form-item label="执行前等待(秒)：">
                                        <el-input-number v-model="script_info.action.before_wait" :min="0"
                                          :max="15"></el-input-number>
                                      </el-form-item>
                                      <div class="h-10px"></div>
                                      <el-form-item label="执行后等待(秒)：">
                                        <el-input-number v-model="script_info.action.after_wait" :min="0"
                                          :max="15"></el-input-number>
                                      </el-form-item>
                                      <div class="h-10px"></div>
                                      <el-form-item label="超时时长(秒)：">
                                        <el-input-number v-model="script_info.action.timeout" :min="0"
                                          :max="15"></el-input-number>
                                      </el-form-item>
                                    </el-form>
                                  </el-tab-pane>
                                  <el-tab-pane label="断言" name="second">
                                    <el-button type="text" icon="CirclePlus"
                                      @click="add_assert(script_info.action.assert)">添加断言</el-button>
                                    <el-form>
                                      <el-form-item v-for="(as, index) in script_info.action.assert" :key="index">
                                        <el-select v-model="as.type" style="width: 17%; padding-block-end: 5px"
                                          filterable>
                                          <el-option v-for="item in assert_list" :key="item.value" :label="item.name"
                                            :value="item.value"></el-option>
                                        </el-select>
                                        <el-select v-if="as.type === 1 || as.type === 2" v-model="as.locator"
                                          style="width: 15%; padding-block-end: 5px; padding-left: 5px" filterable>
                                          <el-option v-for="item in locator_list" :key="item.value" :label="item.name"
                                            :value="item.value"></el-option>
                                        </el-select>
                                        <el-select v-if="as.type === 5" v-model="as.page_type"
                                          style="width: 20%; padding-block-end: 5px; padding-left: 5px" filterable>
                                          <el-option v-for="item in browser_assert" :key="item.value" :label="item.name"
                                            :value="item.value"></el-option>
                                        </el-select>
                                        <el-select v-if="as.locator === 2 && (as.type === 1 || as.type === 2)"
                                          v-model="as.locator_select"
                                          style="width: 15%; padding-block-end: 5px; padding-left: 5px" filterable>
                                          <el-option v-for="item in locator_selects" :key="item.value"
                                            :label="item.label" :value="item.value"></el-option>
                                        </el-select>
                                        <el-select v-if="as.locator_select === 7 && as.locator === 2" v-model="as.role"
                                          style="width: 18%; padding-left: 5px; padding-block-end: 5px">
                                          <el-option v-for="(item, index) in role_list" :key="index" :label="item.label"
                                            :value="item.value"></el-option>
                                        </el-select>
                                        <el-input v-if="as.type !== 6 && as.type !== 7" v-model="as.element"
                                          style="width: 28%; padding-left: 5px; padding-block-end: 5px"
                                          placeholder="请输入断言内容"></el-input>
                                        <el-input v-if="as.type === 6" v-model="as.element"
                                          style="width: 75%; padding-left: 5px; padding-block-end: 5px"
                                          placeholder="例如：expect(page.get_by_role('xxx', name='xxx')).to_have_value(xxx)"></el-input>
                                        <el-input v-if="as.type === 7" v-model="as.element"
                                          style="width: 75%; padding-left: 5px; padding-block-end: 5px"
                                          placeholder="例如：断言xxx存在当前页面"></el-input>
                                        <el-button type="text"
                                          style="color: #f16666; padding-left: 5px; padding-block-end: 10px"
                                          icon="Remove" circle
                                          @click="del_assert(script_info.action.assert, index)"></el-button>
                                      </el-form-item>
                                    </el-form>
                                  </el-tab-pane>
                                </el-tabs>
                              </div>
                            </el-form-item>
                          </el-form>
                        </div>
                      </div>
                    </div>
                  </KoiCard>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
        <div>
          <KoiDialog ref="add_koiDialogRef" :title="title" @koi-confirm="add_menu_confirm" @koi-cancel="add_menu_cancel"
            :height="100">
            <template #content>
              <el-form ref="formRef" :model="add_menu_form" label-width="80px" status-icon>
                <el-form-item label="名称：" prop="roleName">
                  <el-input v-model="add_menu_form.name" placeholder="请输入名称" clearable />
                </el-form-item>
                <el-form-item label="类型：" prop="roleCode">
                  <el-radio-group v-model="add_menu_form.type">
                    <el-radio :value="1">文件夹</el-radio>
                    <el-radio :label="2">脚本</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-form>
            </template>
          </KoiDialog>
        </div>
        <div>
          <KoiDialog ref="rename_koiDialogRef" :title="title" @koi-confirm="edit_menu_confirm"
            @koi-cancel="edit_menu_cancel" :height="100">
            <template #content>
              <el-form ref="formRef" :model="add_menu_form" label-width="80px" status-icon>
                <el-form-item label="名称：" prop="roleName">
                  <el-input v-model="add_menu_form.name" placeholder="请输入名称" clearable></el-input>
                </el-form-item>
              </el-form>
            </template>
          </KoiDialog>
        </div>
        <div>
          <KoiDialog ref="upload_koiDialogRef" :title="title" @koi-confirm="upload_file_confirm"
            @koi-cancel="upload_file_cancel" :height="250">
            <template #content>
              <div style="width: 100%; display: flex; justify-content: center">
                <KoiUploadFiles v-model="file_name" :accept-type="'.json'" :accept-types="'.json'"
                  :file-name="file_name" @file-success="call_back" />
              </div>
            </template>
          </KoiDialog>
        </div>
        <div>
          <KoiDialog ref="run_koiDialogRef" :title="title" @koi-confirm="run_script_confirm"
            @koi-cancel="run_script_cancel" :height="200">
            <template #content>
              <div>
                <el-form>
                  <el-form-item label="名称：">
                    <el-input v-model="run_script_form.task_name" placeholder="请输入名称" clearable />
                  </el-form-item>
                  <el-form-item label="执行模式：">
                    <el-radio-group v-model="run_script_form.browser_type">
                      <el-radio :value="1">有界面</el-radio>
                      <el-radio :value="2">无界面</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="分辨率(高*宽)：">
                    <div>
                      <el-input-number v-model="run_script_form.height" controls-position="right" min="800" label="高度">
                      </el-input-number>
                      <el-input-number v-model="run_script_form.width" style="padding-left: 10px"
                        controls-position="right" min="800" label="宽度">
                      </el-input-number>
                    </div>
                  </el-form-item>
                  <el-form-item label="选择浏览器：">
                    <el-select v-model="run_script_form.browser" multiple style="width: 60%">
                      <el-option v-for="item in browser_list" :key="item.value" :label="item.name"
                        :value="item.value"></el-option>
                    </el-select>
                  </el-form-item>
                </el-form>
              </div>
            </template>
          </KoiDialog>
        </div>
        <div>
          <KoiDialog ref="res_koiDialogRef" :title="title" :height="680" :width="1600" :footer-hidden="true">
            <template #content>
              <div v-loading="loading" style="width: 100%">
                <el-tabs tab-position="left" v-model="run_browser_active" class="demo-tabs" @tab-click="change_browser">
                  <el-tab-pane v-for="(item, index) in run_browsers" :key="index" :name="item.value">
                    <template #label>
                      <div v-show="item.value === 1" class="tab-info">
                        <img src="@/assets/icons/google.png" />
                        <span slot="code" class="code" style="padding-left: 5px">{{ item.name }}</span>
                      </div>
                      <div v-show="item.value === 2" class="tab-info">
                        <img src="@/assets/icons/firefox.png" />
                        <span slot="code" class="code" style="padding-left: 5px">{{ item.name }}</span>
                      </div>
                      <div v-show="item.value === 3" class="tab-info">
                        <img src="@/assets/icons/Edge.png" />
                        <span slot="code" class="code" style="padding-left: 5px">{{ item.name }}</span>
                      </div>
                      <div v-show="item.value === 4" class="tab-info">
                        <img src="@/assets/icons/ios.png" />
                        <span slot="code" class="code" style="padding-left: 5px">{{ item.name }}</span>
                      </div>
                    </template>
                    <div style="width: 100%">
                      <div style="width: 100%; padding-block-end: 10px">
                        <KoiCard style="height: 80px">
                          <div>
                            <el-descriptions :column="5">
                              <el-descriptions-item label="执行状态：">
                                <el-tag type="success" v-if="run_type == '正在执行'">{{ run_type }}</el-tag>
                                <el-tag type="danger" v-if="run_type == '执行结束'">{{ run_type }}</el-tag>
                              </el-descriptions-item>
                              <el-descriptions-item label="浏览器：">{{ item.name }}</el-descriptions-item>
                              <el-descriptions-item label="执行人：">{{ user.username }}</el-descriptions-item>
                              <el-descriptions-item label="开始时间：">{{ start_time }}</el-descriptions-item>
                              <el-descriptions-item label="结束时间：">{{ end_time }}</el-descriptions-item>
                              <el-descriptions-item label="已执行：">{{ run_count }}</el-descriptions-item>
                              <el-descriptions-item label="通过：">{{ run_count - run_fail }}</el-descriptions-item>
                              <el-descriptions-item label="失败：">{{ run_fail }}</el-descriptions-item>
                              <el-descriptions-item label="分析资源下载：">
                                <el-button v-if="trace !== ''" type="text" plain
                                  @click="download_report()">下载trace.zip</el-button>
                                <el-button v-if="trace !== ''" type="text" plain
                                  @click="view_trace()">打开分析页面</el-button>
                              </el-descriptions-item>
                              <el-descriptions-item label="视频查看：">
                                <el-button v-if="pre_video !== ''" type="text" plain
                                  @click="view_video()">查看视频</el-button>
                              </el-descriptions-item>
                            </el-descriptions>
                          </div>
                        </KoiCard>
                      </div>
                      <div style="width: 100%">
                        <KoiCard style="width: 30%; float: left; height: 560px; overflow-y: auto">
                          <div>
                            <el-timeline style="width: 80%">
                              <el-timeline-item center v-for="(res, index) in web_result" :key="index"
                                :icon="getIcon(res.status)" type="primary" :color="colors(res.status)" size="large"
                                :timestamp="'执行时间：' + res.create_time" placement="top">
                                <KoiCard :style="get_colors(res.status)">
                                  <span>{{ res.name }}</span>
                                  <span>{{ "结果：" + res.log }}</span>
                                  <span>
                                    <el-popover placement="right" :width="500" trigger="click">
                                      <template #reference>
                                        <el-button v-if="Object.keys(res.assert_result).length !== 0" icon="Search"
                                          type="text" style="float: right">
                                          断言详情
                                        </el-button>
                                      </template>
                                      <div v-for="(item, index) in res.assert_result" :key="index">
                                        <span :style="get_log_style(item.result)">{{ "断言结果：" + item.result }}</span>
                                        <el-button icon="Picture" type="text" style="float: right"
                                          @click="pre_view(item.img)">
                                          查看详情
                                        </el-button>
                                      </div>
                                    </el-popover>
                                    <el-button v-if="res.before_img !== ''" icon="Picture" type="text"
                                      @click="pre_view(res.before_img)">
                                      执行前
                                    </el-button>
                                    <el-button v-if="res.after_img !== ''" icon="Picture" type="text"
                                      @click="pre_view(res.after_img)">
                                      执行后
                                    </el-button>
                                  </span>
                                  <div class="img-viewer-box">
                                    <el-image-viewer v-if="img_show" :url-list="pre_img" @close="close_img" />
                                  </div>
                                </KoiCard>
                              </el-timeline-item>
                            </el-timeline>
                          </div>
                        </KoiCard>
                        <KoiCard style="width: 66%; float: right; height: 560px; overflow-y: auto">
                          <div>
                            <li v-if="run_type !== '执行结束'" style="margin-bottom: 7px; color: #0bbd87">执行日志获取中...</li>
                            <li v-for="(log, index) in web_result_log" :key="index" :style="get_log_style(log)">{{ log
                            }}</li>
                          </div>
                        </KoiCard>
                      </div>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </template>
          </KoiDialog>
        </div>
      </KoiCard>
    </div>
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

::v-deep .el-image-viewer__img {
  width: 50% !important;
  height: auto !important;
}

.el-tree {
  --el-tree-node-content-height: 30px;
}

.span {
  display: inline-flex;
  max-width: 430px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

/* 不同类型卡片的边框颜色 */
.step-card-api {
  border-left: 4px solid #61649f;
}

.step-card-if {
  border-left: 4px solid rgb(230, 162, 60);
}

.step-card-for {
  border-left: 4px solid rgb(2, 167, 240);
}

.step-card-script {
  border-left: 4px solid rgb(123, 77, 18);
}

.step-card-sql {
  border-left: 4px solid rgb(120, 56, 135);
}

.step-card-time {
  border-left: 4px solid rgb(103, 194, 58);
}

.card-header {
  // padding: 12px;
  width: 100%;
}

.card-content-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow: visible;
  /* 修改为visible，允许下拉菜单显示在容器外 */
  max-width: 100%;
  /* 确保不超出父容器 */
}

.card-inner {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  /* 从左开始 */
  width: 100%;
  padding: 0 20px;
  /* 增加左右内边距从15px到20px */
  min-height: 35px;
  /* 确保最小高度 */
  position: relative;
  /* 添加相对定位 */
  overflow: visible;
  /* 确保下拉菜单可见 */
}

.card-left {
  display: flex;
  align-items: center;
  width: 180px;
  /* 进一步增加宽度 */
  min-width: 180px;
  /* 确保最小宽度也相应增加 */
  justify-content: flex-start;
  /* 左对齐 */
  flex-shrink: 0;
  /* 防止被压缩 */
  margin-right: 15px;
  /* 增加右边距 */
  gap: 10px;
  /* 使用gap属性控制子元素间距 */
}

.card-center {
  margin-left: 10px;
  /* 减少左边距从50px到10px */
  flex-grow: 1;
  overflow: hidden;
}

.card-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  /* 居中对齐操作按钮 */
  gap: 8px;
  /* 按钮之间增加间距 */
}

.action-button {
  margin-left: 0;
  /* 删除左边距，使用gap控制间距 */
  transition: all 0.2s;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.method-tag {
  min-width: 60px;
  margin-left: 0;
  /* 移除左边距，依靠父元素的gap来控制间距 */
  font-size: 15px;
  flex-shrink: 0;
  /* 防止被压缩 */
}

.card-url {
  font-size: 15px;
  margin: 0 10px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 60%;
  /* 防止URL过长 */
}

.card-name {
  font-size: 14px;
  color: #888;
  margin-left: 5px;
}

.el-tag {
  color: #ffffff;
  width: 80px;
  height: 30px;
  text-align: center;
  font-size: 13px;
  line-height: 30px;
  margin-right: 0;
  /* 移除右边距，使用上面的gap代替 */
  margin-left: 0;
  /* 移除左边距，使用上面的gap代替 */
  flex-shrink: 0;
  /* 防止标签被压缩 */
}

.step-icon {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 24px;
  height: 24px;
  margin-right: 0;
  /* 移除右边距，使用上面的gap代替 */
  font-weight: bold;
  border-radius: 50%;
  text-align: center;
  background-color: white;
  border: 2px solid currentColor;
  font-size: 14px;
  line-height: 24px;
  box-sizing: border-box;
  flex-shrink: 0;
  /* 防止图标被压缩 */
}

.input-def {
  width: 160px;
  margin-right: 0;
  /* 移除右边距 */
  margin-bottom: 0;
  /* 移除底部边距 */
  flex-shrink: 0;
  /* 防止输入框被压缩 */
}

.if-content {
  flex-wrap: nowrap;
  gap: 8px;
  justify-content: flex-start;
  /* 左对齐内容 */
  width: 100%;
  padding: 8px 0;
  overflow: visible;
  /* 修改为visible，允许下拉菜单显示 */
  position: relative;
  /* 添加相对定位 */
}

.if-controls-wrapper {
  display: flex;
  flex-wrap: wrap;
  /* 允许在小屏幕上换行 */
  align-items: center;
  width: 100%;
  gap: 8px;
  position: relative;
  /* 添加相对定位 */
  overflow: visible !important;
  /* 确保下拉菜单可见 */
  min-width: min-content;
  /* 确保内容不会被压缩 */
  z-index: 20;
  /* 增加层级 */
}

.radio-group {
  display: flex;
  flex-wrap: nowrap;
  gap: 20px;
  white-space: nowrap;
}

.for-controls-wrapper {
  display: flex;
  flex-wrap: nowrap;
  width: 100%;
  position: relative;
  overflow: visible;
}

.loop {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  /* 允许换行 */
  gap: 20px;
  margin: 15px 0;
  width: 100%;
  overflow: visible;
  position: relative;
}

.loop-control {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  flex-shrink: 0;
}

.loop-details {
  // background-color: #f9f9f9;
  border-radius: 0 0 8px 8px;
  padding: 10px 15px;
  margin-top: 5px;
  width: 100%;
  overflow: visible;
  position: relative;
}

.script-button {
  color: #333;
  border: none;
  outline: none;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: auto;
  margin: 0;
  /* 移除边距 */
  padding: 0 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.script-button .el-icon {
  margin-left: 5px;
  font-size: 14px;
}

.code_mod {
  margin-bottom: 8px;
  text-align: center;
}

.code_mod .el-button {
  margin: 0 auto;
  display: block;
  width: 100%;
}

.script-editor {
  padding: 10px 0;
  border-top: 1px dashed #eee;
  margin-top: 10px;
  width: 100%;
  position: relative;
  z-index: 1;
}

.sql-message {
  text-align: center;
  color: #666;
  padding: 15px 0;
  font-style: italic;
  width: 100%;
  position: relative;
}

.time-controller {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  /* 左对齐 */
  width: 100%;
  flex-wrap: nowrap;
}

.time-control {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

/* 确保树组件中的内容宽度统一 */
:deep(.el-tree-node__content) {
  padding: 4px 4px 4px 0px;
  height: auto;
  width: 100%;
  // background: #f9f9f9;
  min-width: fit-content;
  /* 确保内容不会被压缩 */
}

.card-main-content {
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: visible;
  /* 修改为visible以允许内容溢出 */
  width: 100%;
  min-width: fit-content;
  /* 确保内容不会被压缩 */
}

/* 顶部操作按钮样式统一 */
.stepStyle {
  margin-left: 45px;
  margin-bottom: 10px;
  cursor: pointer;
}

/* 现代化头部样式 */
.page-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.page-header-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: linear-gradient(to bottom, #409eff, #2585ff);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
}

.back-button {
  display: flex;
  align-items: center;
  font-size: 14px;
  border: none;
  background: transparent;
  color: #606266;
  transition: all 0.3s;
  padding: 8px 12px;
  border-radius: 4px;
}

.back-button:hover {
  color: #409eff;
  transform: translateX(-2px);
  background-color: rgba(64, 158, 255, 0.1);
}

.page-title {
  margin-left: 16px;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.header-actions .action-button {
  margin-left: 10px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  height: 36px;
}

.header-actions .action-button:first-child {
  margin-left: 0;
}

.header-actions .action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.save-button {
  font-weight: 500;
  min-width: 86px;
}

.page-container {
  background-color: #f5f7fa;
  min-height: 100vh;
  padding: 16px;
}

:deep(.el-tree) {
  overflow: visible !important;
}

:deep(.el-scrollbar__wrap) {
  overflow-x: auto !important;
  overflow-y: auto !important;
}

:deep(.el-scrollbar__view) {
  overflow: visible;
}

:deep(.judgment-popper) {
  z-index: 9999 !important;
  position: absolute !important;
  /* 改为绝对定位 */
  transform-origin: center top !important;
}

:deep(.el-popper),
:deep(.el-dropdown-menu) {
  z-index: 99999 !important;
}

:deep(.el-dropdown-menu .el-dropdown-menu__item) {
  cursor: pointer !important;
}

/* 优化所有控制器元素的z-index */
.el-dropdown,
.el-radio-group {
  z-index: 5;
}

/* 确保el-tree和卡片显示正常 */
:deep(.el-tree-node) {
  overflow: visible;
}

:deep(.el-card) {
  overflow: visible;
  --el-card-padding: 0;
}

.card-header[data-v-731abb76] {
  padding: 6px;
  width: 100%;
}

:deep(.el-card__body) {
  overflow: visible;
}

/* 进一步增强下拉菜单的显示 */
:deep(.el-dropdown__popper) {
  position: absolute !important;
  /* 改为绝对定位 */
  z-index: 99999 !important;
}

.env-dropdown-item {
  padding: 8px 20px;
  cursor: pointer !important;
  display: block;
  width: 100%;
  text-align: left;
}

/* 修复HTTP请求环境选择的样式 */
.custom-dropdown-item {
  padding: 10px 20px;
  cursor: pointer !important;
  display: block;
  width: 100%;
  text-align: left;
  color: #606266;
  line-height: 1.5;
  box-sizing: border-box;
  white-space: nowrap;
  z-index: 999999 !important;
  position: relative;
  transition: all 0.2s;
}

.custom-dropdown-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.custom-dropdown-item:active {
  background-color: #d9ecff;
  color: #409eff;
}

/* 自定义树组件样式 */
.custom-tree {
  overflow: visible !important;
  position: relative;
  z-index: 1;
}

/* 添加媒体查询，针对小屏幕进行优化 */
@media (max-width: 1200px) {
  .card-inner {
    flex-wrap: wrap;
    padding: 10px;
  }

  .card-left {
    width: auto;
    min-width: 150px;
    margin-right: 10px;
  }

  .if-controls-wrapper {
    flex-wrap: wrap;
  }

  .loop-control {
    margin-bottom: 10px;
  }

  .card-actions {
    justify-content: flex-end;
  }

  .card-center {
    width: 100%;
    margin-top: 10px;
    margin-left: 0;
  }

  .card-url {
    max-width: 100%;
    margin: 5px 0;
  }

  .input-def {
    width: 100%;
    margin-bottom: 8px;
  }

  .el-tag {
    width: auto;
    padding: 0 8px;
  }

  /* HTTP请求专用样式 */
  .step-card-api .card-center {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .step-card-api .card-url {
    max-width: 100%;
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    order: 2;
  }

  .step-card-api .el-dropdown {
    margin-bottom: 5px;
    order: 1;
  }

  .step-card-api .card-name {
    order: 3;
    margin-top: 5px;
  }

  /* 条件控制器专用样式 */
  .step-card-if .if-controls-wrapper {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .step-card-if .if-controls-wrapper .el-input:last-child {
    grid-column: span 2;
  }

  /* 循环控制器专用样式 */
  .step-card-for .for-controls-wrapper {
    width: 100%;
  }

  .step-card-for .loop {
    flex-direction: column;
    align-items: flex-start;
  }

  .step-card-for .loop-control {
    width: 100%;
    margin-bottom: 8px;
  }
}

/* 树容器样式 - 添加横向滚动支持 */
.tree-container {
  // margin-left: 20px;
  margin-right: 20px;
  min-width: 90%;
  overflow-x: auto;
  // padding-bottom: 20px;
  /* 为横向滚动条预留空间 */
}

/* 确保嵌套步骤有足够空间显示 */
:deep(.el-tree-node__children) {
  // margin-left: 20px;
  /* 增加嵌套层级的缩进 */
  position: relative;
}

/* 为嵌套层级添加左侧指示线 */
:deep(.el-tree-node__children)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 2px;
  // background-color: #ebeef5;
  z-index: 1;
}

/* 修复嵌套步骤的宽度问题 */
:deep(.el-tree-node.is-expanded > .el-tree-node__children) {
  display: block;
  width: 100%;
  min-width: fit-content;
  overflow: visible;
}

/* 确保步骤卡片相对于树的位置 */
.step-card {
  border-radius: 10px;
  margin-bottom: 8px;
  transition: all 0.3s;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  width: 100%;
  position: relative;
  z-index: 5;
  overflow: visible !important;
  min-width: fit-content;
  /* 确保卡片不会被压缩 */
}

/* 添加el-tree拖拽提示线样式 */
:deep(.el-tree-node__drop-indicator) {
  position: absolute;
  left: 0;
  right: 0;
  height: 4px !important;
  /* 增加高度使其更明显 */
  background-color: #2b85e4 !important;
  /* 更鲜明的蓝色 */
  z-index: 99999 !important;
  /* 确保最高层级 */
  pointer-events: none;
  border-radius: 2px;
  box-shadow: 0 0 6px rgba(43, 133, 228, 0.8);
  /* 添加阴影效果使线更明显 */
}

/* 加强拖拽提示线可见性 */
:deep(.el-tree-node.is-drop-inner > .el-tree-node__content) {
  background-color: rgba(43, 133, 228, 0.2) !important;
  border: 1px dashed #2b85e4 !important;
  /* 添加边框 */
}

/* 鼠标拖拽样式 */
:deep(.el-tree-node.is-dragging) {
  opacity: 0.7;
  background-color: #f0f9ff !important;
  border: 1px dashed #2b85e4 !important;
}

:deep(.el-tree-node.is-dragging-over) {
  background-color: #e6f1fc !important;
}

/* 确保drop-indicator不被遮挡 */
:deep(.el-tree) {
  position: relative;
  /* 确保相对定位 */
}

:deep(.el-tree-node) {
  position: relative;
  /* 确保相对定位 */
}

/* 全局覆盖el-tree-node__drop-indicator样式，防止被其他样式覆盖 */
body .el-tree-node__drop-indicator {
  position: absolute;
  left: 0;
  right: 0;
  height: 4px !important;
  background-color: #2b85e4 !important;
  z-index: 99999 !important;
  pointer-events: none;
  border-radius: 2px;
  box-shadow: 0 0 6px rgba(43, 133, 228, 0.8);
}

@media (max-width: 768px) {
  .card-main-content {
    width: 100%;
  }

  .card-actions {
    width: 100%;
    justify-content: center;
    margin-top: 10px;
  }

  :deep(.el-row) {
    margin-left: 0 !important;
    margin-right: 0 !important;
  }

  .header-actions {
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
  }

  .header-actions .action-button {
    margin-left: 5px;
  }

  /* 减小间距和调整布局 */
  .card-inner {
    padding: 5px 10px;
  }

  .el-card {
    margin-bottom: 5px;
  }

  .card-left {
    min-width: 130px;
    gap: 5px;
  }

  .step-icon {
    width: 20px;
    height: 20px;
    font-size: 12px;
    line-height: 20px;
  }

  .el-tag {
    font-size: 12px;
    height: 25px;
    line-height: 25px;
  }

  /* 修复脚本编辑器在小屏幕上的显示 */
  .script-editor {
    display: flex;
    flex-direction: column;
  }

  :deep(.script-editor .el-col) {
    width: 100% !important;
    margin-bottom: 10px;
  }
}

/* 确保步骤卡片相对于树的位置 */
.step-card {
  border-radius: 10px;
  margin-bottom: 8px;
  transition: all 0.3s;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  width: 100%;
  position: relative;
  z-index: 5;
  overflow: visible !important;
  min-width: fit-content;
  /* 确保卡片不会被压缩 */
}

/* 修复嵌套步骤的滚动问题 */
:deep(.el-scrollbar__wrap) {
  overflow-x: scroll !important;
}

/* 确保树组件在横向滚动时内容不会被截断 */
:deep(.el-tree) {
  min-width: fit-content;
  width: 100%;
}

:deep(.el-tree-node) {
  white-space: nowrap;
  min-width: fit-content;
}
</style>
