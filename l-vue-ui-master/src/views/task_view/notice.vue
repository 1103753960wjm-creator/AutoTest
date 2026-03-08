<script setup lang="ts">
import {
    notice_list, add_notice, del_notice, edit_notice
} from '@/api/api_task/task.ts';
import { user_select } from "@/api/api_user/user.ts"
import { MsgBox, MsgError, MsgSuccess } from '@/utils/koi';
import { onMounted, ref } from 'vue';

// 查询参数
const searchParams = ref({
    currentPage: 1, // 第几页
    pageSize: 10, // 每页显示多少条
    search: {
        name__icontains: ""
    }
});
const loading = ref(true);
const total = ref<any>(0);
const add_form = ref<any>({});
const table_data = ref<any>([]);
const add_koiDialogRef = ref<any>(null);
const edit_koiDialogRef = ref<any>(null);
const title = ref<string>("");
const user_list = ref<any>([]);

const get_notice_list = async () => {
    const res: any = await notice_list(searchParams.value);
    table_data.value = res.data.content;
    loading.value = false;
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
    await get_notice_list();
};

const get_user_list = async () => {
    const res: any = await user_select({});
    user_list.value = res.data;
};

const Add = async () => {
    title.value = "新增通知信息";
    add_form.value = {
        name: "",
        type: 1,
        script: {
            wechat: {
                msgtype: "text",
                news: {
                    articles: [
                        {
                            title: "",
                            description: "",
                            url: "",
                            picurl: ""
                        }
                    ]
                },
                content: "",
                mentioned_list: [],
                dingding: {},
                email: {}
            },
        },
        value: "",
        status: 1
    }
    add_koiDialogRef.value.koiOpen();
};

const Edit = async (row: any) => {
    title.value = "编辑通知信息"
    add_form.value = row;
    edit_koiDialogRef.value.koiOpen();
};

const add_confirm = async () => {
    const res: any = await add_notice(add_form.value);
    if (res.code === 200) {
        add_koiDialogRef.value.koiQuickClose(res.message);
        await get_notice_list();
    }
};

const add_cancel = async () => {
    add_koiDialogRef.value.koiQuickClose("已取消")
};

const edit_confirm = async () => {
    const res: any = await edit_notice(add_form.value);
    if (res.code === 200) {
        edit_koiDialogRef.value.koiQuickClose(res.message);
        await get_notice_list();
    }
};

const edi_cancel = async () => {
    edit_koiDialogRef.value.koiQuickClose("已取消")
};

const Delete = async (row: any) => {
    MsgBox("您确认需要删除： " + row.name + " 么？").then(async () => {
        const res: any = await del_notice({ id: row.id });
        MsgSuccess(res.message);
        await get_notice_list();
    });
};

const Add_news = async (data: any) => {
    data.push(
        {
            title: "",
            description: "",
            url: "",
            picurl: ""
        }
    )
};

const Del_news = async (index: number) => {
    const data: any = add_form.value.script.wechat.news.articles;
    if (data.length <= 1) {
        MsgError("请至少保留一条数据");
        return;
    } else {
        data.splice(index, 1);
    }
};

onMounted(() => {
    get_notice_list();
    get_user_list();
});

</script>

<template>
    <div stye="padding: 10px">
        <KoiCard>
            <div v-loading="loading">
                <el-form :inline="true">
                    <el-form-item label="通知名称" prop="userName">
                        <el-input placeholder="请输入通知名称" v-model="searchParams.search.name__icontains" clearable
                            style="width: 200px"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" icon="search" plain v-debounce="get_notice_list">搜索</el-button>
                        <el-button type="danger" icon="refresh" plain v-throttle="resetsearch">重置</el-button>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="success" icon="Plus" plain @click="Add">新增通知配置</el-button>
                    </el-form-item>
                </el-form>
                <div>
                    <el-table :data="table_data" border stripe style="width: 100%" :loading="loading">
                        <el-table-column prop="id" label="ID" width="100"></el-table-column>
                        <el-table-column prop="name" label="通知名称" :show-overflow-tooltip="true"></el-table-column>
                        <el-table-column label="通知类型" width="150">
                            <template #default="scope">
                                <el-tag type="primary" v-if="scope.row.type == 1">企微机器人</el-tag>
                                <el-tag type="warning" v-if="scope.row.type == 2">钉钉机器人</el-tag>
                                <el-tag type="error" v-if="scope.row.type == 3">邮件</el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="消息类型" width="150">
                            <template #default="scope">
                                <div v-if="scope.row.type == 1">
                                    <el-tag type="success" v-if="scope.row.script.wechat.msgtype == 'text'">纯文本</el-tag>
                                    <el-tag type="primary"
                                        v-if="scope.row.script.wechat.msgtype == 'markdown'">markdown</el-tag>
                                    <el-tag type="warning" v-if="scope.row.script.wechat.msgtype == 'news'">图文</el-tag>
                                </div>
                            </template>
                        </el-table-column>
                        <el-table-column label="状态" width="100">
                            <template #default="scope">
                                <el-tag type="success" v-if="scope.row.status == 1">启用</el-tag>
                                <el-tag type="info" v-if="scope.row.status == 0">禁用</el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column prop="username" label="创建人"></el-table-column>
                        <el-table-column prop="create_time" label="创建时间"></el-table-column>
                        <el-table-column prop="update_time" label="更新时间"></el-table-column>
                        <el-table-column label="操作">
                            <template #default="scope">
                                <el-button type="primary" size="small" plain @click="Edit(scope.row)">编辑</el-button>
                                <el-button type="danger" size="small" plain @click="Delete(scope.row)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                    <div class="h-10px"></div>
                    <el-pagination background v-model:current-page="searchParams.currentPage"
                        v-model:page-size="searchParams.pageSize" v-show="total > 0" :page-sizes="[10, 20, 50]"
                        layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="get_notice_list"
                        @current-change="get_notice_list" />
                </div>
            </div>
            <div>
                <KoiDialog v-loading="loading" ref="add_koiDialogRef" :title="title" @koi-confirm="add_confirm"
                    @koi-cancel="add_cancel" :height="500" width="50%">
                    <template #content>
                        <div>
                            <el-form :model="add_form" label-width="100px">
                                <el-form-item label="通知对象：">
                                    <el-radio-group v-model="add_form.type">
                                        <el-radio :value="1">企微机器人</el-radio>
                                        <!-- <el-radio :value="2">钉钉机器人</el-radio>
                                        <el-radio :value="3">邮箱</el-radio> -->
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item label="通知名称：">
                                    <el-input v-model="add_form.name" style="width: 85%;"
                                        placeholder="请输入角色名称"></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type !== 3" label="通知地址：">
                                    <el-input v-model="add_form.value" style="width: 85%;"
                                        placeholder="请输入通知地址"></el-input>
                                </el-form-item>
                                <el-form-item label="通知描述：">
                                    <el-input v-model="add_form.description" style="width: 85%;"
                                        placeholder="请输入通知描述："></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="邮件发起人：">
                                    <el-input v-model="add_form.script.email_from" style="width: 85%;"
                                        placeholder="请输入邮件发起人："></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="客户端密码：">
                                    <el-input v-model="add_form.script.email_password" style="width: 85%;"
                                        placeholder="请输入客户端密码："></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="邮件接收人：">
                                    <el-select v-model="add_form.script.email_to" multiple style="width: 85%;"
                                        placeholder="请输入邮件接收人：">
                                        <el-option v-for="(item, index) in user_list" :key="index" :label="item.name"
                                            :value="item.email"> </el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item label="是否启用：">
                                    <el-switch v-model="add_form.status" :active-value="1" :inactive-value="0"
                                        active-color="#13ce66" inactive-color="#ff4949" active-text="启用"
                                        inactive-text="禁用"></el-switch>
                                </el-form-item>
                                <el-form-item label="通知类型：">
                                    <el-radio-group v-model="add_form.script.wechat.msgtype">
                                        <el-radio value="text">纯文本</el-radio>
                                        <el-radio value="markdown">markdown</el-radio>
                                        <el-radio value="news">图文</el-radio>
                                        <el-button v-if="add_form.script.wechat.msgtype == 'news'" type="text"
                                            @click="Add_news(add_form.script.wechat.news.articles)">添加多个图文配置</el-button>
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item
                                    v-if="add_form.script.wechat.msgtype === 'text' || add_form.script.wechat.msgtype === 'markdown'"
                                    label="通知内容：">
                                    <textarea style="width: 97%;" v-model="add_form.script.wechat.content"
                                        placeholder="请输入内容" rows="5"></textarea>
                                </el-form-item>
                                <el-form-item v-if="add_form.script.wechat.msgtype === 'news'">
                                    <div v-for="(item, index) in add_form.script.wechat.news.articles"
                                        style="border: 0.5px solid #e4e7ed; padding: 5px; border-radius: 5px">
                                        <div>
                                            <el-form :model="item" inline>
                                                <el-form-item label="图文标题：">
                                                    <el-input style="width: 260px;" v-model="item.title"
                                                        placeholder="请输入标题"></el-input>
                                                </el-form-item>
                                                <el-form-item label="图文描述：">
                                                    <el-input style="width: 260px;" v-model="item.description"
                                                        placeholder="请输入描述"></el-input>
                                                </el-form-item>
                                                <el-form-item label="图片地址：">
                                                    <el-input style="width: 260px;" v-model="item.picurl"
                                                        placeholder="请输入图片地址"></el-input>
                                                </el-form-item>
                                                <el-form-item label="跳转地址：">
                                                    <el-input style="width: 260px;" v-model="item.url"
                                                        placeholder="请输入跳转地址"></el-input>
                                                </el-form-item>
                                                <el-form-item>
                                                    <el-button type="danger" plain
                                                        @click="Del_news(index)">删除</el-button>
                                                </el-form-item>
                                            </el-form>
                                        </div>
                                    </div>
                                </el-form-item>
                                <el-form-item label="@成员：">
                                    <el-select v-model="add_form.script.wechat.mentioned_list" multiple filterable
                                        placeholder="请选择成员">
                                        <el-option v-for="item in user_list" :key="item.id" :label="item.name"
                                            :value="item.account"></el-option>
                                    </el-select>
                                </el-form-item>
                            </el-form>
                        </div>
                    </template>
                </koiDialog>
            </div>
            <div>
                <KoiDialog v-loading="loading" ref="edit_koiDialogRef" :title="title" @koi-confirm="edit_confirm"
                    @koi-cancel="edi_cancel" :height="500" width="40%">
                    <template #content>
                        <div>
                            <el-form :model="add_form" label-width="100px">
                                <el-form-item label="通知类型：">
                                    <el-radio-group v-model="add_form.type">
                                        <el-radio :value="1">企微机器人</el-radio>
                                        <!-- <el-radio :value="2">钉钉机器人</el-radio>
                                        <el-radio :value="3">邮箱</el-radio> -->
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item label="通知名称：">
                                    <el-input v-model="add_form.name" style="width: 85%;"
                                        placeholder="请输入角色名称"></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type !== 3" label="通知地址：">
                                    <el-input v-model="add_form.value" style="width: 85%;"
                                        placeholder="请输入通知地址"></el-input>
                                </el-form-item>
                                <el-form-item label="通知描述：">
                                    <el-input v-model="add_form.description" style="width: 85%;"
                                        placeholder="请输入通知描述："></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="邮件发起人：">
                                    <el-input v-model="add_form.script.email_from" style="width: 85%;"
                                        placeholder="请输入邮件发起人："></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="客户端密码：">
                                    <el-input v-model="add_form.script.email_password" style="width: 85%;"
                                        placeholder="请输入客户端密码："></el-input>
                                </el-form-item>
                                <el-form-item v-if="add_form.type === 3" label="邮件接收人：">
                                    <el-select v-model="add_form.script.email_to" multiple style="width: 85%;"
                                        placeholder="请输入邮件接收人：">
                                        <el-option v-for="(item, index) in user_list" :key="index" :label="item.name"
                                            :value="item.email"> </el-option>
                                    </el-select>
                                </el-form-item>
                                <el-form-item label="是否启用：">
                                    <el-switch v-model="add_form.status" :active-value="1" :inactive-value="0"
                                        active-color="#13ce66" inactive-color="#ff4949" active-text="启用"
                                        inactive-text="禁用"></el-switch>
                                </el-form-item>
                                <el-form-item label="通知类型：">
                                    <el-radio-group v-model="add_form.script.wechat.msgtype">
                                        <el-radio value="text">纯文本</el-radio>
                                        <el-radio value="markdown">markdown</el-radio>
                                        <el-radio value="news">图文</el-radio>
                                        <el-button v-if="add_form.script.wechat.msgtype == 'news'" type="text"
                                            @click="Add_news(add_form.script.wechat.news.articles)">添加多个图文配置</el-button>
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item
                                    v-if="add_form.script.wechat.msgtype === 'text' || add_form.script.wechat.msgtype === 'markdown'"
                                    label="通知内容：">
                                    <textarea style="width: 97%;" v-model="add_form.script.wechat.content"
                                        placeholder="请输入内容" rows="5"></textarea>
                                </el-form-item>
                                <el-form-item v-if="add_form.script.wechat.msgtype === 'news'">
                                    <div v-for="(item, index) in add_form.script.wechat.news.articles"
                                        style="border: 0.5px solid #e4e7ed; padding: 5px; border-radius: 5px">
                                        <div>
                                            <el-form :model="item" inline>
                                                <el-form-item label="图文标题：">
                                                    <el-input style="width: 260px;" v-model="item.title"
                                                        placeholder="请输入标题"></el-input>
                                                </el-form-item>
                                                <el-form-item label="图文描述：">
                                                    <el-input style="width: 260px;" v-model="item.description"
                                                        placeholder="请输入描述"></el-input>
                                                </el-form-item>
                                                <el-form-item label="图片地址：">
                                                    <el-input style="width: 260px;" v-model="item.picurl"
                                                        placeholder="请输入图片地址"></el-input>
                                                </el-form-item>
                                                <el-form-item label="跳转地址：">
                                                    <el-input style="width: 260px;" v-model="item.url"
                                                        placeholder="请输入跳转地址"></el-input>
                                                </el-form-item>
                                                <el-form-item>
                                                    <el-button type="danger" plain
                                                        @click="Del_news(index)">删除</el-button>
                                                </el-form-item>
                                            </el-form>
                                        </div>
                                    </div>
                                </el-form-item>
                                <el-form-item label="@成员：">
                                    <el-select v-model="add_form.script.wechat.mentioned_list" multiple filterable
                                        placeholder="请选择成员">
                                        <el-option v-for="item in user_list" :key="item.id" :label="item.name"
                                            :value="item.account"></el-option>
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

<style scoped lang="scss"></style>
