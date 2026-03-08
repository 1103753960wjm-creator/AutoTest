<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { ElTree, TabsPaneContext } from "element-plus";
import { MsgBox, MsgError, MsgSuccess, NoticeError } from "@/utils/koi.ts";
import {
  add_app_menu,
  app_menu,
  del_app_menu,
  get_script,
  rename_app_menu,
  run_app_script,
  save_app_script,
  app_result,
  pid_status,
  stop_process,
  get_script_list,
  app_result_detail,
  run_scripts,
  view_script_list, app_correction
} from "@/api/api_app/app.ts";
import { app_view_device, get_device_list } from "@/api/api_app/device.ts";
import { file_list } from "@/api/api_file/file.ts";
import * as echarts from "echarts";
import { img_select } from "@/api/api_app/img.ts";
import { ElLoading } from 'element-plus';
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
const script_info = ref<any>({});

// app目录
watch(filterText, val => {
  treeRef.value!.filter(val);
});

const filterNode = (value: string, data: any) => {
  if (!value) return true;
  return data.name.includes(value);
};

const get_app_menu = async () => {
  try {
    loading.value = true;
    const res: any = await app_menu({});
    tree_data.value = res.data;
    loading.value = false;
  } catch {
    NoticeError("数据查询失败，请刷新重试🌻");
  }
};

const table_list = ref<any>([]);
const app_menu_click = async (node: any) => {
  try {
    if (node.type == 1) {
      loading.value = true;
      const res: any = await get_script_list({ id: node.id });
      table_list.value = res.data;
      table_list.value.forEach((item: any, index: number) => {
        item.step = index + 1;
      });
      await addTab(node, res.data);
      loading.value = false;
    } else if (node.type == 2) {
      loading.value = true;
      const res: any = await get_script({ id: node.id });
      await addTab(node, res.data);
      if (script_info.value.length > 0) {
        script_info.value = res.data.script[0];
      }
      loading.value = false;
    }
  } catch {
    NoticeError("数据查询失败，请刷新重试🌻");
  }
};

const select_list = ref<any>([]);
const handleSelectionChange = (selection: any) => {
  select_list.value = selection.sort((a: any, b: any) => a.step - b.step);
};

const Delete_row = async (name: any) => {
  table_list.value.forEach((item: any, index: any) => {
    if (item.name === name) {
      table_list.value.splice(index, 1);
    }
  });
};

const showPrefix = ref<any>(true);
const props1 = computed(() => ({
  showPrefix: showPrefix.value,
  checkOnClickNode: true
}))
// el-tabs
const tab_active = ref("");
const tab_list = ref<any>([]);

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

const tab_click = async (pane: TabsPaneContext, ev: Event) => {
  console.log(pane);
  console.log(ev);
};

const add_menu_form = ref<any>({});
const run_form = ref<any>({
  version: "",
  run_type: 1,
  channel_id: "",
  app_list: [
    {
      path: "",
      config: [{
        deviceid: "",
        package: ""
      }]
    }
  ]
});
const device_list = ref<any>([]);
const run_device_list = ref<any>([]);
const device_active = ref<any>("");
const title = ref<string>("");
const device = ref<string>("");
const add_koiDialogRef = ref();
const rename_koiDialogRef = ref();
const device_koiDialogRef = ref();
const run_koiDialogRef = ref();
const user = JSON.parse(LocalStorage.get("user"));
const script_id = ref<number>();
const menu_form = ref<any>({
  name: "",
  id: null
});
const pid_list = ref<any>([]);
const run_pid = ref<any>(null);

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
    const res: any = await add_app_menu(add_menu_form.value);
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
    const res: any = await rename_app_menu(add_menu_form.value);
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

const del_menu = async (data: any) => {
  MsgBox("您确认需要该目录么？").then(async () => {
    const res: any = await del_app_menu({ id: data.id, type: data.type });
    MsgSuccess(res.message);
    await get_app_menu();
  });
};

// 自动化脚本
const add_script = (command: any) => {
  script_list.value.push({
    name: command.name,
    address: "",
    type: command.type,
    status: true,
    android: { img: null, assert: null },
    ios: { img: null, assert: null }
  });
};

const app_script_click = async (node: any) => {
  script_info.value = node;
};

const save_script = async (id: number) => {
  try {
    const res: any = await save_app_script({
      script: script_list.value,
      id: id
    });
    MsgSuccess(res.message);
  } catch {
    NoticeError("保存失败，请重试🌻");
  }
};
const result_id = ref<string>("");

const get_device = async () => {
  const res: any = await get_device_list({});
  device_list.value = res.data;
};

const dialog_height = ref<any>(350);
const package_list = ref<any>([]);
const add_app_list = async () => {
  run_form.value.app_list.push({
    path: "",
    config: [
      {
        deviceid: "",
        package: ""
      }
    ]
  });
  dialog_height.value = dialog_height.value + 80
};

const add_config = async (config: any) => {
  config.push({
    deviceid: "",
    package: ""
  });
};

const search_package = async (path: any) => {
  const res: any = await file_list({
    folder_path: path
  });
  package_list.value = res.data;
};
const del_app_list = async (index: any) => {
  run_form.value.app_list.splice(index, 1);
  dialog_height.value = dialog_height.value - 80
};

const del_config = async (index: any, data: any) => {
  if (data.length == 1) {
    return;
  }
  data.splice(index, 1);
};

const run_script = async (id: number) => {
  title.value = "选择设备";
  run_form.value.run_type = 1;
  script_id.value = id;
  await get_device();
  device_koiDialogRef.value.koiOpen();
};

const get_run_device = async () => {
  if (run_form.value.run_type == 1) {
    run_form.value.app_list.forEach((item: any) => {
      item.config.forEach((conf: any) => {
        device_list.value.forEach((device: any) => {
          if (conf.deviceid == device.deviceid) {
            device.path = item.path;
            device.package = conf.package;
            device.notify = 0;
            run_device_list.value.push(
              device
            )
          }
        })
      })
    })
  }
};

const run_script_list = async () => {
  title.value = "执行脚本";
  run_form.value.run_type = 1;
  await get_device();
  script_list_koiDialogRef.value.koiOpen();
};

const run_script_confirm = async () => {
  const loadingInstance = ElLoading.service({
    text: "正在启动自动化任务，请稍后！",
    background: "rgba(0,0,0,.2)"
  });
  const id_result = String(Date.now());
  await get_run_device();
  const res: any = await run_scripts({
    id: script_id.value,
    run_type: run_form.value.run_type,
    version: run_form.value.version,
    channel_id: run_form.value.channel_id,
    result_id: id_result,
    device_list: run_device_list.value,
    task_name: run_form.value.task_name,
    script_list: select_list.value
  });
  pid_list.value = res.data.pid_list;
  MsgSuccess(res.message);
  loadingInstance.close();
  device_active.value = run_device_list.value[0].name;
  title.value = "设备执行过程";
  run_koiDialogRef.value.koiOpen();
  result_id.value = id_result;
  await device_pid();
  run_pid.value = pid_list.value[0]["pid"];
  device.value = run_device_list.value[0].deviceid;
  await startPolling();
  await getEcharts();
};

const script_list_koiDialogRef = ref();
const run_list_cancel = async () => {
  script_list_koiDialogRef.value.koiClose();
};

const run_confirm = async () => {
  const loadingInstance = ElLoading.service({
    text: "正在启动自动化任务，请稍后！",
    background: "rgba(0,0,0,.2)"
  });
  const id_result = String(Date.now());
  await get_run_device();
  const res: any = await run_app_script({
    id: script_id.value,
    run_type: run_form.value.run_type,
    version: run_form.value.version,
    channel_id: run_form.value.channel_id,
    result_id: id_result,
    device_list: run_device_list.value,
    task_name: run_form.value.task_name
  });
  pid_list.value = res.data.pid_list;
  MsgSuccess(res.message);
  loadingInstance.close();
  device_active.value = run_device_list.value[0].name;
  title.value = "设备执行过程";
  run_koiDialogRef.value.koiOpen();
  result_id.value = id_result;
  await device_pid();
  run_pid.value = pid_list.value[0]["pid"];
  device.value = run_device_list.value[0].deviceid;;
  await startPolling();
  await getEcharts();
};

const device_pid = async () => {
  run_device_list.value.forEach((item: any) => {
    pid_list.value.forEach((pid: any) => {
      if (item.deviceid == pid.deviceid) {
        item.pid = pid.pid;
      }
    });
  });
};

const run_type = ref<string>("");
const get_pid_status = async () => {
  const res: any = await pid_status({
    pid: run_pid.value
  });
  run_type.value = res.message;
  // const res_number: number = await result_check();

  if (res.message == "执行结束") {
    stopPolling();
    run_type.value = "执行结束";
    await get_details(result_id.value);
  }
  await get_result();
};

const percentage = ref<number>();
const script_pass = ref<number>();
const script_fail = ref<number>();
const script_un_run = ref<number>();
const start_time = ref<any>("");
const end_time = ref<any>("");
const script_total = ref<number>();
const get_details = async (result_id: any) => {
  const res: any = await app_result_detail({
    result_id: result_id,
    device: device.value,
    device_list: run_device_list.value
  });
  percentage.value = res.data.percent;
  script_pass.value = res.data.script_pass;
  script_fail.value = res.data.script_fail;
  script_total.value = res.data.script_total;
  script_un_run.value = res.data.script_un_run;
  end_time.value = res.data.end_time;
  start_time.value = res.data.start_time;
};

// const result_check = async () => {
//   let result_umber = 0;
//   for (const item of run_result.value) {
//     if (item.status === 0) {
//       result_umber++;
//     }
//   }
//   return result_umber;
// };

const stop_run = async (pid: any) => {
  const res: any = await stop_process({
    pid: pid,
    deviceid: device.value,
    result_id: result_id.value
  });
  if (res.message == "执行结束") {
    stopPolling();
    run_type.value = "执行结束";
  } else {
    MsgError(res.message);
  }
};

const device_url = ref<any>("");
const device_koiDrawerRef = ref();
const view_phone = async () => {
  const res: any = await app_view_device({
    "device_id": device.value
  });
  device_url.value = res.data.device_url
  device_koiDrawerRef.value.koiOpen();
};

const run_app_correction = async () => {
  const res: any = await app_correction({
    result_id: result_id.value,
    device: device.value,
  });
  MsgSuccess(res.message);
};

const interval = ref<any>(null); // 保存轮询的定时器 ID

// 开始轮询
const startPolling = async () => {
  if (interval.value) return; // 避免重复启动
  interval.value = setInterval(get_pid_status, 3000); // 每5秒轮询一次
};

// 停止轮询
const stopPolling = () => {
  if (interval.value) {
    clearInterval(interval.value);
    interval.value = null;
  }
};

const run_close = async () => {
  run_device_list.value = [];
  per_time.value = [0];
  cpu.value = [0];
  memory.value = [0];
  up_network.value = [0];
  down_network.value = [0];
  temperature.value = [0];
  percentage.value = 0;
  run_koiDialogRef.value.koiQuickClose("关闭成功");
};

const change_device = async (pane: TabsPaneContext) => {
  stopPolling();
  device_url.value = "";
  run_device_list.value.forEach((item: any) => {
    if (item.name == pane.props.name) {
      run_pid.value = item.pid;
      device.value = item.deviceid;
      startPolling();
      per_time.value = [0];
      cpu.value = [0];
      memory.value = [0];
      up_network.value = [0];
      down_network.value = [0];
      temperature.value = [0];
    }
  });
  await get_pid_status();
  await getEcharts();
};

const run_result = ref<any>([]);
const get_result = async () => {
  const res = await app_result({
    result_id: result_id.value,
    device: device.value
  });
  await perform_result(res.data);
  run_result.value = res.data;
  res.data.forEach((item: any) => {
    if (item.name == "执行结束") {
      pre_video.value = item.video;
    }
  });
  await getEcharts();
};

const per_time = ref<any>([]);
const cpu = ref<any>([]);
const memory = ref<any>([]);
const up_network = ref<any>([]);
const down_network = ref<any>([]);
const temperature = ref<any>([]);
const perform_result = async (result: any) => {
  if (result.length > 0) {
    const res: any = result[0];
    per_time.value = res.performance.time;
    cpu.value = res.performance.cpu;
    memory.value = res.performance.memory;
    up_network.value = res.performance.up_network;
    down_network.value = res.performance.down_network;
    temperature.value = res.performance.temperature;
  }
};
const getEcharts = async () => {
  const dom = document.getElementById("chart");
  let chartRefs = echarts.init(dom);
  let rq = per_time.value;
  let seriesArr: any = [];
  let list = [
    {
      name: "CPU(%)",
      children: cpu.value
    },
    {
      name: "内存(%)",
      children: memory.value
    },
    {
      name: "温度(℃)",
      children: temperature.value
    },
    {
      name: "上传网速(KB/s)",
      children: up_network.value
    },
    {
      name: "下载网速(KB/s)",
      children: down_network.value
    }
  ];
  let colorArr = ["0, 62, 246", "0, 193, 142", "253, 148, 67", "211, 225, 96", "234, 66, 66"];
  list.forEach((val, index) => {
    seriesArr.push({
      name: val.name,
      type: "line",
      symbolSize: 6,
      data: val.children,
      areaStyle: {
        normal: {
          color: new echarts.graphic.LinearGradient(
            0,
            0,
            0,
            1,
            [
              {
                offset: 0,
                color: `rgba(${colorArr[index]},.2)`
              },
              {
                offset: 1,
                color: "rgba(255, 255, 255,0)"
              }
            ],
            false
          )
        }
      },
      itemStyle: {
        normal: {
          color: `rgb(${colorArr[index]})`
        }
      },
      lineStyle: {
        normal: {
          width: 2,
          shadowColor: `rgba(${colorArr[index]}, .2)`,
          shadowBlur: 4,
          shadowOffsetY: 25
        }
      }
    });
  });
  let option = {
    backgroundColor: "#fff",
    tooltip: {
      trigger: "axis",
      axisPointer: {
        lineStyle: {
          color: "#ddd"
        }
      },
      backgroundColor: "rgba(255,255,255,1)",
      padding: [5, 10],
      textStyle: {
        color: "#000"
      }
    },
    legend: {
      right: "center",
      top: "6%",
      textStyle: {
        color: "#000",
        fontSize: 12,
        fontWeight: 600
      },
      data: list.map(val => {
        return val.name;
      })
    },
    grid: {
      left: "2%",
      right: "5%",
      bottom: "6%",
      top: "18%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      data: rq,
      boundaryGap: false,
      splitLine: {
        show: true,
        interval: "auto",
        lineStyle: {
          type: "dashed",
          color: ["#cfcfcf"]
        }
      },
      axisTick: {
        show: false
      },
      axisLine: {
        lineStyle: {
          color: "#cfcfcf"
        }
      },
      axisLabel: {
        // margin: 10,
        textStyle: {
          fontSize: 12,
          color: "#9e9d9f",
          fontWeight: 600
        }
      }
    },
    yAxis: [
      {
        name: "(%)",
        type: "value",
        splitLine: {
          show: true,
          lineStyle: {
            type: "dashed",
            color: ["#cfcfcf"]
          }
        },
        axisTick: {
          show: false
        },
        axisLine: {
          show: true,
          lineStyle: {
            fontSize: 12,
            color: "#cfcfcf"
          }
        },
        axisLabel: {
          textStyle: {
            fontSize: 12,
            color: "#9e9d9f",
            fontWeight: 600
          }
        },
        max: 100
      }
    ],
    series: seriesArr
  };
  chartRefs.setOption(option);
};

const getIcon = (status: any) => {
  if (status === 1 || status === 2) {
    return "Check";
  } else {
    return "Close";
  }
};
const colors = (status: any) => {
  if (status === 1 || status === 2) {
    return "#0bbd87";
  } else {
    return "#d70e0e";
  }
};

const get_colors = (status: any) => {
  if (status === 1 || status == 2) {
    return "color: #0bbd87";
  } else {
    return "color: #d70e0e";
  }
};

const run_cancel = async () => {
  device_koiDialogRef.value.koiClose();
};

// 预览图片，视频
const pre_video = ref<any>("");
const img_show = ref<any>(false);
const pre_img = ref<any>("");
const pre_view = async (img: any) => {
  pre_img.value = [img];
  img_show.value = true;
};

const close_img = async () => {
  img_show.value = false;
};

const pre_view_video = async () => {
  window.open(pre_video.value);
};

const run_script_data = ref<any>([]);
const view_script = async (item: any) => {
  const res: any = await view_script_list({
    menu_id: item
  });
  if (res.code == 200) {
    run_script_data.value = res.data;
  }
};

const on_allowDrop = (moveNode: any, inNode: any, type: any) => {
  console.log(moveNode, inNode)
  // 不允许同一层级内的inner操作
  return type !== "inner";
};

const on_menu_allowDrop = (moveNode: any, inNode: any, type: any) => {
  console.log(moveNode, inNode)
  // 不允许同一层级内的inner操作
  if (inNode.data.type == 2) {
    return type !== "inner";
  } else {
    return type;
  }
};

// 删除脚本
const del_script_info = async (node: any) => {
  const list = script_list.value;
  list.forEach((item: any, index: any) => {
    if (item.name === node.label) {
      list.splice(index, 1);
    }
  });
};

const img_select_list = ref<any>([]);
const get_img_select = async () => {
  const res: any = await img_select({});
  img_select_list.value = res.data;
};

const Add_install = async (data: any) => {
  data.push({
    channel_id: "", device_id: ""
  })
};

const Del_install = async (data: any, index: any) => {
  if (data.length > 1) {
    data.splice(index, 1);
  } else {
    return;
  }
};

// 生命周期钩子
onMounted(() => {
  get_app_menu();
  get_img_select();
});
</script>

<template>
  <div>
    <KoiCard>
      <div style="width: 100%">
        <KoiCard style="width: 75%; height: 780px; float: right; padding: 5px">
          <div>
            <el-tabs v-model="tab_active" type="card" closable class="demo-tabs" @tab-remove="removeTab"
              @tab-click="tab_click">
              <el-tab-pane v-loading="loading" v-for="(item, index) in tab_list" :key="index" :label="item.title"
                :name="item.name">
                <div v-if="item.type == 1">
                  <div>
                    <KoiCard style="height: 700px">
                      <div>
                        <div style="float: right; padding-left: 10px; padding-right: 10px; padding-block-end: 10px">
                          <el-button type="primary" @click="run_script_list()">立即调试</el-button>
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
                          <el-table-column label="操作" align="center" fixed="right">
                            <template #default="{ row }">
                              <el-tooltip content="删除🌻" placement="top">
                                <el-button type="danger" icon="Delete" circle plain
                                  @click="Delete_row(row.name)"></el-button>
                              </el-tooltip>
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
                          <el-descriptions-item label="类型：">APP自动化</el-descriptions-item>
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
                          <el-button type="success" @click="save_script(item.id)">保存</el-button>
                        </div>
                        <div style="float: right; padding-left: 10px; padding-right: 10px">
                          <el-button type="primary" @click="run_script(item.id)">立即调试</el-button>
                        </div>
                        <div style="float: right">
                          <el-dropdown @command="add_script">
                            <el-button type="warning">
                              添加步骤<el-icon class="el-icon--right"><arrow-down /></el-icon>
                            </el-button>
                            <template #dropdown>
                              <el-dropdown-menu>
                                <el-dropdown-item icon="Download" :command="{ type: 0, name: '等待热更' }">
                                  等待热更
                                </el-dropdown-item>
                                <el-dropdown-item icon="SwitchButton" divided :command="{ type: 1, name: '启动App' }">
                                  启动App
                                </el-dropdown-item>
                                <el-dropdown-item divided icon="Pointer" :command="{ type: 2, name: '点击事件' }">
                                  点击事件
                                </el-dropdown-item>
                                <el-dropdown-item divided icon="Edit" :command="{ type: 3, name: '输入事件' }">
                                  输入事件
                                </el-dropdown-item>
                                <el-dropdown-item divided icon="Delete" :command="{ type: 4, name: '清空输入' }">
                                  清空输入
                                </el-dropdown-item>
                                <el-dropdown-item divided icon="Iphone" :command="{ type: 5, name: '手机验证码' }">
                                  手机验证码
                                </el-dropdown-item>
                                <el-dropdown-item divided icon="TurnOff" :command="{ type: 6, name: '关闭app' }">
                                  关闭app
                                </el-dropdown-item>
                                <el-dropdown-item divided icon="Sort" :command="{ type: 7, name: 'Tab键' }">
                                  Tab键
                                </el-dropdown-item>
                                <el-dropdown-item divided icon="Check" :command="{ type: 8, name: '回车键' }">
                                  回车键
                                </el-dropdown-item>
                                <el-dropdown-item divided icon="Document" :command="{ type: 9, name: '热更 push 文件' }">
                                  热更 push 文件
                                </el-dropdown-item>
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
                            <el-tree ref="script_tree" draggable :data="item.content.script" :props="defaultProps"
                              :highlight-current="true" :default-expanded-keys="[1, 10]" :expand-on-click-node="false"
                              @node-click="app_script_click" :allow-drop="on_allowDrop">
                              <template #default="{ node, data }">
                                <div style="
                                    border: 0.5px solid rgb(204, 204, 204);
                                    border-radius: 10px;
                                    width: 97%;
                                    padding-left: 10px;
                                    padding-top: 1.5px;
                                  ">
                                  <el-icon v-if="data.type === 0">
                                    <Download />
                                  </el-icon>
                                  <el-icon v-if="data.type === 1">
                                    <SwitchButton />
                                  </el-icon>
                                  <el-icon v-if="data.type === 2">
                                    <Pointer />
                                  </el-icon>
                                  <el-icon v-if="data.type === 3">
                                    <Edit />
                                  </el-icon>
                                  <el-icon v-if="data.type === 4">
                                    <Delete />
                                  </el-icon>
                                  <el-icon v-if="data.type === 5">
                                    <Iphone />
                                  </el-icon>
                                  <el-icon v-if="data.type === 6">
                                    <TurnOff />
                                  </el-icon>
                                  <el-icon v-if="data.type === 7">
                                    <Sort />
                                  </el-icon>
                                  <el-icon v-if="data.type === 8">
                                    <Check />
                                  </el-icon>
                                  <el-icon v-if="data.type === 9">
                                    <Document />
                                  </el-icon>
                                  <span style="padding-left: 5px">
                                    {{ node.label }}
                                  </span>
                                  <span style="float: right">
                                    <el-button type="text" icon="Remove" style="color: #ea4242"
                                      @click="del_script_info(node)"></el-button>
                                  </span>
                                  <span style="float: right; padding-right: 5px">
                                    <el-switch v-model="data.status" class="size-mini" inline-prompt />
                                  </span>
                                </div>
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
                            ">
                            <el-form :model="script_info">
                              <el-form-item v-if="script_info.type !== ''" label="事件名称：">
                                <el-input v-model="script_info.name"></el-input>
                              </el-form-item>
                              <el-form-item v-if="script_info.type == 1 || script_info.type == 6" label="app包名：">
                                <el-input v-model="script_info.package"></el-input>
                              </el-form-item>
                              <!-- <el-form-item v-if="script_info.type == 8 || script_info.type == 7" label="poco地址：">
                                <el-input v-model="script_info.address"></el-input>
                              </el-form-item> -->
                              <el-form-item
                                v-if="script_info.type == 3 || script_info.type == 7 || script_info.type == 8"
                                label="输入值：">
                                <el-input v-model="script_info.value"></el-input>
                              </el-form-item>
                              <el-form-item v-if="
                                script_info.type == 0 || script_info.type == 2 || script_info.type == 3 || script_info.type == 4 || script_info.type == 5
                              " label="图像识别：">
                                <!-- <el-select v-model="script_info.android.img" filterable>
                                  <el-option v-for="(img, index) in img_select_list" :key="index" :label="img.file_name"
                                    :value="img.id">
                                    <span style="float: left">{{ img.file_name }}</span>
                                    <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
                                      <el-image class="w-200px h-36px" :preview-teleported="true"
                                        :preview-src-list="[img.file_path]" :src="img.file_path != null && img.file_path != ''
                                          ? img.file_path
                                          : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
                                          ">
                                        <template #error>
                                          <el-icon class="c-[--el-color-primary]" :size="36">
                                            <CircleCloseFilled />
                                          </el-icon>
                                        </template>
                                      </el-image>
                                    </span>
                                  </el-option>
                                </el-select> -->
                                <el-cascader v-model="script_info.android.img" :options="img_select_list" filterable
                                  style="width: 100%;" :props="props1" clearable><template #default="{ node, data }">
                                    <span style="float: left">{{ node.label }}</span>
                                    <span v-if="data.file_path != null && data.file_path != ''" style="float: right;">
                                      <el-image class="w-200px h-30px" :preview-teleported="true"
                                        :preview-src-list="[data.file_path]" :src="data.file_path != null && data.file_path != ''
                                          ? data.file_path
                                          : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
                                          ">
                                        <template #error>
                                          <!-- <el-icon class="c-[--el-color-primary]" :size="36">
                                            <CircleCloseFilled />
                                          </el-icon> -->
                                        </template>
                                      </el-image>
                                    </span>
                                  </template></el-cascader>
                              </el-form-item>
                              <el-form-item v-if="script_info.type == 2" label="图像断言：">
                                <el-cascader v-model="script_info.android.assert" :options="img_select_list" filterable
                                  :props="props1" style="width: 100%" clearable><template #default="{ node, data }">
                                    <span style="float: left">{{ node.label }}</span>
                                    <span v-if="data.file_path != null && data.file_path != ''" style="float:
                                    right; color: var(--el-text-color-secondary)">
                                      <el-image class="w-200px h-36px" :preview-teleported="true"
                                        :preview-src-list="[data.file_path]" :src="data.file_path != null && data.file_path != ''
                                          ? data.file_path
                                          : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
                                          ">
                                        <template #error>
                                          <el-icon class="c-[--el-color-primary]" :size="36">
                                            <CircleCloseFilled />
                                          </el-icon>
                                        </template>
                                      </el-image>
                                    </span>
                                  </template></el-cascader>
                                <!-- <el-select v-model="script_info.android.assert" filterable>
                                  <el-option v-for="(img, index) in img_select_list" :key="index" :label="img.file_name"
                                    :value="img.id">
                                    <span style="float: left">{{ img.file_name }}</span>
                                    <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
                                      <el-image class="w-200px h-36px" :preview-teleported="true"
                                        :preview-src-list="[img.file_path]" :src="img.file_path != null && img.file_path != ''
                                          ? img.file_path
                                          : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
                                          ">
                                        <template #error>
                                          <el-icon class="c-[--el-color-primary]" :size="36">
                                            <CircleCloseFilled />
                                          </el-icon>
                                        </template>
                                      </el-image>
                                    </span>
                                  </el-option>
                                </el-select> -->
                              </el-form-item>
                              <el-form-item v-if="script_info.type == 10" label="差更版本号：">
                                <el-input v-model="script_info.install.version"></el-input>
                              </el-form-item>
                              <el-form-item v-if="script_info.type == 10" label="分配设备：">
                                <div>
                                  <div v-for="(item, index) in script_info.install.channel" :key="index"
                                    class="mb-10px">
                                    <el-form inline>
                                      <el-form-item label="渠道号：">
                                        <el-input v-model="item.channel_id" style="width: 80px;"></el-input>
                                      </el-form-item>
                                      <el-form-item label="设备：">
                                        <el-select v-model="item.device_id" filterable style="width: 150px">
                                          <el-option v-for="(item, index) in device_list" :key="index"
                                            :label="item.name" :value="item.deviceid" />
                                        </el-select>
                                        <el-button type="text" icon="CirclePlus"
                                          @click="Add_install(script_info.install.channel)"></el-button>
                                        <el-button type="text" style="color: rgb(219, 97, 120);" icon="Delete"
                                          @click="Del_install(item, index)"></el-button>
                                      </el-form-item>
                                    </el-form>
                                  </div>
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
        </KoiCard>
        <KoiCard style="width: 22%; height: 780px; float: left;">
          <div style="width: 100%; overflow: auto;">
            <div>
              <el-input v-model="filterText" style="margin-bottom: 5px; width: 90%; padding-right: 10px"
                placeholder="请输入节点名称" />
              <el-button type="text" style="padding-left: 5px" icon="Refresh" @click="get_app_menu()" />
            </div>
            <el-tree v-loading="loading" ref="treeRef" class="filter-tree" :data="tree_data" :props="defaultProps"
              default-expand-all :filter-node-method="filterNode" @node-click="app_menu_click"
              :allow-drop="on_menu_allowDrop" draggable>
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
                      <Iphone />
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
                <el-input v-model="add_menu_form.name" placeholder="请输入名称" clearable />
              </el-form-item>
            </el-form>
          </template>
        </KoiDialog>
      </div>
      <div>
        <KoiDialog ref="device_koiDialogRef" :title="title" @koi-confirm="run_confirm" @koi-cancel="run_cancel"
          confirmText="立即启动" :height="dialog_height" :width="1000">
          <template #content>
            <el-form ref="formRef" :model="run_form" label-width="80px" status-icon>
              <el-form-item label="任务名称：" prop="roleName">
                <el-input v-model="run_form.task_name" placeholder="请输入名称" clearable />
              </el-form-item>
              <el-form-item label="类型：">
                <el-radio-group v-model="run_form.run_type">
                  <el-radio :value="1">普通自动化</el-radio>
                  <el-radio :value="2">差更包体自动化</el-radio>
                  <el-radio :value="3">包体已安装（无需分配包体）</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item v-if="run_form.run_type === 2" label="差更版本：" prop="roleCode">
                <el-input v-model="run_form.version" placeholder="请输入版本号" clearable />
              </el-form-item>
              <el-form-item v-if="run_form.run_type === 2" label="渠道id：" prop="roleCode">
                <el-input v-model="run_form.channel_id" placeholder="请输入渠道id" clearable />
              </el-form-item>
              <el-form-item v-if="run_form.run_type == 1" label="配置设备：" prop="roleCode">
                <div>
                  <el-form :model="run_form.app_list">
                    <el-form-item>
                      <el-button @click="add_app_list" plain type="primary">添加安装配置</el-button>
                    </el-form-item>
                    <el-form-item v-for="(app, index) in run_form.app_list" :key="index">
                      <koiCard style="margin-top: 5px;">
                        <div>
                          <el-input v-model="app.path" style="width: 400px; padding-right: 10px;" placeholder="请输入路径" />
                          <el-button @click="search_package(app.path)" type="primary">搜索</el-button>
                        </div>
                        <div class="h-2"></div>
                        <div style="padding-top: 5px;" v-for="(config, config_index) in app.config" :key="config_index">
                          请选择：
                          <el-select v-model="config.package" filterable style="width: 400px; padding-right: 10px"
                            clearable placeholder="请选择包体">
                            <el-option v-for="device in package_list" :key="device.id" :label="device.file_name"
                              :value="device.file_name"></el-option>
                          </el-select>
                          <el-select v-model="config.deviceid" filterable style="width: 200px; padding-right: 10px"
                            clearable placeholder="请选择设备">
                            <el-option v-for="device in device_list" :key="device.deviceid" :label="device.name"
                              :value="device.deviceid"></el-option>
                          </el-select>
                          <el-button @click="add_config(app.config)" type="primary">添加</el-button>
                          <el-button @click="del_config(config_index, app.config)" type="text" style="float: right;"
                            icon="Delete"></el-button>
                        </div>
                      </koiCard>
                      <el-button @click="del_app_list(index)" type="text" icon="Delete"></el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-form-item>
              <el-form-item v-if="run_form.run_type == 2" label="配置设备">
                <el-select v-model="run_form.device_list" multiple placeholder="Select">
                  <el-option v-for="(item, index) in device_list" :key="index" :label="item.name"
                    :value="item.deviceid" />
                </el-select>
              </el-form-item>
            </el-form>
          </template>
        </KoiDialog>
      </div>
      <div>
        <KoiDialog ref="script_list_koiDialogRef" :title="title" @koi-confirm="run_script_confirm"
          @koi-cancel="run_list_cancel" :width="1000" :height="dialog_height" confirmText="立即启动">
          <template #content>
            <el-form ref="formRef" :model="run_form" label-width="80px" status-icon>
              <el-form-item label="任务名称：" prop="roleName">
                <el-input v-model="run_form.task_name" placeholder="请输入名称" clearable />
              </el-form-item>
              <el-form-item label="类型：">
                <el-radio-group v-model="run_form.run_type">
                  <el-radio :value="1">普通自动化</el-radio>
                  <el-radio :value="2">差更包体自动化</el-radio>
                  <el-radio :value="3">包体已安装（无需分配包体）</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item v-if="run_form.run_type === 2" label="差更版本：" prop="roleCode">
                <el-input v-model="run_form.version" placeholder="请输入版本号" clearable />
              </el-form-item>
              <el-form-item v-if="run_form.run_type === 2" label="渠道id：" prop="roleCode">
                <el-input v-model="run_form.channel_id" placeholder="请输入渠道id" clearable />
              </el-form-item>
              <el-form-item v-if="run_form.run_type == 1" label="配置设备：" prop="roleCode">
                <div>
                  <el-form :model="run_form.app_list">
                    <el-form-item>
                      <el-button @click="add_app_list" plain type="primary">添加安装配置</el-button>
                    </el-form-item>
                    <el-form-item v-for="(app, index) in run_form.app_list" :key="index">
                      <koiCard style="margin-top: 5px;">
                        <div>
                          <el-input v-model="app.path" style="width: 400px; padding-right: 10px;" placeholder="请输入路径" />
                          <el-button @click="search_package(app.path)" type="primary">搜索</el-button>
                        </div>
                        <div class="h-2"></div>
                        <div style="padding-top: 5px;" v-for="(config, config_index) in app.config" :key="config_index">
                          请选择：
                          <el-select v-model="config.package" filterable style="width: 400px; padding-right: 10px"
                            clearable placeholder="请选择包体">
                            <el-option v-for="device in package_list" :key="device.id" :label="device.file_name"
                              :value="device.file_name"></el-option>
                          </el-select>
                          <el-select v-model="config.deviceid" filterable style="width: 200px; padding-right: 10px"
                            clearable placeholder="请选择设备">
                            <el-option v-for="device in device_list" :key="device.deviceid" :label="device.name"
                              :value="device.deviceid"></el-option>
                          </el-select>
                          <el-button @click="add_config(app.config)" type="primary">添加</el-button>
                          <el-button @click="del_config(config_index, app.config)" type="text" style="float: right;"
                            icon="Delete"></el-button>
                        </div>
                      </koiCard>
                      <el-button @click="del_app_list(index)" type="text" icon="Delete"></el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-form-item>
              <el-form-item v-if="run_form.run_type == 2" label="配置设备">
                <el-select v-model="run_form.device_list" multiple placeholder="Select">
                  <el-option v-for="(item, index) in device_list" :key="index" :label="item.name"
                    :value="item.deviceid" />
                </el-select>
              </el-form-item>
            </el-form>
          </template>
        </KoiDialog>
      </div>
      <div>
        <KoiDialog ref="run_koiDialogRef" :title="title" :height="680" width="93%" :footer-hidden="true"
          :before-close="run_close">
          <template #content>
            <div style="width: 100%">
              <div style="width: 65%; float: left">
                <el-tabs tab-position="left" class="demo-tabs" v-model="device_active" @tab-click="change_device">
                  <el-tab-pane v-loading="loading" v-for="(item, index) in run_device_list" :key="index"
                    :label="item.name" :name="item.name" :lazy="true">
                    <div>
                      <KoiCard>
                        <div>
                          <el-descriptions column="4">
                            <el-descriptions-item label="任务名称：">{{ run_form.task_name }}</el-descriptions-item>
                            <el-descriptions-item label="设备：">{{ item.name }}</el-descriptions-item>
                            <el-descriptions-item label="操作系统：">{{ item.os_type }}</el-descriptions-item>
                            <el-descriptions-item label="系统版本： ">{{ item.version }}</el-descriptions-item>
                            <!-- <el-descriptions-item label="进程id： ">{{ item.pid }}</el-descriptions-item> -->
                            <el-descriptions-item label="进程状态：">
                              <el-tag type="success" v-if="run_type == '正在执行'">{{ run_type }}</el-tag>
                              <el-tag type="danger" v-if="run_type == '执行结束'">{{ run_type }}</el-tag>
                            </el-descriptions-item>
                            <el-descriptions-item label="执行人：">
                              {{ user.username }}
                            </el-descriptions-item>
                            <el-descriptions-item v-if="run_type == '正在执行'" label="运行：">
                              <el-button type="danger" plain @click="stop_run(item.pid)">停止</el-button>
                            </el-descriptions-item>
                          </el-descriptions>
                        </div>
                      </KoiCard>
                    </div>
                    <div style="padding-top: 5px">
                      <KoiCard style="height: 560px">
                        <div style="width: 100%">
                          <div>
                            <KoiCard style="width: 45%; float: left; height: 530px; overflow: auto">
                              <el-timeline style="width: 85%">
                                <el-timeline-item center v-for="(res, index) in run_result" :key="index"
                                  :icon="getIcon(res.status)" type="primary" :color="colors(res.status)" size="large"
                                  :timestamp="'执行时间：' + res.create_time" placement="top">
                                  <KoiCard :style="get_colors(res.status)">
                                    <span>{{ res.name }}</span>
                                    <span>{{ "结果：" + res.log }}</span>
                                    <span>
                                      <el-popover placement="right" :width="200" trigger="click">
                                        <template #reference>
                                          <el-button v-if="Object.keys(res.assert_value).length !== 0" icon="Search"
                                            type="text" style="float: right">
                                            断言详情
                                          </el-button>
                                        </template>
                                        <div>
                                          <span>{{ "断言结果：" + res.assert_value.result }}</span>
                                          <el-button icon="Picture" type="text" style="float: right"
                                            @click="pre_view(res.assert_value.img)">
                                            查看详情
                                          </el-button>
                                        </div>
                                      </el-popover>
                                      <el-button icon="Picture" type="text" @click="pre_view(res.before_img)"> 执行前
                                      </el-button>
                                      <el-button icon="Picture" type="text" @click="pre_view(res.after_img)"> 执行后
                                      </el-button>
                                      <el-popover placement="right" :width="500" trigger="click">
                                        <template #reference>
                                          <el-button icon="View" type="text" @click="view_script(res.menu_id)"> 步骤
                                          </el-button>
                                        </template>
                                        <div>
                                          <el-tree ref="script_tree" draggable :data="run_script_data"
                                            :props="defaultProps" :highlight-current="true"
                                            :default-expanded-keys="[1, 10]" :expand-on-click-node="false">
                                            <template #default="{ node, data }">
                                              <div style="
                                    border: 0.5px solid rgb(204, 204, 204);
                                    border-radius: 10px;
                                    width: 97%;
                                    padding-left: 10px;
                                    padding-top: 1.5px;
                                  ">
                                                <el-icon v-if="data.type === 0">
                                                  <Download />
                                                </el-icon>
                                                <el-icon v-if="data.type === 1">
                                                  <SwitchButton />
                                                </el-icon>
                                                <el-icon v-if="data.type === 2">
                                                  <Pointer />
                                                </el-icon>
                                                <el-icon v-if="data.type === 3">
                                                  <Edit />
                                                </el-icon>
                                                <el-icon v-if="data.type === 4">
                                                  <Delete />
                                                </el-icon>
                                                <el-icon v-if="data.type === 5">
                                                  <Iphone />
                                                </el-icon>
                                                <el-icon v-if="data.type === 6">
                                                  <TurnOff />
                                                </el-icon>
                                                <el-icon v-if="data.type === 7">
                                                  <Sort />
                                                </el-icon>
                                                <el-icon v-if="data.type === 8">
                                                  <Check />
                                                </el-icon>
                                                <span style="padding-left: 5px">
                                                  {{ node.label }}
                                                </span>
                                                <span style="float: right; padding-right: 5px">
                                                  <el-switch v-model="data.status" class="size-mini" inline-prompt />
                                                </span>
                                              </div>
                                            </template>
                                          </el-tree>
                                        </div>
                                      </el-popover>
                                    </span>
                                    <div class="img-viewer-box">
                                      <el-image-viewer v-if="img_show" :url-list="pre_img" @close="close_img" />
                                    </div>
                                  </KoiCard>
                                </el-timeline-item>
                              </el-timeline>
                            </KoiCard>
                          </div>
                          <div>
                            <KoiCard style="width: 46%; float: left; height: 530px; overflow: auto">
                              <div style="padding-left: 35%">
                                <el-progress type="dashboard" :percentage="percentage" status="success">
                                  <template #default="{ percentage }">
                                    <span class="percentage-value">{{ percentage }}%</span>
                                    <span class="percentage-label">通过率</span>
                                  </template>
                                </el-progress>
                              </div>
                              <div>
                                <el-descriptions :column="1">
                                  <el-descriptions-item label="执行的包体：">
                                    {{ item.package }}
                                  </el-descriptions-item>
                                  <el-descriptions-item label="手机实时页面：">
                                    <el-button type="primary" plain @click="view_phone()">查看手机页面</el-button>
                                  </el-descriptions-item>
                                  <el-descriptions-item label="是否已修正：">
                                    <el-button type="primary" plain @click="run_app_correction()">已修正点击此按钮</el-button>
                                  </el-descriptions-item>
                                </el-descriptions>
                                <el-descriptions column="2">
                                  <el-descriptions-item label="脚本总数：">{{ script_total }} 个</el-descriptions-item>
                                  <el-descriptions-item label="未执行：">{{ script_un_run }}个</el-descriptions-item>
                                  <el-descriptions-item label="执行通过：">
                                    <el-tag type="success"> {{ script_pass }} 个 </el-tag>
                                  </el-descriptions-item>
                                  <el-descriptions-item label="执行失败：">
                                    <el-tag type="danger"> {{ script_fail }} 个 </el-tag>
                                  </el-descriptions-item>
                                </el-descriptions>
                                <el-descriptions column="1">
                                  <el-descriptions-item label="开始时间：">{{ start_time }}</el-descriptions-item>
                                  <el-descriptions-item label="结束时间：">{{ end_time }}</el-descriptions-item>
                                  <el-descriptions-item v-if="pre_video !== ''" label="视频详情：">
                                    <el-button icon="VideoPlay" type="text" @click="pre_view_video">查看视频详情</el-button>
                                  </el-descriptions-item>
                                </el-descriptions>

                              </div>
                            </KoiCard>
                          </div>
                        </div>
                      </KoiCard>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
              <div style="width: 33%; float: left; padding-left: 5px">
                <KoiCard style="width: 100%; float: left; height: 660px; overflow: auto">
                  <p>{{ device_active }}：性能情况：</p>
                  <div id="chart" class="echarts" style="width: 100%; height: 600px"></div>
                </KoiCard>
              </div>
            </div>
          </template>
        </KoiDialog>
      </div>
      <div>
        <KoiDrawer ref="device_koiDrawerRef" :title="device_active" :footerHidden="true" :size="830"
          :beforeCloseCheck="false">
          <template #content>
            <div>
              <iframe :src="device_url" style="width: 98%; height: 730px" />
            </div>
          </template>
        </KoiDrawer>
      </div>
    </KoiCard>
  </div>
</template>

<style scoped lang="scss">
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
</style>
