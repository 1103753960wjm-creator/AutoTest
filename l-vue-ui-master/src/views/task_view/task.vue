<script setup lang="ts">
import { task_list, del_task, notice_select, add_task, edit_task } from "@/api/api_task/task";
import { get_device_list } from "@/api/api_app/device.ts";
import { get_app_script_list } from "@/api/api_app/app.ts";
import { web_group_select } from "@/api/api_web/web.ts";
import { MsgSuccess, MsgBox } from "@/utils/koi";
import { ref, onMounted } from "vue";
import { api_env, params_select, get_api_script_list } from "@/api/api_api/api";

const searchParams = ref({
    search: {
        name__icontains: "",
    },
    currentPage: 1, // 第几页
    pageSize: 10, // 每页显示多少条
});
const table_data = ref<any>([]);
const total = ref<any>(0);
const get_task_list = async () => {
    console.log(searchParams.value);
    const res: any = await task_list(searchParams.value);
    table_data.value = res.data.content;
    total.value = res.data.total;
};
const resetsearch = async () => {
    searchParams.value = {
        currentPage: 1, // 第几页
        pageSize: 10, // 每页显示多少条
        search: {
            name__icontains: ""
        }
    };
    await get_task_list();
};

const add_koiDialogRef = ref<any>(null);
const edit_koiDialogRef = ref<any>(null);
const title = ref<any>("");
const device_list = ref<any>([]);
const app_script_list = ref<any>([]);
const web_script_list = ref<any>([]);
const api_script_list = ref<any>([]);
const loading = ref<any>(false);
const notice_list = ref<any>([]);
const week_list = ref<any>([
    { name: "周一", value: "mon" }, { name: "周二", value: "tue" }, { name: "周三", value: "wed" },
    { name: "周四", value: "thu" }, { name: "周五", value: "fri" }, { name: "周六", value: "sat" }, { name: "周日", value: "sun" }
]);
const browser_list = ref<any>([
    { name: "Chrome", value: 1 },
    { name: "Firefox", value: 2 },
    { name: "Edge", value: 3 },
    { name: "Safari", value: 4 }
]);
const env_list = ref<any>([]);
const params_list = ref<any>([]);

const get_params = async () => {
    const res: any = await params_select({});
    params_list.value = res.data;
};
const get_env_list = async () => {
    const res: any = await api_env({});
    env_list.value = res.data;
};

const get_api_script = async () => {
    const res: any = await get_api_script_list({});
    api_script_list.value = res.data;
};

const get_notice = async () => {
    const res: any = await notice_select({});
    notice_list.value = res.data;
};

const get_device = async () => {
    const res: any = await get_device_list({});
    device_list.value = res.data;
};

const app_script_list_get = async () => {
    const res: any = await get_app_script_list({});
    app_script_list.value = res.data;
};

const web_script_list_get = async () => {
    const res: any = await web_group_select({});
    web_script_list.value = res.data.content;
};

const add_form = ref<any>({
    name: "",
    type: 1,
    status: 1,
    script: {
        width: 1920,
        height: 1080,
        device: [],
        app_script_list: [],
        web_script_list: [],
        api_script_list: [],
        browser: [],
        env_id: null,
        params_id: null,
    },
    time: {
        type: 1,
        run_time: "",
        interval: 1,
        week_date: [],
        week_run_time: ""
    },
    notice: {
        status: 1,
        notice_id: "",
    }
})
const Add = async () => {
    loading.value = true;
    await get_notice();
    await get_device();
    await get_env_list();
    await get_params();
    await get_api_script();
    await app_script_list_get();
    await web_script_list_get();
    title.value = "新增定时任务"
    add_koiDialogRef.value.koiOpen();
    loading.value = false;
};

const Edit = async (row: any) => {
    loading.value = true;
    await get_notice();
    await get_device();
    await get_env_list();
    await get_params();
    await get_api_script();
    await app_script_list_get();
    await web_script_list_get();
    add_form.value = row;
    title.value = "编辑定时任务"
    edit_koiDialogRef.value.koiOpen();
    loading.value = false;
};

const Delete = async (row: any) => {
    MsgBox("您确认需要删除： " + row.name + " 么？").then(async () => {
        const res: any = await del_task({ id: row.id });
        MsgSuccess(res.message);
        await get_task_list();
    });
};

const handle_device = async (device: any) => {
    const res: any = [];
    device.forEach((item1: any) => {
        device_list.value.forEach((item2: any) => {
            if (item1 === item2.deviceid) {
                res.push(item2);
            }
        });
    });
    return res;
};

const add_confirm = async () => {
    const device = await handle_device(add_form.value.script.device);
    add_form.value.script.device_list = device;
    const res: any = await add_task(add_form.value);
    if (res.code === 200) {
        add_koiDialogRef.value.koiQuickClose(res.message);
        await get_task_list();
    }
};

const add_cancel = async () => {
    add_koiDialogRef.value.koiQuickClose("已取消")
};

const edit_confirm = async () => {
    const device = await handle_device(add_form.value.script.device);
    add_form.value.script.device_list = device;
    const res: any = await edit_task(add_form.value);
    if (res.code === 200) {
        edit_koiDialogRef.value.koiQuickClose(res.message);
        await get_task_list();
    }
};

const edit_cancel = async () => {
    edit_koiDialogRef.value.koiQuickClose("已取消")
};

onMounted(() => {
    get_task_list();
});
</script>

<template>
    <div style="padding: 10px;">
        <KoiCard style="height: 800px;">
            <div>
                <el-form :inline="true">
                    <el-form-item label="名称" prop="userName">
                        <el-input placeholder="请输入名称" v-model="searchParams.search.name__icontains" clearable
                            style="width: 200px"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" icon="search" plain v-debounce="get_task_list">搜索</el-button>
                        <el-button type="danger" icon="refresh" plain v-throttle="resetsearch">重置</el-button>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="success" icon="Plus" plain @click="Add">新增任务</el-button>
                    </el-form-item>
                </el-form>
                <div class="h-10px"></div>
                <el-table :data="table_data" border stripe>
                    <el-table-column prop="name" label="任务名称" align="center"></el-table-column>
                    <el-table-column label="任务类型" align="center">
                        <template #default="scope">
                            <el-tag v-if="scope.row.type == 1" type="success">APP自动化</el-tag>
                            <el-tag v-if="scope.row.type == 2" type="warning">WEB自动化</el-tag>
                            <el-tag v-if="scope.row.type == 3" type="warning">API自动化</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="status" label="任务状态" align="center">
                        <template #default="scope">
                            <el-switch v-model="scope.row.status" active-text="启用" inactive-text="停用" :active-value="1"
                                :inactive-value="0" :inline-prompt="true" disabled>
                            </el-switch>
                        </template>
                    </el-table-column>
                    <el-table-column label="执行类型" align="center">
                        <template #default="scope">
                            <el-tag v-if="scope.row.time.type == 1" type="success">执行一次</el-tag>
                            <el-tag v-if="scope.row.time.type == 2" type="warning">间隔执行</el-tag>
                            <el-tag v-if="scope.row.time.type == 3" type="danger">每天执行</el-tag>
                            <el-tag v-if="scope.row.time.type == 4" type="warning">每周执行</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="next_time" label="下一次执行时间" align="center">
                        <template #default="scope">
                            <el-tag v-if="scope.row.next_time !== ''" type="primary">{{ scope.row.next_time }}</el-tag>
                            <el-tag v-if="scope.row.next_time === ''" type="info">-</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="username" label="最后更新人" align="center"></el-table-column>
                    <el-table-column prop="create_time" label="创建时间" align="center"></el-table-column>
                    <el-table-column prop="update_time" label="更新时间" align="center"></el-table-column>
                    <el-table-column label="操作" align="center">
                        <template #default="scope">
                            <el-button type="primary" size="small" plain @click="Edit(scope.row)">编辑</el-button>
                            <el-button type="danger" size="small" plain @click="Delete(scope.row)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
                <div class="h-10px"></div>
                <el-pagination background v-model:current-page="searchParams.currentPage"
                    v-model:page-size="searchParams.pageSize" v-show="total > 0" :page-sizes="[10, 20, 50]"
                    layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="get_task_list"
                    @current-change="get_task_list" />
            </div>
            <div v-loading="loading" element-loading-text="配置加载中...">
                <KoiDialog ref="add_koiDialogRef" :title="title" @koi-confirm="add_confirm" @koi-cancel="add_cancel"
                    :height="500" width="40%">
                    <template #content>
                        <div>
                            <el-form :model="add_form" label-width="100px">
                                <el-form-item label="任务类型：">
                                    <el-radio-group v-model="add_form.type" placeholder="请选择任务类型">
                                        <el-radio label="APP自动化" :value="1"></el-radio>
                                        <el-radio label="WEB自动化" :value="2"></el-radio>
                                        <el-radio label="API自动化" :value="3"></el-radio>
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item label="任务名称：">
                                    <el-input v-model="add_form.name" style="width: 85%;"
                                        placeholder="请输入任务名称"></el-input>
                                </el-form-item>
                                <el-form-item label="任务状态：">
                                    <el-switch v-model="add_form.status" :active-value="1" :inactive-value="0"
                                        active-text="开启" inactive-text="关闭"></el-switch>
                                </el-form-item>
                                <el-form-item label="任务描述：">
                                    <el-input v-model="add_form.description" style="width: 85%;"
                                        placeholder="请输入任务描述"></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 1" label="设备列表：">
                                    <el-select style="width: 85%" v-model="add_form.script.device" multiple
                                        placeholder="请选择设备">
                                        <el-option v-for="(item, index) in device_list" :key="index" :label="item.name"
                                            :value="item.deviceid"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 2" label="浏览器列表：">
                                    <el-select style="width: 85%" v-model="add_form.script.browser" multiple
                                        placeholder="请选择浏览器">
                                        <el-option v-for="(item, index) in browser_list" :key="index" :label="item.name"
                                            :value="item.value"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 2" label="分辨率(高*宽)：">
                                    <div>
                                        <el-input-number v-model="add_form.script.height" controls-position="right"
                                            min="800" label="高度">
                                        </el-input-number>
                                        <el-input-number v-model="add_form.script.width" style="padding-left: 10px;"
                                            controls-position="right" min="800" label="宽度">
                                        </el-input-number>
                                    </div>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 1" label="测试用例：">
                                    <el-select style="width: 85%" v-model="add_form.script.app_script_list" multiple
                                        placeholder="请选择测试用例">
                                        <el-option v-for="(item, index) in app_script_list" :key="index"
                                            :label="item.name" :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 2" label="测试用例：">
                                    <el-select style="width: 85%" v-model="add_form.script.web_script_list" multiple
                                        placeholder="请选择测试用例">
                                        <el-option v-for="(item, index) in web_script_list" :key="index"
                                            :label="item.name" :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="测试用例：">
                                    <el-select style="width: 85%" v-model="add_form.script.api_script_list" multiple
                                        placeholder="请选择测试用例">
                                        <el-option v-for="(item, index) in api_script_list" :key="index"
                                            :label="item.name" :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="执行环境：">
                                    <el-select style="width: 85%" v-model="add_form.script.env_id" placeholder="请选择环境">
                                        <el-option v-for="(item, index) in env_list" :key="index" :label="item.name"
                                            :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item label="执行类型：">
                                    <el-radio-group v-model="add_form.time.type" placeholder="请选择任务类型">
                                        <el-radio label="执行一次" :value="1"></el-radio>
                                        <el-radio label="间隔执行" :value="2"></el-radio>
                                        <el-radio label="每天执行" :value="3"></el-radio>
                                        <el-radio label="每周执行" :value="4"></el-radio>
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item v-if="add_form.time.type === 1" label="执行时间：">
                                    <el-date-picker v-model="add_form.time.run_time" value-format="yyyy-MM-dd HH:mm:ss"
                                        type="datetime" placeholder="请选择执行的时间" />
                                </el-form-item>
                                <el-form-item v-if="add_form.time.type === 2" label="间隔(分钟)：">
                                    <el-input-number v-model="add_form.time.interval" :min="1" :max="3600" />
                                </el-form-item>
                                <el-form-item v-if="add_form.time.type === 3" label="执行时间：">
                                    <el-time-select v-model="add_form.time.week_run_time" style="width: 240px"
                                        start="08:30" step="00:15" end="18:30" placeholder="请选择执行的时间" />
                                </el-form-item>
                                <el-form-item v-if="add_form.time.type === 4" label="执行时间：">
                                    <el-select v-model="add_form.time.week_date" style="width: 30%; padding-right: 10px"
                                        collapse-tags multiple placeholder="请选择测试用例">
                                        <el-option v-for="(item, index) in week_list" :key="index" :label="item.name"
                                            :value="item.value"></el-option>
                                    </el-select>
                                    <el-time-select v-model="add_form.time.week_run_time" style="width: 240px"
                                        start="08:30" step="00:15" end="18:30" placeholder="请选择执行的时间" />
                                </el-form-item>
                                <el-form-item label="结果通知：">
                                    <el-switch v-model="add_form.notice.status" :active-value="1" :inactive-value="0"
                                        active-text="开启" inactive-text="关闭"></el-switch>
                                </el-form-item>
                                <el-form-item label="通知配置：" v-if="add_form.notice.status === 1">
                                    <el-select style="width: 85%" v-model="add_form.notice.notice_id"
                                        placeholder="请选择通知配置">
                                        <el-option v-for="(item, index) in notice_list" :key="index" :label="item.name"
                                            :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                            </el-form>
                        </div>
                    </template>
                </koiDialog>
            </div>
            <div v-loading="loading" element-loading-text="配置加载中...">
                <KoiDialog ref="edit_koiDialogRef" :title="title" @koi-confirm="edit_confirm" @koi-cancel="edit_cancel"
                    :height="500" width="40%">
                    <template #content>
                        <div>
                            <el-form :model="add_form" label-width="100px">
                                <el-form-item label="任务类型：">
                                    <el-radio-group v-model="add_form.type" placeholder="请选择任务类型">
                                        <el-radio label="APP自动化" :value="1"></el-radio>
                                        <el-radio label="WEB自动化" :value="2"></el-radio>
                                        <el-radio label="API自动化" :value="3"></el-radio>
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item label="任务名称：">
                                    <el-input v-model="add_form.name" style="width: 85%;"
                                        placeholder="请输入任务名称"></el-input>
                                </el-form-item>
                                <el-form-item label="任务状态：">
                                    <el-switch v-model="add_form.status" :active-value="1" :inactive-value="0"
                                        active-text="开启" inactive-text="关闭"></el-switch>
                                </el-form-item>
                                <el-form-item label="任务描述：">
                                    <el-input v-model="add_form.description" style="width: 85%;"
                                        placeholder="请输入任务描述"></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 1" label="设备列表：">
                                    <el-select style="width: 85%" v-model="add_form.script.device" multiple
                                        placeholder="请选择设备">
                                        <el-option v-for="(item, index) in device_list" :key="index" :label="item.name"
                                            :value="item.deviceid"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 2" label="浏览器列表：">
                                    <el-select style="width: 85%" v-model="add_form.script.browser" multiple
                                        placeholder="请选择浏览器">
                                        <el-option v-for="(item, index) in browser_list" :key="index" :label="item.name"
                                            :value="item.value"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 2" label="分辨率(高*宽)：">
                                    <div>
                                        <el-input-number v-model="add_form.script.height" controls-position="right"
                                            min="800" label="高度">
                                        </el-input-number>
                                        <el-input-number v-model="add_form.script.width" style="padding-left: 10px;"
                                            controls-position="right" min="800" label="宽度">
                                        </el-input-number>
                                    </div>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 1" label="测试用例：">
                                    <el-select style="width: 85%" v-model="add_form.script.app_script_list" multiple
                                        placeholder="请选择测试用例">
                                        <el-option v-for="(item, index) in app_script_list" :key="index"
                                            :label="item.name" :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 2" label="测试用例：">
                                    <el-select style="width: 85%" v-model="add_form.script.web_script_list" multiple
                                        placeholder="请选择测试用例">
                                        <el-option v-for="(item, index) in web_script_list" :key="index"
                                            :label="item.name" :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="测试用例：">
                                    <el-select style="width: 85%" clearable v-model="add_form.script.api_script_list"
                                        multiple placeholder="请选择测试用例">
                                        <el-option v-for="(item, index) in api_script_list" :key="index"
                                            :label="item.name" :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="执行环境：">
                                    <el-select style="width: 85%" clearable v-model="add_form.script.env_id"
                                        placeholder="请选择环境">
                                        <el-option v-for="(item, index) in env_list" :key="index" :label="item.name"
                                            :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item label="执行类型：">
                                    <el-radio-group v-model="add_form.time.type" placeholder="请选择任务类型">
                                        <el-radio label="执行一次" :value="1"></el-radio>
                                        <el-radio label="间隔执行" :value="2"></el-radio>
                                        <el-radio label="每天执行" :value="3"></el-radio>
                                        <el-radio label="每周执行" :value="4"></el-radio>
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item v-if="add_form.time.type === 1" label="执行时间：">
                                    <el-date-picker v-model="add_form.time.run_time" type="datetime"
                                        placeholder="请选择执行的时间" />
                                </el-form-item>
                                <el-form-item v-if="add_form.time.type === 2" label="间隔(分钟)：">
                                    <el-input-number v-model="add_form.time.interval" :min="1" :max="3600" />
                                </el-form-item>
                                <el-form-item v-if="add_form.time.type === 3" label="执行时间：">
                                    <el-time-select v-model="add_form.time.week_run_time" style="width: 240px"
                                        start="08:30" step="00:15" end="18:30" placeholder="请选择执行的时间" />
                                </el-form-item>
                                <el-form-item v-if="add_form.time.type === 4" label="执行时间：">
                                    <el-select style="width: 30%; padding-right: 10px" collapse-tags
                                        v-model="add_form.time.week_date" multiple placeholder="请选择测试用例">
                                        <el-option v-for="(item, index) in week_list" :key="index" :label="item.name"
                                            :value="item.value"></el-option>
                                    </el-select>
                                    <el-time-select v-model="add_form.time.week_run_time" style="width: 240px"
                                        start="08:30" step="00:15" end="18:30" placeholder="请选择执行的时间" />
                                </el-form-item>
                                <el-form-item label="结果通知：">
                                    <el-switch v-model="add_form.notice.status" :active-value="1" :inactive-value="0"
                                        active-text="开启" inactive-text="关闭"></el-switch>
                                </el-form-item>
                                <el-form-item label="通知配置：" v-if="add_form.notice.status === 1">
                                    <el-select style="width: 85%" v-model="add_form.notice.notice_id"
                                        placeholder="请选择通知配置">
                                        <el-option v-for="(item, index) in notice_list" :key="index" :label="item.name"
                                            :value="item.id"></el-option>
                                    </el-select>
                                </el-form-item>
                            </el-form>
                        </div>
                    </template>
                </koiDialog>
            </div>
        </KoiCard>
    </div>
</template>

<style lang="scss" scoped></style>