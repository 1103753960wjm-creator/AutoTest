<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { get_web_result_report, get_web_result_detail } from "@/api/api_web/web.ts";

const loading = ref<any>(false);
const result_id = ref<any>("");
const menu_id = ref<any>(null);
const res_form = ref<any>({});
const script_active = ref<any>("all");
const selectedIndex = ref<any>(0);
const script_list = ref<any>([]);
const browser_show = ref<any>([
  { name: "Chrome", value: 1 },
  { name: "Firefox", value: 2 },
  { name: "Edge", value: 3 },
  { name: "Safari", value: 4 }
]);
const browser_list = ref<any>([]);
const browser_active = ref<any>(null);
const web_result_log = ref<any>([]);
const img_show = ref<any>(false);
const pre_img = ref<any>("");
const web_result = ref<any>([]);
const start_time = ref<any>("");
const end_time = ref<any>("");
const run_pass = ref<any>(0);
const run_fail = ref<any>(0);
const run_total = ref<any>(0);
const pre_video = ref<any>("");

const get_result_report = async () => {
  loading.value = true;
  const route = useRoute();
  result_id.value = route.query.result_id;
  const res: any = await get_web_result_report({ result_id: result_id.value });
  res_form.value = res.data;
  script_list.value = res.data.script_list;
  await handle_browser(res.data.browser_list);
  browser_active.value = res.data.browser_list[0];
  menu_id.value = res.data.script_list[0].id;
  await get_result_detail();
  loading.value = false;
};

const get_result_detail = async () => {
  const res: any = await get_web_result_detail({
    result_id: result_id.value,
    browser: browser_active.value,
    menu_id: menu_id.value
  });
  web_result.value = res.data.content;
  web_result_log.value = res.data.log;
  start_time.value = res.data.content[res.data.content.length - 1].create_time;
  end_time.value = res.data.content[0].create_time;
  run_pass.value = res.data.content.filter((item: any) => item.status === 1).length;
  run_fail.value = res.data.content.filter((item: any) => item.status === 0).length;
  run_total.value = run_pass.value + run_fail.value;
  trace.value = res.data.trace;
  pre_video.value = res.data.video;
};

const script_click = async (script: any, index: any) => {
  selectedIndex.value = index;
  menu_id.value = script.id;
  await get_result_detail();
};

const handleTabClick = async (tab: any) => {
  if (tab.props.name === "all") {
    script_list.value = res_form.value.script_list;
  } else if (tab.props.name === "pass") {
    script_list.value = res_form.value.script_list.filter((item: any) => item.status === 1);
  } else if (tab.props.name === "fail") {
    script_list.value = res_form.value.script_list.filter((item: any) => item.status === 0);
  }
};

const handle_browser = async (browsers: any) => {
  browsers.forEach((item: any) => {
    browser_show.value.forEach((browser: any) => {
      if (item === browser.value) {
        browser_list.value.push(browser);
      }
    });
  });
};

const change_browser = async (browser: any) => {
  browser_active.value = browser.props.name;
  await get_result_detail();
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

const get_card_style = (type: any) => {
  if (type === 0) {
    return "border-radius: 10px; border-color: #f3050d; text-align: left;";
  } else {
    return "border-radius: 10px; border-color: #67c23ae0; text-align: left";
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

const view_video = async () => {
  window.open(pre_video.value);
};

const pre_view = async (img: any) => {
    pre_img.value = [img];
    img_show.value = true;
};

const close_img = async () => {
    img_show.value = false;
};

const trace = ref<any>("");
const download_report = async () => {
  window.open(trace.value);
  await view_trace();
};

const view_trace = async () => {
  window.open("https://trace.playwright.dev/");
};

onMounted(() => {
  get_result_report();
});
</script>

<template>
  <div v-loading="loading" style="padding: 10px">
    <div>
      <KoiCard>
        <div style="width: 100%; height: 100%">
          <div style="width: 34%; height: 100%; float: left">
            <KoiCard>
              <div>
                <el-descriptions border column="2">
                  <el-descriptions-item label="任务名称">{{ res_form.task_name }}</el-descriptions-item>
                  <el-descriptions-item label="执行人">{{ res_form.username }}</el-descriptions-item>
                  <el-descriptions-item label="开始时间">{{ res_form.start_time }}</el-descriptions-item>
                  <el-descriptions-item label="结束时间">{{ res_form.end_time }}</el-descriptions-item>
                  <el-descriptions-item label="执行总数">{{ res_form.total }}</el-descriptions-item>
                  <el-descriptions-item label="通过率">
                    <el-tag type="success">{{ res_form.percent + "%" }}</el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </KoiCard>
          </div>
          <div style="width: 65%; height: 100%; float: right">
            <KoiCard>
              <div class="flex flex-wrap gap-4" style="width: 100%; padding-top: 10px; padding-bottom: 7px">
                <el-card style="width: 270px; float: left; padding-right: 10px">
                  脚本总数：<span style="font-size: 26px">{{ res_form.total }}</span>
                </el-card>
                <el-card style="width: 270px; float: left">
                  通过率：<span style="font-size: 26px">{{ res_form.percent + "%" }}</span>
                </el-card>
                <el-card style="width: 270px; float: left">
                  通过数：<span style="font-size: 26px">{{ res_form.total - res_form.total_fail }}</span>
                </el-card>
                <el-card style="width: 270px; float: left">
                  失败数：<span style="font-size: 26px">{{ res_form.total_fail }}</span>
                </el-card>
              </div>
            </KoiCard>
          </div>
        </div>
        <div style="padding-top: 10px">
          <KoiCard>
            <div style="width: 100%; height: 100%">
              <div style="width: 20%; height: 100%; float: left">
                <KoiCard style="height: 710px">
                  <div>
                    <el-tabs v-model="script_active" @tab-click="handleTabClick">
                      <el-tab-pane label="全部" name="all">
                        <div>
                          <div v-for="(script, index) in script_list" :key="index" style="padding-block-end: 10px">
                            <div :style="get_card_style(script.status)" :class="{ highlight: selectedIndex === index }"
                              style="border: 1px solid #e5e5e5">
                              <el-button v-if="script.status === 0"
                                style="padding: 0 !important; color: #f3050d; width: 60%" type="text" icon="CircleClose"
                                circle @click="script_click(script, index)">{{ script.name }}
                              </el-button>
                              <el-button v-if="script.status === 1"
                                style="padding: 0 !important; color: #0bbd87; width: 60%" type="text" icon="CircleCheck"
                                circle @click="script_click(script, index)">{{ script.name }}
                              </el-button>
                            </div>
                          </div>
                        </div>
                      </el-tab-pane>
                      <el-tab-pane label="通过" name="pass">
                        <div>
                          <div v-for="(script, index) in script_list" :key="index" style="padding-block-end: 10px">
                            <div :style="get_card_style(script.status)" :class="{ highlight: selectedIndex === index }"
                              style="border: 1px solid #e5e5e5">
                              <el-button v-if="script.status === 1"
                                style="padding: 0 !important; color: #0bbd87; width: 60%" type="text" icon="CircleCheck"
                                circle @click="script_click(script, index)">
                                {{ script.name }}
                              </el-button>
                            </div>
                          </div>
                        </div>
                      </el-tab-pane>
                      <el-tab-pane label="失败" name="fail">
                        <div>
                          <div v-for="(script, index) in script_list" :key="index" style="padding-block-end: 10px">
                            <div :style="get_card_style(script.status)" :class="{ highlight: selectedIndex === index }"
                              style="border: 1px solid #e5e5e5">
                              <el-button v-if="script.status === 0"
                                style="padding: 0 !important; color: #f3050d; width: 60%" type="text" icon="CircleClose"
                                circle @click="script_click(script, index)">
                                {{ script.name }}
                              </el-button>
                            </div>
                          </div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </KoiCard>
              </div>
              <div style="width: 79%; height: 100%; float: right">
                <KoiCard style="height: 710px">
                  <div>
                    <el-tabs tab-position="left" v-model="browser_active" class="demo-tabs" @tab-click="change_browser">
                      <el-tab-pane v-for="(item, index) in browser_list" :key="index" :name="item.value">
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
                                  <el-descriptions-item label="执行状态："><el-tag
                                      type="danger">执行结束</el-tag></el-descriptions-item>
                                  <el-descriptions-item label="浏览器：">{{ item.name }}</el-descriptions-item>
                                  <el-descriptions-item label="执行人：">{{ res_form.username }}</el-descriptions-item>
                                  <el-descriptions-item label="开始时间：">{{ start_time }}</el-descriptions-item>
                                  <el-descriptions-item label="结束时间：">{{ end_time }}</el-descriptions-item>
                                  <el-descriptions-item label="执行总数：">{{ run_total }}</el-descriptions-item>
                                  <el-descriptions-item label="通过数：">{{ run_pass }}</el-descriptions-item>
                                  <el-descriptions-item label="失败数：">{{ run_fail }}</el-descriptions-item>
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
                                <li v-for="(log, index) in web_result_log" :key="index" :style="get_log_style(log)">{{
                                  log }}</li>
                              </div>
                            </KoiCard>
                          </div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </KoiCard>
              </div>
            </div>
          </KoiCard>
        </div>
      </KoiCard>
    </div>
  </div>
</template>

<style scoped lang="scss">
.el-card__body {
  padding: 5px !important;
}

.highlight {
  background-color: rgba(182, 230, 239, 0.52);
  /* 高亮时的边框颜色 */
}
</style>
