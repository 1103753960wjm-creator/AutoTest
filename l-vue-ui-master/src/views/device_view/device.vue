<script setup lang="ts">
import { onMounted, ref } from 'vue';
import {
  device_info_list, use_device, stop_device,
  get_device_log, get_history_list, device_install_app,
  direct_install_app, add_device,
  device_performance
} from '@/api/api_app/device'
import { MsgBox, MsgError, MsgSuccess, NoticeError, NoticeSuccess } from "@/utils/koi.ts";
import { ElIcon, ElLoading } from 'element-plus';
import jsonE from "@/components/CodeEditor/jsonE.vue";
import * as echarts from "echarts";
import VueJsonPretty from "vue-json-pretty";
import "vue-json-pretty/lib/styles.css";
import { mitmproxy_check, mitmproxy_close_agent, mitmproxy_run_log, mitmproxy_single_start } from '@/api/api_mitmproxy/mitmproxy';

const device_type = ref<any>("");
const device_version = ref<any>("");
const device_status = ref<any>("");
const device_list = ref<any>([]);
const total = ref<any>(0);
const use_koiDialogRef = ref<any>(null);
const title = ref<any>("");
const searchParams = ref({
  search: {
    device_version: null,
    device_type: null,
    device_status: null
  },
  currentPage: 1,
  pageSize: 24
});
const apk_path = ref<any>("");
const use_active = ref<any>("");
const install_history = ref<any>([]);
const history_searchParams = ref({
  search: {
    device_id: ''
  },
  currentPage: 1,
  pageSize: 10
});
const log_searchParams = ref({
  search: {
    device_id: null
  },
  currentPage: 1,
  pageSize: 10
});
const device_log = ref<any>([]);
const history_total = ref<any>(0);
const device_url = ref<any>("");
const shell_url = ref<any>("");
const file_url = ref<any>("");
const device_id = ref<any>("");
const log_id = ref<any>(null);
const phone_id = ref<any>(null);
const log_total = ref<any>(0);
const getDeviceList = async () => {
  const loadingInstance = ElLoading.service({
    text: "手机设备加载中，请稍后！",
    background: "rgba(0,0,0,.2)"
  });
  searchParams.value.search.device_version = device_version.value
  searchParams.value.search.device_type = device_type.value
  searchParams.value.search.device_status = device_status.value
  const res = await device_info_list(searchParams.value)
  device_list.value = res.data.content
  total.value = res.data.total
  loadingInstance.close();
}

const use_status = ref<any>(false);
const wifi_ip = ref<any>("");
const use_phone = async (phone: any) => {
  if (phone.device_type == 1) {
    title.value = phone.device_name + "（手机号：" + phone.device_info.phone + "----系统版本：HormonyOS " + phone.device_version + "）";
  } else {
    title.value = phone.device_name + "（手机号：" + phone.device_info.phone + "----系统版本：Android " + phone.device_version + "）";
  }
  device_id.value = phone.device_id
  phone_id.value = phone.id
  use_active.value = "install"
  wifi_ip.value = phone.wifi_ip
  const res: any = await use_device({
    "device_id": device_id.value,
    "id": phone_id.value,
    "wifi_ip": wifi_ip.value,
    "port": 8088
  });
  if (res.code != 200) {
    MsgError(res.message);
    return;
  }
  log_id.value = res.data.log_id
  device_url.value = res.data.device_url;
  file_url.value = res.data.file_url
  await get_log_list();
  await get_history();
  use_koiDialogRef.value.koiOpen();
  use_status.value = true
};

const stop_phone = async () => {
  MsgBox("您确认停止使用：" + title.value).then(async () => {
    use_koiDialogRef.value.koiClose();
    const res: any = await stop_device({
      "log_id": log_id.value,
      "id": phone_id.value
    });
    if (res.code == 200) {
      await getDeviceList();
      device_url.value = ""
      file_url.value = ""
      use_status.value = false;
      start_status.value = false;
      performance.value = {
        cpu: [],
        memory: [],
        time: [],
        temperature: [],
        up_network: [],
        down_network: []
      };
      stopPolling();
      await mitmproxy_stop();
      await mitmproxy_log_stoppolling();
    }
  });
};

const mitmproxy_log = ref<any>([]);
const result_id = ref<any>("");
const mitmproxy_log_total = ref<any>(0);
const mitmproxy_log_searchParams = ref({
  search: {
    device_id: null,
    result_id: ""
  },
  currentPage: 1,
  pageSize: 18
});
const mitmproxy_interval = ref<any>(null);

const mitmproxy_log_list = async () => {
  mitmproxy_log_searchParams.value.search.device_id = phone_id.value;
  mitmproxy_log_searchParams.value.search.result_id = result_id.value;
  const res: any = await mitmproxy_run_log(mitmproxy_log_searchParams.value);
  mitmproxy_log.value = res.data.content;
  mitmproxy_log_total.value = res.data.total;
};

const mitmproxy_log_polling = async () => {
  if (mitmproxy_interval.value) return; // 避免重复启动
  mitmproxy_interval.value = setInterval(mitmproxy_log_list, 5000); // 每5秒轮询一次
};

// 停止轮询
const mitmproxy_log_stoppolling = async () => {
  if (mitmproxy_interval.value) {
    clearInterval(mitmproxy_interval.value);
    mitmproxy_interval.value = null;
  }
};

const mitmproxy_start = async (data: any) => {
  await mitmproxy_single_start(data);
};

const mitmproxy_check_status = async () => {
  const res: any = await mitmproxy_check({
    "deviceid": device_id.value,
  });
  if (res.data.status === "stop") {
    await mitmproxy_start({
      "deviceid": device_id.value,
      "id": phone_id.value,
      "port": 8088,
      "result_id": result_id.value,
      "wifi_ip": wifi_ip.value,
    });
    mitmproxy_log_polling();
  } else {
    mitmproxy_log_polling();
  }
};

const mitmproxy_stop = async () => {
  await mitmproxy_close_agent({
    "deviceid": device_id.value,
  });
};

const mitmproxy_koiDialogRef = ref<any>(null);
const mitmproxy_api_details = ref<any>({});
const mitmproxy_log_detail = async (row: any) => {
  mitmproxy_koiDialogRef.value.koiOpen();
  mitmproxy_api_details.value = row;
};

document.addEventListener("keydown", async (event: any) => {
  if (event.key === "Escape" && use_status.value === true) {
    console.log('Esc键被按下，关闭对话框')
    await stop_phone();
  }
})

const loading = ref<any>(false);
const call_back = async (fileMap: any) => {
  MsgSuccess("上传文件成功");
  fileMap.device_id = device_id.value;
  fileMap.phone_id = phone_id.value;
  loading.value = true;
  const res: any = await device_install_app(fileMap);
  if (res.code == 200) {
    NoticeSuccess(fileMap.filename + "，安装成功🌻", "温馨提示", 0, "success");
    await get_history();
  } else {
    NoticeError(fileMap.filename + "，安装失败，原因：" + res.message, "温馨提示", 0, "error");
  }
  loading.value = false;
};

const get_log_list = async () => {
  log_searchParams.value.search.device_id = phone_id.value;
  const res: any = await get_device_log(log_searchParams.value);
  device_log.value = res.data.content;
  log_total.value = res.data.total;
};

const get_history = async () => {
  // history_searchParams.value.search.device_id = phone_id.value;
  history_searchParams.value.search.device_id = '';
  const res: any = await get_history_list(history_searchParams.value);
  install_history.value = res.data.content;
  history_total.value = res.data.total;
};

const install_app = async (row: any) => {
  loading.value = true;
  const res: any = await direct_install_app({
    "device_id": device_id.value,
    "id": row.id,
    "filename": row.apk_name
  });
  if (res.code == 200) {
    NoticeSuccess(row.apk_name + "，安装成功🌻", "温馨提示", 0, "success");
  } else {
    NoticeError(row.apk_name + "，安装失败，原因：" + res.message, "温馨提示", 0, "error");
  }
  loading.value = false;
};

const add_device_form = ref<any>({});
const add_device_koiDialogRef = ref<any>(null);
const Add_device = async () => {
  title.value = "添加设备";
  add_device_koiDialogRef.value.koiOpen();
  add_device_form.value = {
    device_name: "",
    device_info: {},
    device_type: "",
    device_version: "",
    device_status: "",
    device_id: "",
    file_path: "",
    device_description: "xxxx"
  };
  add_device_form.value.device_info = JSON.stringify({
    cpu: "",
    phone: "",
    memory: "",
    screen: "",
    battery: "",
    display: "",
    running_memory: ""
  });
}

const add_device_cancel = async () => {
  add_device_koiDialogRef.value.koiQuickClose("已取消");
};

const add_device_confirm = async () => {
  const res: any = await add_device(add_device_form.value);
  if (res.code == 200) {
    MsgSuccess(res.message);
  }
};

const tab_click = (tab: any) => {
  if (tab.props.name == "fourth" && start_status.value == false) {
    startPolling();
  } else if (tab.props.name == "third") {
    mitmproxy_check_status();
  } else {
    stopPolling();
    mitmproxy_log_polling();
  }
};

const performance = ref<any>({
  cpu: [],
  memory: [],
  time: [],
  temperature: [],
  up_network: [],
  down_network: []
});

const get_device_performance = async () => {
  const res: any = await device_performance({
    "device_id": device_id.value,
    "performance": performance.value
  });
  performance.value = res.data;
  await perform_result(res.data);
};

const interval = ref<any>(null); // 保存轮询的定时器 ID
const start_status = ref<any>(false);
// 开始轮询
const startPolling = async () => {
  if (interval.value) return; // 避免重复启动
  start_status.value = true;
  interval.value = setInterval(get_device_performance, 3000); // 每5秒轮询一次
};

// 停止轮询
const stopPolling = () => {
  if (interval.value) {
    start_status.value = false;
    clearInterval(interval.value);
    interval.value = null;
  }
};

const per_time = ref<any>([]);
const cpu = ref<any>([]);
const memory = ref<any>([]);
const up_network = ref<any>([]);
const down_network = ref<any>([]);
const temperature = ref<any>([]);

const perform_result = async (res: any) => {
  per_time.value = res.time;
  cpu.value = res.cpu;
  memory.value = res.memory;
  up_network.value = res.up_network;
  down_network.value = res.down_network;
  temperature.value = res.temperature;
  await getEcharts();
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
      name: "下载网速(MB/s)",
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


onMounted(() => {
  getDeviceList();
  result_id.value = String(Date.now());
})

</script>

<template>
  <div>
    <div>
      <koiCard>
        <div>
          <el-radio-group v-model="device_type" @change="getDeviceList">
            <el-button style="margin-right: 10px;" type="text" icon="Refresh" plain
              @click="getDeviceList">刷新状态</el-button>
            <el-radio :label="0" value="0" disabled>手机品牌：</el-radio>
            <el-radio :label="100" value="">所有设备</el-radio>
            <el-radio :label="1" value="1">华为</el-radio>
            <el-radio :label="2" value="2">小米</el-radio>
            <el-radio :label="3" value="3">OPPO</el-radio>
            <el-radio :label="4" value="4">荣耀</el-radio>
            <el-radio :label="5" value="5">Vivo</el-radio>
            <el-radio :label="6" value="6">夏普</el-radio>
            <el-radio :label="7" value="7">一加</el-radio>
            <el-radio :label="8" value="8">三星</el-radio>
            <el-radio :label="9" value="9">Google</el-radio>1
            <el-radio :label="10" value="10">IPhone</el-radio>
          </el-radio-group>
        </div>
        <div>
          <el-radio-group v-model="device_version" @change="getDeviceList">
            <el-button style="margin-right: 10px;" type="text" icon="Plus" plain @click="Add_device">添加设备</el-button>
            <el-radio :label="0" value="0" disabled>系统版本：</el-radio>
            <el-radio :label="100" value="">所有版本</el-radio>
            <el-radio :label="16" value="16">16</el-radio>
            <el-radio :label="15" value="15">15</el-radio>
            <el-radio :label="14" value="14">14</el-radio>
            <el-radio :label="13" value="13">13</el-radio>
            <el-radio :label="12" value="12">12</el-radio>
            <el-radio :label="11" value="11">11</el-radio>
            <el-radio :label="10" value="10">10</el-radio>
          </el-radio-group>
        </div>
        <div>
          <el-radio-group v-model="device_status" @change="getDeviceList">
            <el-radio :label="0" value="0" disabled>设备状态</el-radio>
            <el-radio :label="100" value="">所有状态</el-radio>
            <el-radio :label="1" :value="1">空闲</el-radio>
            <el-radio :label="2" :value="2">使用中</el-radio>
            <el-radio :label="3" :value="3">离线</el-radio>
          </el-radio-group>
        </div>
      </koiCard>
      <koiCard>
        <el-row :gutter="8">
          <el-col style="padding-block-end: 5px;" :span="3" :lg="3.5" :md="3" :sm="3" :xs="3"
            v-for="(item, index) in device_list" :key="index">
            <el-card style="padding: 5px;" shadow="hover">
              <div class="flex justify-center">
                <el-badge v-if="item.device_status == 1" value="空闲" class="item" type="success" :offset="[-130, 5]">
                  <el-image :src="item.file_path" style="width: 120px; height: 120px;" />
                </el-badge>
                <el-badge v-if="item.device_status == 2" value="使用中" class="item" type="danger" :offset="[-140, 5]">
                  <el-image :src="item.file_path" style="width: 120px; height: 120px;" />
                </el-badge>
                <el-badge v-if="item.device_status == 3" value="离线" class="item" type="info" :offset="[-130, 5]">
                  <el-image :src="item.file_path" style="width: 120px; height: 120px;" />
                </el-badge>
              </div>
              <div class="flex justify-center">
                <span>
                  <div style="font-size: 14px;">{{ item.device_name }}</div>
                  <div style="font-size: 14px;">{{ item.device_info.phone }}</div>
                </span>
              </div>
              <div class="flex justify-center">
                <el-popover placement="top-start" :width="200" trigger="hover"
                  content="this is content, this is content, this is content">
                  <div>
                    <el-descriptions :title="item.device_name" column="1">
                      <el-descriptions-item label="手机卡:">{{ item.device_info.phone }}</el-descriptions-item>
                      <el-descriptions-item v-if="item.device_type === '1'" label="系统版本:">{{ 'HormonyOS ' +
                        item.device_version }}</el-descriptions-item>
                      <el-descriptions-item v-if="item.device_type !== '1'" label="系统版本:">{{ item.device_version
                      }}</el-descriptions-item>
                      <el-descriptions-item label="CPU:">{{ item.device_info.cpu }}</el-descriptions-item>
                      <el-descriptions-item label="内存:">{{ item.device_info.memory }}</el-descriptions-item>
                      <el-descriptions-item label="运行内存:">{{ item.device_info.running_memory }}</el-descriptions-item>
                      <el-descriptions-item label="电池:">{{ item.device_info.battery }}</el-descriptions-item>
                      <el-descriptions-item label="分辨率:">{{ item.device_info.display }}</el-descriptions-item>
                      <el-descriptions-item label="屏幕尺寸:">{{ item.device_info.screen }}</el-descriptions-item>
                    </el-descriptions>
                  </div>
                  <template #reference>
                    <el-button type="text" ref="buttonRef" size="small" icon="View">设备信息</el-button>
                  </template>
                </el-popover>
                <el-button v-if="item.device_status == 1" type="text" size="small" icon="Pointer"
                  @click="use_phone(item)">立即使用</el-button>
                <el-button v-if="item.device_status != 1" disabled type="text" size="small" icon="Pointer"
                  @click="use_phone(item)">立即使用</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <div class="h-5px"></div>
        <el-pagination v-model:current-page="searchParams.currentPage" v-model:page-size="searchParams.pageSize"
          :total="total" :page-sizes="[24, 50, 100]" layout="total, sizes, prev, pager, next, jumper"
          @size-change="getDeviceList" @current-change="getDeviceList" />
      </koiCard>
    </div>
    <div>
      <koiDialog ref="use_koiDialogRef" :show-close="false" :before-close-check="false" :title="title" :height="740"
        width="94%" confirmText="停止使用" @koi-confirm="stop_phone" @koi-cancel="stop_phone">
        <template #content>
          <div style="height: 730px; width: 100%">
            <div style="width: 46%; float: left;">
              <iframe :src="device_url" style="width: 97%; height: 730px" />
            </div>
            <div style="float: right; width: 54%;">
              <el-tabs v-model="use_active" type="card" class="demo-tabs" @tab-click="tab_click">
                <el-tab-pane label="安装APP" name="install">
                  <div>
                    <div class="flex justify-center">
                      <KoiUploadFiles v-model="apk_path" :acceptType="'.apk,.aab'" :acceptTypes="'.apk, .aab'"
                        :file-name="apk_path" @fileSuccess="call_back" />
                    </div>
                    <div class="h-10px"></div>
                    <div v-loading="loading" element-loading-text="正在安装包体，请留意手机页面...">
                      <el-table border :data="install_history" empty-text="暂时没有数据哟🌻">
                        <el-table-column label="序号" prop="id" align="left" type="index" width="50px"></el-table-column>
                        <el-table-column label="设备ID" prop="device_name" align="left" width="120px"
                          :show-overflow-tooltip="true"></el-table-column>
                        <el-table-column label="包体名称" prop="apk_name" align="left"
                          :show-overflow-tooltip="true"></el-table-column>
                        <el-table-column label="执行人" prop="username" align="left" width="70px"></el-table-column>
                        <el-table-column label="安装时间" prop="create_time" align="left" width="140px"></el-table-column>
                        <el-table-column label="操作" align="center" fixed="right" width="100px">
                          <template #default="{ row }">
                            <el-button type="text" @click="install_app(row)">重新安装</el-button>
                          </template>
                        </el-table-column>
                      </el-table>
                      <div class="h-10px"></div>
                      <el-pagination background v-model:current-page="history_searchParams.currentPage"
                        v-model:page-size="history_searchParams.pageSize" v-show="history_total > 0"
                        :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next, jumper"
                        :total="history_total" @size-change="get_history" @current-change="get_history" />
                    </div>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="设备终端" name="first">
                  <div style="width: 100%; float: left;">
                    <iframe :src="shell_url" style="width: 98%; height: 650px" />
                  </div>
                </el-tab-pane>
                <el-tab-pane label="文件列表" name="second">
                  <div style="width: 100%; float: left;">
                    <iframe :src="file_url" style="width: 100%; height: 650px" />
                  </div>
                </el-tab-pane>
                <el-tab-pane label="设备抓包" name="third">
                  <div>
                    <KoiCard style="width: 100%; float: left; height: 660px; overflow: auto">
                      <el-table border :data="mitmproxy_log" empty-text="暂时没有数据哟🌻">
                        <el-table-column label="" align="center" width="30px">
                          <template #default="{ row }">
                            <div v-if="row.status === 1" style="color: #0bbd87"><el-icon>
                                <CircleCheck />
                              </el-icon></div>
                            <div v-if="row.status === 0" style="color: #d70e0e"><el-icon>
                                <CircleClose />
                              </el-icon></div>
                          </template>
                        </el-table-column>
                        <el-table-column label="URL" prop="url" align="left" width="435px"
                          :show-overflow-tooltip="true"></el-table-column>
                        <!-- <el-table-column label="Method" prop="method" align="left" width="110px">
                          <template #default="{ row }">
                            <el-tag v-if="row.method === 'GET'" type="success">GET({{ row.res_time + 'ms' }})</el-tag>
                            <el-tag v-if="row.method === 'POST'" type="danger">POST({{ row.res_time + 'ms' }})</el-tag>
                            <el-tag v-if="row.method === 'PUT'" type="warning">PUT({{ row.res_time + 'ms' }})</el-tag>
                            <el-tag v-if="row.method === 'DELETE'" type="info">DELETE({{ row.res_time + 'ms'
                            }})</el-tag>
                          </template>
                        </el-table-column> -->
                        <el-table-column label="响应码" align="center" width="65px">
                          <template #default="{ row }">
                            <el-tag v-if="row.response_body.code === 200" type="success">{{ row.response_body.code
                            }}</el-tag>
                            <el-tag v-if="row.response_body.code !== 200" type="danger">{{ row.response_body.code
                            }}</el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column label="接口响应数据" align="left" :show-overflow-tooltip="true" width="200px">
                          <template #default="{ row }">
                            {{ row.response_body }}
                          </template>
                        </el-table-column>
                        <el-table-column label="请求时间" prop="create_time" :show-overflow-tooltip="true" width="140px">

                        </el-table-column>
                        <el-table-column label="操作" align="center" width="70px">
                          <template #default="{ row }">
                            <el-button type="success" plain @click="mitmproxy_log_detail(row)">详情</el-button>
                          </template>
                        </el-table-column>
                      </el-table>
                      <div class="h-10px"></div>
                      <el-pagination background v-model:current-page="mitmproxy_log_searchParams.currentPage"
                        v-model:page-size="mitmproxy_log_searchParams.pageSize" v-show="mitmproxy_log_total > 0"
                        :page-sizes="[18]" layout="total, sizes, prev, pager, next, jumper" :total="mitmproxy_log_total"
                        @size-change="mitmproxy_log_list" @current-change="mitmproxy_log_list" />
                    </KoiCard>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="设备性能" name="fourth">
                  <div>
                    <KoiCard style="width: 100%; float: left; height: 660px; overflow: auto">
                      <div id="chart" class="echarts" style="width: 100%; height: 600px"></div>
                    </KoiCard>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="使用记录" name="sixth">
                  <el-table border :data="device_log" empty-text="暂时没有数据哟🌻">
                    <el-table-column label="序号" prop="id" align="left" type="index"></el-table-column>
                    <el-table-column label="操作人" prop="username" align="left" width="120px"></el-table-column>
                    <el-table-column label="开始时间" prop="start_time" align="left"></el-table-column>
                    <el-table-column label="结束时间" prop="end_time" align="left"></el-table-column>
                    <el-table-column label="操作" align="center" fixed="right" width="120px">
                      <template #default="{ row }">
                        <el-button type="text" @click="install_app(row)">重新安装</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                  <div class="h-10px"></div>
                  <el-pagination background v-model:current-page="log_searchParams.currentPage"
                    v-model:page-size="log_searchParams.pageSize" v-show="log_total > 0" :page-sizes="[10, 20, 50]"
                    layout="total, sizes, prev, pager, next, jumper" :total="log_total" @size-change="get_log_list"
                    @current-change="get_log_list" />
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </template>
      </koiDialog>
    </div>
    <div>
      <koiDialog ref="add_device_koiDialogRef" :title="title" :height="570" width="700"
        @koi-confirm="add_device_confirm" @koi-cancel="add_device_cancel">
        <template #content>
          <el-form :model="add_device_form" label-position="left">
            <el-form-item label="设备名称：">
              <el-input v-model="add_device_form.device_name" />
            </el-form-item>
            <el-form-item label="设备类型：">
              <el-input v-model="add_device_form.device_type" />
            </el-form-item>
            <el-form-item label="设备版本：">
              <el-input v-model="add_device_form.device_version" />
            </el-form-item>
            <el-form-item label="设备状态：">
              <el-input v-model="add_device_form.device_status" />
            </el-form-item>
            <el-form-item label="设备 I D ：">
              <el-input v-model="add_device_form.device_id" />
            </el-form-item>
            <el-form-item label="设备图片：">
              <KoiUploadImage v-model:image-url="add_device_form.file_path">
                <template #content>
                  <el-icon>
                    <Avatar />
                  </el-icon>
                  <span>请上传图片</span>
                </template>
              </KoiUploadImage>
            </el-form-item>
            <el-form-item label="设备信息：">
              <jsonE v-model:value="add_device_form.device_info" :height="'200px'" />
            </el-form-item>
          </el-form>
        </template>
      </koiDialog>
    </div>
    <div>
      <koiDialog ref="mitmproxy_koiDialogRef" :title="'请求详情'" :height="660" width="1000" :footer-hidden="true"
        :before-close-check="false">
        <template #content>
          <span style="color: rgb(18 31 205);">
            <div>URL：{{ mitmproxy_api_details.url }}</div>
          </span>
          <div style="color: rgb(18 31 205);">请求方法：{{ mitmproxy_api_details.method + ' ---' }} 响应时长：{{
            mitmproxy_api_details.res_time + ' ms' }}</div>
          <el-tabs>
            <el-tab-pane label="Request Headers">
              <vue-json-pretty v-model:data="mitmproxy_api_details.request_headers" :height="250" :showIcon="true"
                :showLine="true" :virtual="true" :showSelectController="true" />
            </el-tab-pane>
            <el-tab-pane label="Request Body">
              <vue-json-pretty v-model:data="mitmproxy_api_details.request_body" :height="250" :showIcon="true"
                :showLine="true" :virtual="true" :showSelectController="true" />
            </el-tab-pane>
          </el-tabs>
          <el-tabs>
            <el-tab-pane label="Response Headers">
              <vue-json-pretty v-model:data="mitmproxy_api_details.response_headers" :height="250" :showIcon="true"
                :showLine="true" :virtual="true" :showSelectController="true" />
            </el-tab-pane>
            <el-tab-pane label="Response Body">
              <vue-json-pretty v-model:data="mitmproxy_api_details.response_body" :height="250" :showIcon="true"
                :showLine="true" :virtual="true" :showSelectController="true" />
            </el-tab-pane>
          </el-tabs>
        </template>
      </koiDialog>
    </div>
  </div>
</template>

<style lang="scss"></style>
