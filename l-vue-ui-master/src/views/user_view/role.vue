<script setup lang="ts">
import {
    add_role, del_role, edit_role, role_list, permission_tree, role_permission, add_permission, edit_permission,
    del_permission, edit_role_permission,
    role_user
} from '@/api/api_user/user';
import { MsgBox, MsgSuccess } from '@/utils/koi';
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
const role = ref([]);
const total = ref(0);
const title = ref("");
const add_koiDialogRef = ref<any>(null);
const edit_koiDialogRef = ref<any>(null);
const permission_koiDialogRef = ref<any>(null);
const tree_data = ref<any>([]);
const tree_checked = ref<any>([]);
const add_form = ref({
    id: null,
    name: ""
});
const defaultProps = {
    children: "children",
    label: "name"
};

const get_role_list = async () => {
    loading.value = true;
    const res: any = await role_list(searchParams.value);
    role.value = res.data.content;
    total.value = res.data.total;
    loading.value = false;
};

const resetsearch = async () => {
    searchParams.value = {
        currentPage: 1, // 第几页
        pageSize: 10, // 每页显示多少条
        search: {
            name__icontains: ""
        }
    };
    await get_role_list();
};

const Add = async () => {
    title.value = "新增角色";
    add_form.value = { id: null, name: "" };
    add_koiDialogRef.value.koiOpen();
};

const Edit = async (row: any) => {
    title.value = "编辑角色"
    add_form.value = row;
    edit_koiDialogRef.value.koiOpen();
};

const add_confirm = async () => {
    const res: any = await add_role(add_form.value);
    if (res.code === 200) {
        add_koiDialogRef.value.koiQuickClose(res.message);
        await get_role_list();
    }
};

const add_cancel = async () => {
    add_koiDialogRef.value.koiQuickClose("已取消")
};

const edit_confirm = async () => {
    const res: any = await edit_role(add_form.value);
    if (res.code === 200) {
        edit_koiDialogRef.value.koiQuickClose(res.message);
        await get_role_list();
    }
};

const edi_cancel = async () => {
    edit_koiDialogRef.value.koiQuickClose("已取消")
};

const Delete = async (row: any) => {
    MsgBox("您确认需要删除角色： " + row.name + " 么？").then(async () => {
        const res: any = await del_role({ id: row.id });
        MsgSuccess(res.message);
        await get_role_list();
    });
};

const get_permission_tree = async (id: any) => {
    const tree_res: any = await permission_tree({ role_id: id });
    tree_data.value = tree_res.data;
};

const get_role_permission = async (id: any) => {
    const res: any = await role_permission({ role_id: id });
    tree_checked.value = res.data;
};

const role_id = ref<any>(null);
const Permission = async (row: any) => {
    title.value = "权限管理：" + row.name;
    permission_koiDialogRef.value.koiOpen();
    role_id.value = row.id;
    tree_data.value = [];
    tree_checked.value = [];
    await get_permission_tree(row.id);
    await get_role_permission(row.id);
};

const permission_check = async (node: any, Nodes: any) => {
    console.log("当前选中的节点：", node);
    // 获取当前选中的节点ID
    const checkedNodes = Nodes.checkedNodes.map((item: any) => item.id);

    // 更新 tree_checked.value 为当前选中的节点ID
    tree_checked.value = checkedNodes;
};

const permission_confirm = async () => {
    const res: any = await edit_role_permission({ role_id: role_id.value, permission: tree_checked.value });
    if (res.code === 200) {
        await get_permission_tree(role_id.value);
        await get_role_permission(role_id.value);
        permission_koiDialogRef.value.koiQuickClose(res.message);
    }
};

const permission_cancel = async () => {
    permission_koiDialogRef.value.koiQuickClose("已取消")
};

const add_per_koiDialogRef = ref<any>(null);
const edit_per_koiDialogRef = ref<any>(null);
const per_form = ref<any>({
    id: null,
    name: "",
    permission: []
});

const permission_id = ref<any>(null);
const pid = ref<any>(null);
const per_type = ref<any>(null);
const add_per = async (data: any, type: any) => {
    title.value = "新增权限";
    pid.value = data.id;
    per_type.value = type;
    per_form.value = {
        name: "",
        id: null,
        url: ""
    }
    add_per_koiDialogRef.value.koiOpen();
};

const del_per = async (data: any) => {
    MsgBox("您确认需要删除权限： " + data.name + " 么？").then(async () => {
        const res: any = await del_permission({ id: data.id });
        MsgSuccess(res.message);
        await get_permission_tree(role_id.value);
    });
};

const edit_per = async (data: any) => {
    title.value = "编辑权限";
    per_form.value = data;
    permission_id.value = data.id;
    edit_per_koiDialogRef.value.koiOpen();
};

const add_per_confirm = async () => {
    per_form.value.pid = pid.value;
    per_form.value.type = per_type.value;
    const res: any = await add_permission(per_form.value);
    if (res.code === 200) {
        await get_permission_tree(role_id.value)
        add_per_koiDialogRef.value.koiQuickClose(res.message);
    }
};

const edit_per_confirm = async () => {
    const res: any = await edit_permission(per_form.value);
    if (res.code === 200) {
        await get_permission_tree(role_id.value)
        edit_per_koiDialogRef.value.koiQuickClose(res.message);
    }
};

const add_per_cancel = async () => {
    add_per_koiDialogRef.value.koiQuickClose("已取消")
};

const edit_per_cancel = async () => {
    edit_per_koiDialogRef.value.koiQuickClose("已取消")
};

const role_user_list = ref<any>([]);
const get_role_user = async (id: any) => {
    role_user_list.value = [];
    const res: any = await role_user({ role_id: id });
    role_user_list.value = res.data;
};

onMounted(() => {
    get_role_list();
});

</script>

<template>
    <div stye="padding: 10px">
        <KoiCard>
            <div v-loading="loading">
                <el-form :inline="true">
                    <el-form-item label="角色名称" prop="userName">
                        <el-input placeholder="请输入名称" v-model="searchParams.search.name__icontains" clearable
                            style="width: 200px"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" icon="search" plain v-debounce="get_role_list">搜索</el-button>
                        <el-button type="danger" icon="refresh" plain v-throttle="resetsearch">重置</el-button>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="success" icon="Plus" plain @click="Add">新增角色</el-button>
                    </el-form-item>
                </el-form>
                <div>
                    <el-table :data="role" border stripe style="width: 100%" :loading="loading">
                        <el-table-column prop="id" label="ID"></el-table-column>
                        <el-table-column prop="name" label="角色"></el-table-column>
                        <el-table-column prop="username" label="创建人"></el-table-column>
                        <el-table-column prop="create_time" label="创建时间"></el-table-column>
                        <el-table-column prop="update_time" label="更新时间"></el-table-column>
                        <el-table-column label="操作" width="400">
                            <template #default="scope">
                                <el-popover placement="top-start" title="用户列表":hight="300" :width="100" trigger="click">
                                    <div style="overflow-y: auto; max-height: 270px"><p v-for="(user, index) in role_user_list" :key="index" class="text item">{{ user.username }}</p></div>
                                    <template #reference>
                                        <el-button type="warning" size="small" plain
                                        @click="get_role_user(scope.row.id)">查看角色用户</el-button>
                                    </template>
                                </el-popover>
                                <el-button type="primary" size="small" plain @click="Edit(scope.row)">编辑</el-button>
                                <el-button type="success" size="small" plain
                                    @click="Permission(scope.row)">权限管理</el-button>
                                <el-button type="danger" size="small" plain @click="Delete(scope.row)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
                <div class="h-10px"></div>
                <el-pagination background v-model:current-page="searchParams.currentPage"
                    v-model:page-size="searchParams.pageSize" v-show="total > 0" :page-sizes="[10, 20, 50]"
                    layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="get_role_list"
                    @current-change="get_role_list" />
            </div>
            <div>
                <KoiDialog v-loading="loading" ref="add_koiDialogRef" :title="title" @koi-confirm="add_confirm"
                    @koi-cancel="add_cancel" :height="50" width="20%">
                    <template #content>
                        <div>
                            <el-form :model="add_form" label-width="100px">
                                <el-form-item label="角色名称">
                                    <el-input v-model="add_form.name" style="width: 85%;"
                                        placeholder="请输入角色名称"></el-input>
                                </el-form-item>
                            </el-form>
                        </div>
                    </template>
                </koiDialog>
            </div>
            <div>
                <KoiDialog v-loading="loading" ref="edit_koiDialogRef" :title="title" @koi-confirm="edit_confirm"
                    @koi-cancel="edi_cancel" :height="100" width="20%">
                    <template #content>
                        <div>
                            <el-form :model="add_form" label-width="100px">
                                <el-form-item label="角色id">
                                    <el-input v-model="add_form.id" disabled style="width: 85%;"
                                        placeholder="请输入角色名称"></el-input>
                                </el-form-item>
                                <el-form-item label="角色名称">
                                    <el-input v-model="add_form.name" style="width: 85%;"
                                        placeholder="请输入角色名称"></el-input>
                                </el-form-item>
                            </el-form>
                        </div>
                    </template>
                </koiDialog>
            </div>
            <div>
                <KoiDialog v-loading="loading" ref="permission_koiDialogRef" :title="title"
                    @koi-confirm="permission_confirm" @koi-cancel="permission_cancel" :height="500" width="45%">
                    <template #content>
                        <div style="height: 100%; overflow-y: auto;">
                            <el-tree :data="tree_data" show-checkbox node-key="id" :default-expanded-keys="[2, 3]"
                                :default-checked-keys="tree_checked" :props="defaultProps" @check="permission_check">
                                <template #default="{ node, data }">
                                    <span v-if="data.type === 2">{{ node.label + '（' + data.url + '）' }}</span>
                                    <span v-if="data.type !== 2">{{ node.label }}</span>
                                    <div style="float: right;">
                                        <el-button v-if="data.type === 0" type="text" icon="CirclePlus"
                                            @click="add_per(data, 1)">新增</el-button>
                                        <el-button v-if="data.type === 1" type="text" icon="CirclePlus"
                                            @click="add_per(data, 2)">新增</el-button>
                                        <el-button v-if="data.type !== 0" type="text" icon="Edit"
                                            @click="edit_per(data)">编辑</el-button>
                                        <el-button v-if="data.type === 2" style="margin-left: 4px" icon="Delete"
                                            type="danger" link @click="del_per(data)"></el-button>
                                    </div>
                                </template>
                            </el-tree>
                        </div>
                    </template>
                </koiDialog>
            </div>
            <div>
                <KoiDialog v-loading="loading" ref="add_per_koiDialogRef" :title="title" @koi-confirm="add_per_confirm"
                    @koi-cancel="add_per_cancel" :height="100" width="25%">
                    <template #content>
                        <div>
                            <el-form :model="per_form" label-width="100px">
                                <el-form-item label="权限名称：">
                                    <el-input v-model="per_form.name" style="width: 85%;"
                                        placeholder="请输入权限名称"></el-input>
                                </el-form-item>
                                <el-form-item label="权限地址：">
                                    <el-input v-model="per_form.url" style="width: 85%;"
                                        placeholder="请输入权限地址"></el-input>
                                </el-form-item>
                            </el-form>
                        </div>
                    </template>
                </koiDialog>
            </div>
            <div>
                <KoiDialog v-loading="loading" ref="edit_per_koiDialogRef" :title="title"
                    @koi-confirm="edit_per_confirm" @koi-cancel="edit_per_cancel" :height="100" width="25%">
                    <template #content>
                        <div>
                            <el-form :model="per_form" label-width="100px">
                                <el-form-item label="权限名称：">
                                    <el-input v-model="per_form.name" style="width: 85%;"
                                        placeholder="请输入权限名称"></el-input>
                                </el-form-item>
                                <el-form-item label="权限地址：">
                                    <el-input v-model="per_form.url" style="width: 85%;"
                                        placeholder="请输入权限地址"></el-input>
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
