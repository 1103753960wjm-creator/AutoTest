<script setup lang="ts">
import {
    add_web_group, del_web_group, group_add_script, web_group_list,
    web_menu, edit_web_group, get_web_result_log, get_web_result,
    run_web_script
} from "@/api/api_web/web";
import { MsgBox, MsgError, MsgSuccess } from "@/utils/koi";
import { ref, onMounted } from "vue";
import { LocalStorage } from "@/utils/storage.ts";


const searchParams = ref({
    search: {
        name__icontains: "",
    },
    currentPage: 1,
    pageSize: 10,
});
const table_data = ref<any>([]);
const total = ref(0);

const reset_search = () => {
    searchParams.value = {
        search: {
            name__icontains: "",
        },
        currentPage: 1,
        pageSize: 10,
    };
};

const group_list = async () => {
    const res: any = await web_group_list(searchParams.value);
    table_data.value = res.data.content;
    total.value = res.data.total;
};

const element_select_list = ref<any>([]);
const web_list = ref<any>("");
const element_select = async () => {
    const res: any = await web_menu({});
    element_select_list.value = res.data;
};

const add_web = async () => {
    const res: any = await group_add_script({
        "web_list": web_list.value
    })
    add_form.value.script = [...add_form.value.script, ...res.data]
    web_list.value = []
};

const del_web = async (data: any) => {
    add_form.value.script = add_form.value.script.filter((item: any) => item.id !== data.id);
};

const add_koiDialogRef = ref();
const add_form = ref<any>({
    name: "",
    script: []
});
const defaultProps = {
    children: "children",
    label: "name"
};
const title = ref<any>("");
const Add = async () => {
    await element_select();
    title.value = "新增测试场景";
    add_koiDialogRef.value.koiOpen();
};

const add_confirm = async () => {
    const res: any = await add_web_group(add_form.value);
    await group_list();
    add_koiDialogRef.value.koiQuickClose(res.message);
};

const add_cancel = () => {
    add_koiDialogRef.value.koiClose();
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

const edit_koiDialogRef = ref();
const Edit = async (row: any) => {
    title.value = "编辑测试场景：" + row.name;
    add_form.value = row;
    edit_koiDialogRef.value.koiOpen();
    await element_select();
};

const edit_confirm = async () => {
    const res: any = await edit_web_group(add_form.value);
    await group_list();
    edit_koiDialogRef.value.koiQuickClose(res.message);
};

const edit_cancel = () => {
    edit_koiDialogRef.value.koiClose();
};

const Delete = async (row: any) => {
    MsgBox("您确认需要删除： " + row.name + " 么？").then(async () => {
        const res: any = await del_web_group({ id: row.id });
        MsgSuccess(res.message);
        await group_list();
    });
};

const run_koiDialogRef = ref();
const run_script_form = ref<any>({
    task_name: "",
    browser: [],
    script: [],
    width: 1920,
    height: 1080,
    browser_type: 1
});
const browser_list = ref<any>([
    { name: "Chrome", value: 1 },
    { name: "Firefox", value: 2 },
    { name: "Edge", value: 3 },
    { name: "Safari", value: 4 }
]);
const run_browsers = ref<any>([]);
const run_browser_active = ref<any>("");
const res_koiDialogRef = ref();
const result_id = ref<any>("");
const run_script = async (row: any) => {
    title.value = "请配置调试信息";
    run_script_form.value.script = row.script;
    run_koiDialogRef.value.koiOpen();
};

const run_script_confirm = async () => {
    if (run_script_form.value.script.length === 0) {
        MsgError("请选择脚本");
        return;
    }
    run_browsers.value = [];
    result_id.value = String(Date.now());
    run_script_form.value.result_id = result_id.value;
    await run_browser_show();
    run_browser_active.value = run_script_form.value.browser[0];
    title.value = "正在执行：" + run_script_form.value.task_name;
    res_koiDialogRef.value.koiOpen();
    await startPolling();
    await run_web_script(run_script_form.value);
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
    await startPolling();
};

const run_script_cancel = async () => {
    run_koiDialogRef.value.koiQuickClose("取消调试");
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
    const fail = 0;
    web_result.value.forEach((item: any) => {
        if (item.status == 0) {
            run_fail.value = fail + 1;
        }
        if (item.name == "执行结束") {
            stopPolling();
            run_type.value = "执行结束";
            end_time.value = item.create_time;
            pre_video.value = item.video;
            trace.value = item.trace
        }
    });
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
    group_list();
});
</script>

<template>
    <div style="padding: 10px;">
        <koiCard>
            <div>
                <el-form inline>
                    <el-form-item label="任务名称：" prop="userName">
                        <el-input placeholder="请输入任务名称" v-model="searchParams.search.name__icontains" clearable
                            style="width: 300px"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" icon="search" plain v-debounce="group_list">搜索</el-button>
                        <el-button type="danger" icon="refresh" plain v-throttle="reset_search">重置</el-button>
                        <el-button type="success" icon="plus" plain @click="Add()">新增测试场景</el-button>
                    </el-form-item>
                </el-form>
                <div class="h-10px"></div>
                <el-table :data="table_data" stripe border style="width: 100%">
                    <el-table-column prop="id" label="ID"></el-table-column>
                    <el-table-column prop="name" label="名称"></el-table-column>
                    <el-table-column label="用例集">
                        <template #default="{ row }">
                            <el-popover placement="top" :width="300" trigger="hover">
                                <div>
                                    <el-steps direction="vertical" :active="99">
                                        <el-step v-for="step in row.script" :key="step.id" :title="step.name"></el-step>
                                    </el-steps>
                                </div>
                                <template #reference>
                                    <el-button type="text">用例详情</el-button>
                                </template>
                            </el-popover>
                        </template>
                    </el-table-column>
                    <el-table-column prop="description" label="描述" :show-overflow-tooltip="true"></el-table-column>
                    <el-table-column prop="username" label="最后更新人"></el-table-column>
                    <el-table-column prop="create_time" label="创建时间"></el-table-column>
                    <el-table-column prop="update_time" label="更新时间"></el-table-column>
                    <el-table-column label="操作" align="center" width="300">
                        <template #default="scope">
                            <el-button type="success" size="small" plain @click="run_script(scope.row)">立即运行</el-button>
                            <el-button type="primary" size="small" plain @click="Edit(scope.row)">编辑</el-button>
                            <el-button type="danger" size="small" plain @click="Delete(scope.row)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
                <div class="h-10px"></div>
                <el-pagination background v-model:current-page="searchParams.currentPage"
                    v-model:page-size="searchParams.pageSize" v-show="total > 0" :page-sizes="[10, 20, 50]"
                    layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="group_list"
                    @current-change="group_list" />
            </div>
            <div>
                <KoiDialog ref="add_koiDialogRef" :title="title" @koi-confirm="add_confirm" @koi-cancel="add_cancel"
                    :height="620">
                    <template #content>
                        <el-form ref="formRef" :model="add_form" label-width="80px" status-icon>
                            <el-form-item label="名称：" prop="roleName">
                                <el-input v-model="add_form.name" placeholder="请输入名称" clearable />
                            </el-form-item>
                            <el-form-item label="用例集：" prop="roleName">
                                <el-cascader v-model="web_list" placeholder="请选择元素"
                                    style="width: 400px; padding-right: 10px;" :options="element_select_list" filterable
                                    collapse-tags
                                    :props="{ value: 'id', label: 'name', children: 'children', multiple: true }">
                                    <template #default="{ node, data }">
                                        <el-icon v-if="data.type === 0" style="padding-right: 5px;">
                                            <HomeFilled />
                                        </el-icon>
                                        <el-icon v-if="data.type === 1" style="padding-right: 5px;">
                                            <Folder />
                                        </el-icon>
                                        <el-icon v-if="data.type === 2" style="padding-right: 5px;">
                                            <ChromeFilled />
                                        </el-icon>
                                        <span>{{ data.name }}</span>
                                        <span v-if="!node.isLeaf">({{ data.children.length }})</span>
                                    </template>
                                </el-cascader>
                                <el-button type="primary" icon="plus" plain @click="add_web">确认添加</el-button>
                            </el-form-item>
                            <el-form-item>
                                <div
                                    style="border: 1px solid #e4e7ed; width: 400px; height: 400px; overflow-y: auto; padding: 10px;">
                                    <el-tree ref="treeRef" :data="add_form.script" :props="defaultProps"
                                        default-expand-all :allow-drop="on_menu_allowDrop" draggable>
                                        <template #default="{ node, data }">
                                            <span class="custom-tree-node" style="width: 100%;">
                                                <div
                                                    style="border: 1px solid #3e7be5; border-radius: 5px; width: 93%; color: #3e7be5">
                                                    <span>
                                                        <el-icon style="padding-right: 3px; padding-left: 5px;">
                                                            <ChromeFilled />
                                                        </el-icon>
                                                        {{ node.label }}
                                                        <el-button type="text" style="float: right;" plain icon="Delete"
                                                            @click="del_web(data)"></el-button>
                                                    </span>
                                                </div>
                                            </span>
                                        </template>
                                    </el-tree>
                                </div>
                            </el-form-item>
                            <el-form-item label="描述：">
                                <el-input v-model="add_form.description" placeholder="请输入描述" />
                            </el-form-item>
                        </el-form>
                    </template>
                </KoiDialog>
            </div>
            <div>
                <KoiDialog ref="edit_koiDialogRef" :title="title" @koi-confirm="edit_confirm" @koi-cancel="edit_cancel"
                    :height="620">
                    <template #content>
                        <el-form ref="formRef" :model="add_form" label-width="80px" status-icon>
                            <el-form-item label="名称：" prop="roleName">
                                <el-input v-model="add_form.name" placeholder="请输入名称" clearable />
                            </el-form-item>
                            <el-form-item label="用例集：" prop="roleName">
                                <el-cascader v-model="web_list" placeholder="请选择元素"
                                    style="width: 400px; padding-right: 10px;" :options="element_select_list" filterable
                                    collapse-tags
                                    :props="{ value: 'id', label: 'name', children: 'children', multiple: true }">
                                    <template #default="{ node, data }">
                                        <el-icon v-if="data.type === 0" style="padding-right: 5px;">
                                            <HomeFilled />
                                        </el-icon>
                                        <el-icon v-if="data.type === 1" style="padding-right: 5px;">
                                            <Folder />
                                        </el-icon>
                                        <el-icon v-if="data.type === 2" style="padding-right: 5px;">
                                            <ChromeFilled />
                                        </el-icon>
                                        <span>{{ data.name }}</span>
                                        <span v-if="!node.isLeaf">({{ data.children.length }})</span>
                                    </template>
                                </el-cascader>
                                <el-button type="primary" icon="plus" plain @click="add_web">确认添加</el-button>
                            </el-form-item>
                            <el-form-item>
                                <div
                                    style="border: 1px solid #e4e7ed; width: 400px; height: 400px; overflow-y: auto; padding: 10px;">
                                    <el-tree ref="treeRef" :data="add_form.script" :props="defaultProps"
                                        default-expand-all :allow-drop="on_menu_allowDrop" draggable>
                                        <template #default="{ node, data }">
                                            <span class="custom-tree-node" style="width: 100%;">
                                                <div
                                                    style="border: 1px solid #3e7be5; border-radius: 5px; width: 93%; color: #3e7be5">
                                                    <span>
                                                        <el-icon style="padding-right: 3px; padding-left: 5px;">
                                                            <ChromeFilled />
                                                        </el-icon>
                                                        {{ node.label }}
                                                        <el-button type="text" style="float: right;" plain icon="Delete"
                                                            @click="del_web(data)"></el-button>
                                                    </span>
                                                </div>
                                            </span>
                                        </template>
                                    </el-tree>
                                </div>
                            </el-form-item>
                            <el-form-item label="描述：">
                                <el-input v-model="add_form.description" placeholder="请输入描述" />
                            </el-form-item>
                        </el-form>
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
                                        <el-input-number v-model="run_script_form.width" controls-position="right"
                                            min="800" label="宽度">
                                        </el-input-number>
                                        <el-input-number v-model="run_script_form.height" style="padding-left: 10px;"
                                            controls-position="right" min="800" label="高度">
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
                        <div style="width: 100%">
                            <el-tabs tab-position="left" v-model="run_browser_active" class="demo-tabs"
                                @tab-click="change_browser">
                                <el-tab-pane v-for="(item, index) in run_browsers" :key="index" :name="item.value">
                                    <template #label>
                                        <div v-show="item.value === 1" class="tab-info">
                                            <img src="@/assets/icons/google.png" />
                                            <span slot="code" class="code" style="padding-left: 5px">{{ item.name
                                            }}</span>
                                        </div>
                                        <div v-show="item.value === 2" class="tab-info">
                                            <img src="@/assets/icons/firefox.png" />
                                            <span slot="code" class="code" style="padding-left: 5px">{{ item.name
                                            }}</span>
                                        </div>
                                        <div v-show="item.value === 3" class="tab-info">
                                            <img src="@/assets/icons/Edge.png" />
                                            <span slot="code" class="code" style="padding-left: 5px">{{ item.name
                                            }}</span>
                                        </div>
                                        <div v-show="item.value === 4" class="tab-info">
                                            <img src="@/assets/icons/ios.png" />
                                            <span slot="code" class="code" style="padding-left: 5px">{{ item.name
                                            }}</span>
                                        </div>
                                    </template>
                                    <div style="width: 100%">
                                        <div style="width: 100%; padding-block-end: 10px">
                                            <KoiCard style="height: 80px">
                                                <div>
                                                    <el-descriptions :column="5">
                                                        <el-descriptions-item label="执行状态：">
                                                            <el-tag type="success" v-if="run_type == '正在执行'">{{ run_type
                                                            }}</el-tag>
                                                            <el-tag type="danger" v-if="run_type == '执行结束'">{{ run_type
                                                            }}</el-tag>
                                                        </el-descriptions-item>
                                                        <el-descriptions-item label="浏览器：">{{ item.name
                                                        }}</el-descriptions-item>
                                                        <el-descriptions-item label="执行人：">{{ user.username
                                                        }}</el-descriptions-item>
                                                        <el-descriptions-item label="开始时间：">{{ start_time
                                                        }}</el-descriptions-item>
                                                        <el-descriptions-item label="结束时间：">{{ end_time
                                                        }}</el-descriptions-item>
                                                        <el-descriptions-item label="已执行：">{{ run_count - 1
                                                        }}</el-descriptions-item>
                                                        <el-descriptions-item label="通过：">{{ run_count - run_fail - 1
                                                        }}</el-descriptions-item>
                                                        <el-descriptions-item label="失败：">{{ run_fail
                                                        }}</el-descriptions-item>
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
                                                        <el-timeline-item center v-for="(res, index) in web_result"
                                                            :key="index" :icon="getIcon(res.status)" type="primary"
                                                            :color="colors(res.status)" size="large"
                                                            :timestamp="'执行时间：' + res.create_time" placement="top">
                                                            <KoiCard :style="get_colors(res.status)">
                                                                <span>{{ res.name }}</span>
                                                                <span>{{ "结果：" + res.log }}</span>
                                                                <span>
                                                                    <el-popover placement="right" :width="500"
                                                                        trigger="click">
                                                                        <template #reference>
                                                                            <el-button
                                                                                v-if="Object.keys(res.assert_result).length !== 0"
                                                                                icon="Search" type="text"
                                                                                style="float: right">
                                                                                断言详情
                                                                            </el-button>
                                                                        </template>
                                                                        <div v-for="(item, index) in res.assert_result"
                                                                            :key="index">
                                                                            <span :style="get_log_style(item.result)">{{
                                                                                "断言结果：" + item.result
                                                                            }}</span>
                                                                            <el-button icon="Picture" type="text"
                                                                                style="float: right"
                                                                                @click="pre_view(item.img)">
                                                                                查看详情
                                                                            </el-button>
                                                                        </div>
                                                                    </el-popover>
                                                                    <el-button v-if="res.before_img !== ''"
                                                                        icon="Picture" type="text"
                                                                        @click="pre_view(res.before_img)">
                                                                        执行前
                                                                    </el-button>
                                                                    <el-button v-if="res.after_img !== ''"
                                                                        icon="Picture" type="text"
                                                                        @click="pre_view(res.after_img)">
                                                                        执行后
                                                                    </el-button>
                                                                </span>
                                                                <div class="img-viewer-box">
                                                                    <el-image-viewer v-if="img_show" :url-list="pre_img"
                                                                        @close="close_img" />
                                                                </div>
                                                            </KoiCard>
                                                        </el-timeline-item>
                                                    </el-timeline>
                                                </div>
                                            </KoiCard>
                                            <KoiCard style="width: 66%; float: right; height: 560px; overflow-y: auto">
                                                <div>
                                                    <li v-if="run_type !== '执行结束'"
                                                        style="margin-bottom: 7px; color: #0bbd87">执行日志获取中...</li>
                                                    <li v-for="(log, index) in web_result_log" :key="index"
                                                        :style="get_log_style(log)">{{ log
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