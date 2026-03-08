<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from "vue-router";
import { get_api_script_report_log, get_api_script_result_detail, get_api_script_result_detail_list, get_api_script_result_report_list, api_env, api_db_list, api_tree_list } from "@/api/api_api/api";
import Api_detail from "./api_detail.vue";

const result_id = ref<any>('');
const result_form = ref<any>({
    result: {
        percent: 0,
        pass: 0,
        fail: 0
    }
});
const loading = ref<any>(false);
const script_active = ref<any>('all');
const script_list = ref<any>([]);
const menu_id = ref<any>('');
const selectedIndex = ref<any>(0);
const script_result_list = ref<any>([]);
const res_script_result = ref<any>({});
const get_script_result = async () => {
    loading.value = true;
    const route = useRoute();
    result_id.value = route.query.result_id;
    const res: any = await get_api_script_result_detail({
        result_id: result_id.value
    });
    result_form.value = res.data;
    menu_id.value = res.data.script[0].uuid;
    script_list.value = res.data.script;
    res_script_result.value = res.data.script;
    name.value = res.data.script[0].name;
    run_env.value = env_list.value.find((item: any) => item.id === res.data.config.env_id)?.name;
    await get_script_result_detail_list();
    await get_script_result_report_list();
    await get_script_log();
    loading.value = false;
};

const env_list = ref<any>([]);
const get_env_list = async () => {
  const res: any = await api_env({});
  env_list.value = res.data;
};
const get_script_result_detail_list = async () => {
    const res: any = await get_api_script_result_detail_list({
        "menu_id": menu_id.value,
        "result_id": result_id.value
    });
    script_result_list.value = res.data;
};

const tree_list = ref<any>([]);
const get_api_tree_list = async () => {
  const res: any = await api_tree_list({});
  tree_list.value = res.data;
};

const handleTabClick = (tab: any) => {
    if (tab.props.name === "all") {
        script_list.value = res_script_result.value;
    } else if (tab.props.name === "pass") {
        script_list.value = res_script_result.value.filter((item: any) => item.status === 1);
    } else if (tab.props.name === "fail") {
        script_list.value = res_script_result.value.filter((item: any) => item.status === 0);
    }
};
const script_click = async (script: any, index: any) => {
    selectedIndex.value = index;
    menu_id.value = script.uuid;
    name.value = script.name;
    await get_script_result_detail_list();
    await get_script_result_report_list();
    await get_script_log();
};

const run_result_list = ref<any>([]);
const run_count = ref<any>(0);
const run_fail = ref<any>(0);
const start_time = ref<any>("");
const end_time = ref<any>("");
const run_env = ref<any>("");
const name = ref<any>("");
const get_script_result_report_list = async () => {
  const res: any = await get_api_script_result_report_list({
    result_id: result_id.value,
    menu_id: menu_id.value
  });
  run_result_list.value = res.data;
  run_count.value = run_result_list.value.length;
  if (run_result_list.value.length > 0) {
    start_time.value = start_time.value = run_result_list.value[run_result_list.value.length - 1].create_time;
  }
  end_time.value = run_result_list.value[0].create_time;
  run_fail.value = 0
  run_result_list.value.forEach((item: any) => {
    if (item.status == 0) {
      run_fail.value = run_fail.value + 1;
    }
  });
};
const run_result_log = ref<any>([]);
const get_script_log = async () => {
  const res: any = await get_api_script_report_log({
    result_id: result_id.value,
    menu_id: menu_id.value
  });
  run_result_log.value = res.data;
};
const detail_koiDrawerRef = ref();
const detail = ref<any>({});
const local_db_list = ref<any>([]);
const get_db_list = async () => {
  const res: any = await api_db_list({});
  local_db_list.value = res.data.content;
};
const view_result = async (api: any) => {
  //   await get_redis_example();
  await get_db_list();
  detail.value = api;
  detail_koiDrawerRef.value.koiOpen();
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

onMounted(() => {
    get_script_result();
    get_env_list();
    get_api_tree_list();
});
</script>

<template>
    <div style="padding: 10px" v-loading="loading" element-loading-text="加载中...">
        <koiCard>
            <div>
                <div style="width: 100%; padding-left: 10px;">
                    <div style="width: 33%; float: left;">
                        <koiCard style="height: 180px;">
                            <div>
                                <el-descriptions border :column="1" size="mini">
                                    <el-descriptions-item label="任务名称">{{ result_form.name }}</el-descriptions-item>
                                    <el-descriptions-item label="执行人">{{ result_form.username }}</el-descriptions-item>
                                    <el-descriptions-item label="开始时间">{{ result_form.start_time
                                        }}</el-descriptions-item>
                                    <el-descriptions-item label="结束时间">{{ result_form.end_time }}</el-descriptions-item>
                                </el-descriptions>
                            </div>
                        </koiCard>
                    </div>
                    <div style="width: 33%; float: left; height: 190px;">
                        <koiCard>
                            <div style="display: flex; justify-content: center">
                                <el-card style="width: 270px" shadow="never">
                                    接口总数：
                                    <span style="font-size: 26px">{{ result_form.result.total }}</span>
                                </el-card>
                                <el-card style="width: 270px" shadow="never">
                                    通过率：
                                    <span style="font-size: 26px">{{ result_form.result.percent + '%' }}</span>
                                </el-card>
                            </div>
                            <div style="display: flex; justify-content: center; padding-top: 10px">
                                <el-card style="width: 270px" shadow="never">
                                    通过数：
                                    <span style="font-size: 26px">{{ result_form.result.pass }}</span>
                                </el-card>
                                <el-card style="width: 270px" shadow="never">
                                    失败数：
                                    <span style="font-size: 26px">{{ result_form.result.fail }}</span>
                                </el-card>
                            </div>
                        </koiCard>
                    </div>
                    <div style="width: 33%; float: left;">
                        <koiCard style="height: 180px;">
                            <div style="justify-content: center; padding-left: 34%">
                                <el-progress type="dashboard" :percentage="result_form.result.percent" status="success">
                                    <template #default="{ percentage }">
                                        <span class="percentage-value">{{ percentage }}%</span>
                                        <span class="percentage-label">通过率</span>
                                    </template>
                                </el-progress>
                            </div>
                        </koiCard>
                    </div>
                </div>
                <div style="padding-left: 10px; width: 99%;">
                    <koiCard>
                        <div style="width: 100%;">
                            <div style="width: 20%; float: left;">
                                <koiCard style="height: 670px; overflow: auto;">
                                    <el-tabs v-model="script_active" @tab-click="handleTabClick">
                                        <el-tab-pane label="全部" name="all">
                                            <div>
                                                <div v-for="(script, index) in script_list" :key="index"
                                                    style="padding-block-end: 10px">
                                                    <div :style="get_card_style(script.status)"
                                                        :class="{ highlight: script.uuid === menu_id }"
                                                        style="border: 1px solid #e5e5e5">
                                                        <el-button v-if="script.status === 0"
                                                            style="padding: 0 !important; color: #f3050d; padding-left: 10px"
                                                            type="text" icon="CircleClose" plain
                                                            @click="script_click(script, index)">
                                                            {{ script.name + '(通过数' + script.pass + '，失败数' + script.fail
                                                            + ')' }}
                                                        </el-button>
                                                        <el-button v-if="script.status === 1"
                                                            style="padding: 0 !important; color: #0bbd87; padding-left: 10px"
                                                            type="text" icon="CircleCheck" plain
                                                            @click="script_click(script, index)">
                                                            {{ script.name + '(通过数' + script.pass + '，失败数' + script.fail
                                                            + ')' }}
                                                        </el-button>
                                                    </div>
                                                </div>
                                            </div>
                                        </el-tab-pane>
                                        <el-tab-pane label="通过" name="pass">
                                            <div>
                                                <div v-for="(script, index) in script_list" :key="index"
                                                    style="padding-block-end: 10px">
                                                    <div :style="get_card_style(script.status)"
                                                        :class="{ highlight: script.uuid === menu_id }"
                                                        style="border: 1px solid #e5e5e5">
                                                        <el-button v-if="script.status === 1"
                                                            style="padding: 0 !important; color: #0bbd87"
                                                            type="text" icon="CircleCheck" plain
                                                            @click="script_click(script, index)">
                                                            {{ script.name + '(通过数' + script.pass + '，失败数' + script.fail
                                                            + ')' }}
                                                        </el-button>
                                                    </div>
                                                </div>
                                            </div>
                                        </el-tab-pane>
                                        <el-tab-pane label="失败" name="fail">
                                            <div>
                                                <div v-for="(script, index) in script_list" :key="index"
                                                    style="padding-block-end: 10px">
                                                    <div :style="get_card_style(script.status)"
                                                        :class="{ highlight: script.uuid === menu_id }"
                                                        style="border: 1px solid #e5e5e5">
                                                        <el-button v-if="script.status === 0"
                                                            style="padding: 0 !important; color: #f3050d"
                                                            type="text" icon="CircleClose" plain
                                                            @click="script_click(script, index)">
                                                            {{ script.name + '(通过数' + script.pass + '，失败数' + script.fail
                                                            + ')' }}
                                                        </el-button>
                                                    </div>
                                                </div>
                                            </div>
                                        </el-tab-pane>
                                    </el-tabs>
                                </koiCard>
                            </div>
                            <div style="width: 80%; float: left">
                                <koiCard style="height: 670px; overflow: auto;">
                                    <div style="width: 100%">
                                        <div>
                                            <KoiCard>
                                                <div>
                                                    <el-descriptions column="4">
                                                        <el-descriptions-item label="任务名称：">{{ name
                                                            }}</el-descriptions-item>
                                                        <el-descriptions-item label="开始时间：">{{ start_time
                                                            }}</el-descriptions-item>
                                                        <el-descriptions-item label="结束时间：">{{ end_time
                                                            }}</el-descriptions-item>
                                                        <el-descriptions-item label="执行环境：">{{ run_env
                                                            }}</el-descriptions-item>
                                                        <el-descriptions-item label="执行总数：">{{ run_count
                                                            }}</el-descriptions-item>
                                                        <el-descriptions-item label="通过数：">{{ run_count - run_fail
                                                            }}</el-descriptions-item>
                                                        <el-descriptions-item label="失败数：">{{ run_fail
                                                            }}</el-descriptions-item>
                                                    </el-descriptions>
                                                </div>
                                            </KoiCard>
                                        </div>
                                        <div style="padding-top: 5px">
                                            <KoiCard style="height: 560px">
                                                <div style="width: 100%">
                                                    <div>
                                                        <KoiCard
                                                            style="width: 30%; float: left; height: 530px; overflow: auto">
                                                            <el-timeline style="width: 80%">
                                                                <el-timeline-item center
                                                                    v-for="(res, index) in run_result_list" :key="index"
                                                                    :icon="getIcon(res.status)" type="primary"
                                                                    :color="colors(res.status)" size="large"
                                                                    :timestamp="'执行时间：' + res.create_time"
                                                                    placement="top">
                                                                    <KoiCard :style="get_colors(res.status)">
                                                                        <span v-if="res.name !== '执行结束'">{{ "接口：" +
                                                                            res.name }}</span>
                                                                        <span v-if="res.name === '执行结束'">{{ res.name
                                                                            }}</span>
                                                                        <span v-if="res.name !== '执行结束'">
                                                                            <span style="padding-right: 10px">{{ "code："
                                                                                + res.res.code
                                                                                }}</span>
                                                                            <span style="padding-right: 10px">{{ "size："
                                                                                + res.res.size
                                                                                }}B</span>
                                                                            <span>{{ "time：" + res.res.res_time
                                                                                }}ms</span>
                                                                        </span>
                                                                        <span v-if="res.name !== '执行结束'">
                                                                            <div>
                                                                                <el-button icon="View" type="text"
                                                                                    style="float: right"
                                                                                    @click="view_result(res)">
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
                                                        <KoiCard
                                                            style="width: 66%; float: left; height: 530px; overflow: auto">
                                                            <div>
                                                                <li v-for="(log, index) in run_result_log" :key="index"
                                                                    :style="get_log_style(log)">{{ log }}</li>
                                                            </div>
                                                        </KoiCard>
                                                    </div>
                                                </div>
                                            </KoiCard>
                                        </div>
                                    </div>
                                </koiCard>
                            </div>
                        </div>
                    </koiCard>
                </div>
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
                :local_db_list="local_db_list"
                :redis_example_list="['common']"
              />
            </div>
          </template>
        </KoiDrawer>
      </div>
        </koiCard>
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