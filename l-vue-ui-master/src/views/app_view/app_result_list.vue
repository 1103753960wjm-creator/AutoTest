<script setup lang="ts">
import { onMounted, ref } from "vue";
import { app_result, app_result_detail, get_process, get_result_list, pid_status, stop_process, view_script_list, app_correction } from "@/api/api_app/app.ts";
import { TabsPaneContext } from "element-plus";
import { MsgError, MsgSuccess } from "@/utils/koi";
import * as echarts from "echarts";
import { app_view_device } from "@/api/api_app/device";
import { ElLoading } from 'element-plus';
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
    task_name__icontaints: ""
  }
});
//总数
const total = ref<number>(0);

const result_list = async () => {
  loading.value = true;
  const res: any = await get_result_list(searchParams.value);
  table_list.value = res.data.content;
  total.value = res.data.total;
  console.log(table_list.value);
  loading.value = false;
};

const reset_search = async () => {
  searchParams.value = {
    currentPage: 1, // 第几页
    pageSize: 10, // 每页显示多少条
    search: {
      task_name__icontaints: ""
    }
  };
  await result_list();
};


const run_device_list = ref<any>([]);
const device_active = ref<any>("");
const title = ref<any>("");
const per_time = ref<any>([]);
const cpu = ref<any>([]);
const memory = ref<any>([]);
const up_network = ref<any>([]);
const down_network = ref<any>([]);
const temperature = ref<any>([]);
const percentage = ref<number>();
const script_pass = ref<number>();
const script_fail = ref<number>();
const start_time = ref<any>("");
const end_time = ref<any>("");
const script_total = ref<number>();
const script_un_run = ref<number>();
const run_koiDialogRef = ref();
const run_pid = ref<any>(null);
const device_url = ref<any>("");
const device = ref<any>("");
const result_id = ref<any>(null);
const run_result = ref<any>([]);
const pre_video = ref<any>("");
const username = ref<any>(null);
const task_name = ref<any>(null);
const defaultProps = {
  children: "children",
  label: "name"
};
const view_result = async (data: any) => {
  const res: any = await get_process({
    "device_list": data.device_list
  });
  if (res.data.status !== "stop") {
    title.value = data.task_name + " - 实时页面";
    result_id.value = data.result_id;
    task_name.value = data.task_name;
    username.value = data.username;
    run_pid.value = data.device_list[0].pid;
    device_active.value = data.device_list[0].name;
    device.value = data.device_list[0].deviceid;
    run_device_list.value = data.device_list;
    run_koiDialogRef.value.koiOpen();
    const loadingInstance = ElLoading.service({
      text: "正在加载实时页面，请稍后...",
      background: "rgba(0,0,0,.2)"
    });
    await startPolling();
    await getEcharts();
    loadingInstance.close()
  } else {
    MsgError("任务已执行完成，请查看测试报告");
  }
};

const change_device = async (pane: TabsPaneContext) => {
  stopPolling();
  device_url.value = "";
  run_device_list.value.forEach((item: any) => {
    if (item.name == pane.props.name) {
      run_result.value = [];
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

const device_koiDrawerRef = ref<any>();
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

const run_type = ref<string>("");
const get_pid_status = async () => {
  const res: any = await pid_status({
    pid: run_pid.value
  });
  run_type.value = res.message;
  // const res_number: number = await result_check();
  // console.log(res_number);
  if (res.message == "执行结束") {
    stopPolling();
    run_type.value = "执行结束";
    await get_details(result_id.value);
  }
  await get_result();
};

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

// const result_check = async () => {
//   let result_umber = 0;
//   for (const item of run_result.value) {
//     if (item.status === 0) {
//       result_umber++;
//     }
//   }
//   return result_umber;
// };

const run_script_data = ref<any>([]);
const view_script = async (item: any) => {
  const res: any = await view_script_list({
    menu_id: item
  });
  if (res.code == 200) {
    run_script_data.value = res.data;
  }
};
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

// 预览图片，视频
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
const view_report = async (result_id: any) => {
  // 待修改：前端地址ip:port
  window.open(`${REPORT_BASE_URL}/app_report?result_id=${result_id}`);
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
            <el-input placeholder="请输入任务名称" v-model="searchParams.search.task_name__icontaints" clearable
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
          <el-table-column label="测试用例" prop="device_list" width="180px" align="center">
            <template #default="{ row }">
              <el-popover placement="top" :width="200" trigger="hover">
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
          <el-table-column label="执行设备" prop="device_list" width="180px" align="center">
            <template #default="{ row }">
              <el-popover placement="top" trigger="hover">
                <div v-for="device in row.device_list" :key="device.id" style="padding-block-end: 3px">
                  <el-tag>{{ device.name }}</el-tag>
                </div>
                <template #reference>
                  <el-button type="text">设备详情</el-button>
                </template>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column label="通过率" prop="percent" width="180px" align="center">
            <template #default="{ row }">
              <el-progress :percentage="row.percent" :color="customColors"></el-progress>
            </template>
          </el-table-column>
          <el-table-column label="执行人" prop="username" width="130px" align="center"></el-table-column>
          <el-table-column label="开始时间" prop="start_time" width="180px" align="center"></el-table-column>
          <el-table-column label="结束时间" prop="end_time" width="180px" align="center"></el-table-column>
          <el-table-column label="操作" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="success" plain icon="Iphone" @click="view_result(row)">查看实时画面</el-button>
              <el-button type="info" plain icon="Tickets" @click="view_report(row.result_id)">查看测试报告</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="h-10px"></div>
        <el-pagination background v-model:current-page="searchParams.currentPage"
          v-model:page-size="searchParams.pageSize" v-show="total > 0" :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="result_list"
          @current-change="result_list" />
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
                            <el-descriptions-item label="任务名称：">{{ task_name }}</el-descriptions-item>
                            <el-descriptions-item label="设备：">{{ item.name }}</el-descriptions-item>
                            <el-descriptions-item label="操作系统：">{{ item.os_type }}</el-descriptions-item>
                            <el-descriptions-item label="系统版本： ">{{ item.version }}</el-descriptions-item>
                            <!-- <el-descriptions-item label="进程id： ">{{ item.pid }}</el-descriptions-item> -->
                            <el-descriptions-item label="进程状态：">
                              <el-tag type="success" v-if="run_type == '正在执行'">{{ run_type }}</el-tag>
                              <el-tag type="danger" v-if="run_type == '执行结束'">{{ run_type }}</el-tag>
                            </el-descriptions-item>
                            <el-descriptions-item label="执行人：">
                              {{ username }}
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
                              <el-timeline style="width: 88%">
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
                                          <el-button icon="View" type="text" @click="view_script(res.menu_id)"> 查看步骤
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
                                <el-descriptions column="1">
                                  <el-descriptions-item label="手机实时页面：">
                                    <el-button type="text" plain @click="view_phone()">查看手机页面</el-button>
                                  </el-descriptions-item>
                                  <el-descriptions-item label="是否已修正：">
                                    <el-button type="text" plain @click="run_app_correction()">已修正点击此按钮</el-button>
                                  </el-descriptions-item>
                                </el-descriptions>
                                <el-descriptions column="2">
                                  <el-descriptions-item label="脚本总数：">{{ script_total }} 个</el-descriptions-item>
                                  <el-descriptions-item label="未执行：">{{ script_un_run }} 个</el-descriptions-item>
                                </el-descriptions>
                                <el-descriptions column="2">
                                  <el-descriptions-item label="执行通过：">
                                    <el-tag type="success"> {{ script_pass }} 个 </el-tag>
                                  </el-descriptions-item>
                                  <el-descriptions-item label="执行失败：">
                                    <el-tag type="danger"> {{ script_fail }} 个 </el-tag>
                                  </el-descriptions-item>
                                  <el-descriptions-item label="开始时间：">{{ start_time }}</el-descriptions-item>
                                  <el-descriptions-item label="结束时间：">{{ end_time }}</el-descriptions-item>
                                </el-descriptions>
                                <div v-show="pre_video !== ''">
                                  <el-button icon="VideoPlay" type="text" @click="pre_view_video">查看视频详情</el-button>
                                </div>
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
    </koiCard>
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

.el-tree {
  --el-tree-node-content-height: 30px;
}
</style>
