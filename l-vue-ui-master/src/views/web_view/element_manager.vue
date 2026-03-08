<script setup lang="ts">
import { add_element, add_menu, del_element, del_menu, edit_element, edit_menu, element_tree, get_element_list } from '@/api/api_web/element.ts';
import { MsgBox, MsgSuccess } from '@/utils/koi';
import { ref, onMounted } from 'vue'

const treeData = ref<any>([]);
const defaultProps = ref({
    children: 'children',
    label: "name"
});
const filterText = ref<any>('');
const title = ref<any>('');
const add_koiDialogRef = ref();
const edit_koiDialogRef = ref();
const add_menu_form = ref<any>({});

const get_tree = async () => {
    const res: any = await element_tree({});
    treeData.value = res.data;
};

const Add_menu = async (data: any) => {
    add_menu_form.value = {
        pid: data.id,
        name: "",
        type: 1
    }
    title.value = "新建菜单";
    add_koiDialogRef.value.koiOpen();
};

const add_menu_confirm = async () => {
    const res: any = await add_menu(add_menu_form.value)
    add_koiDialogRef.value.koiQuickClose(res.message);
    await get_tree();
};

const add_menu_cancel = async () => {
    add_koiDialogRef.value.koiClose();
};
const Edit_menu = async (data: any) => {
    add_menu_form.value = {
        id: data.id,
        name: data.name,
        type: 1
    }
    title.value = "重命名";
    edit_koiDialogRef.value.koiOpen();
};

const edit_menu_confirm = async () => {
    const res: any = await edit_menu(add_menu_form.value)
    edit_koiDialogRef.value.koiQuickClose(res.message);
    await get_tree();
};

const edit_menu_cancel = async () => {
    edit_koiDialogRef.value.koiClose();
};

const Del_menu = async (data: any) => {
    MsgBox("您确认需要删除菜单： " + data.name + " 么？").then(async () => {
        const res: any = await del_menu({ id: data.id });
        MsgSuccess(res.message);
        await get_tree();
    });
};

const searchParams = ref<any>({
    currentPage: 1, // 第几页
    pageSize: 10, // 每页显示多少条
    search: {
        menu_id: null,
        name__icontains: ""
    }
});
const tab_list = ref<any>([]);
const tab_active = ref<any>("");
const get_element = async (data: any) => {
    if (data.type === 1) {
        searchParams.value.search.menu_id = data.id;
        const res: any = await get_element_list(searchParams.value);
        await addTab(data, searchParams.value, res.data)
    }
};

const addTab = async (node: any, searchParams: any, element: any) => {
    const newTabName = node.name;
    const index = tab_list.value.findIndex((item: any) => item.title === newTabName);
    const tab = {
        title: newTabName,
        name: newTabName,
        content: element,
        id: node.id,
        type: node.type,
        searchParams: searchParams
    }
    if (index === -1) {
        tab_list.value.push(tab);
    }
    refresh_tab.value = tab;
    tab_active.value = node.name;
};

const tab_click = async (targetName: any) => {
    let tab_name = targetName.props.name;
    tab_list.value.forEach((tab: any) => {
        if (tab.name === tab_name) {
            refresh_tab.value = tab;
            refresh_tab.value.searchParams.search.menu_id = tab.id;
        }
    });
    await element_list();
};

const removeTab = async (targetName: any) => {
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
}

const element_list = async () => {
    const res: any = await get_element_list(refresh_tab.value.searchParams);
    refresh_tab.value.content = res.data;
};

const add_element_dialogRef = ref();
const add_element_form = ref<any>({});
const edit_element_dialogRef = ref();
const element_type_list = ref<any>([
    { name: "网页", value: 1 },
    { name: "元素", value: 2 }
]);
const browser_list = ref<any>([
    { name: "标题", value: 1 },
    { name: "网址", value: 2 }
]);
const locator_list = ref<any>([
    { name: "定位器", value: 3 },
    { name: "选择器", value: 4 },
    { name: "自定义", value: 5 }
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
    { label: "tree", value: "tree" },
    { label: "treeitem", value: "treeitem" }
]);
const refresh_tab = ref<any>({})
const Add_element = async (tab: any, menu_id: any) => {
    refresh_tab.value = tab;
    add_element_form.value = {
        menu_id: menu_id,
        name: "",
        element: {
            type: 1,
            browser: 1,
            locator_type: 1,
            locator_select_type: 1,
            value: '',
            locator_role_type: 1,
        },
    }
    title.value = "新建元素";
    add_element_dialogRef.value.koiOpen();
};

const Edit_element = async (tab: any, data: any) => {
    refresh_tab.value = tab;
    add_element_form.value = data;
    title.value = "编辑元素：" + data.name;
    edit_element_dialogRef.value.koiOpen();
};

const add_element_confirm = async () => {
    const res: any = await add_element(add_element_form.value);
    add_element_dialogRef.value.koiQuickClose(res.message);
    await element_list();
};
const edit_element_confirm = async () => {
    const res: any = await edit_element(add_element_form.value);
    edit_element_dialogRef.value.koiQuickClose(res.message);
    await element_list();
};

const add_element_cancel = () => {
    add_element_dialogRef.value.koiClose();
};

const edit_element_cancel = () => {
    edit_element_dialogRef.value.koiClose();
};

const Del_element = async (tab: any, data: any) => {
    refresh_tab.value = tab;
    MsgBox("您确认需要删除元素： " + data.name + " 么？").then(async () => {
        const res: any = await del_element({ id: data.id });
        MsgSuccess(res.message);
        await element_list();
    });
};

onMounted(() => {
    get_tree();
})
</script>

<template>
    <div>
        <koiCard>
            <div style="width: 100%;">
                <div style="width: 23%; float: left;">
                    <div style="width: 100%; float: left">
                        <koiCard style="height: 780px">
                            <div>
                                <div>
                                    <el-input v-model="filterText"
                                        style="margin-bottom: 5px; width: 90%; padding-right: 10px"
                                        placeholder="请输入节点名称" />
                                    <el-button type="text" style="padding-left: 5px" icon="Refresh"
                                        @click="get_tree()" />
                                </div>
                                <el-tree :data="treeData" :props="defaultProps" default-expand-all
                                    @node-click="get_element">
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
                                            <span v-if="data.type === 0" class="right" style="padding-right: 10px">
                                                <el-dropdown placement="bottom">
                                                    <el-icon>
                                                        <MoreFilled />
                                                    </el-icon>
                                                    <span class="el-dropdown-link" style="font-size: 20px" />
                                                    <template #dropdown>
                                                        <el-dropdown-menu class="header-new-drop">
                                                            <el-dropdown-item icon="CirclePlus"
                                                                @click="Add_menu(data)">新建子菜单</el-dropdown-item>
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
                                                            <el-dropdown-item icon="CirclePlus"
                                                                @click="Add_menu(data)">新建子菜单</el-dropdown-item>
                                                            <el-dropdown-item icon="Edit"
                                                                @click="Edit_menu(data)">重命名</el-dropdown-item>
                                                            <el-dropdown-item icon="Remove"
                                                                @click="Del_menu(data)">删除</el-dropdown-item>
                                                        </el-dropdown-menu>
                                                    </template>
                                                </el-dropdown>
                                            </span>
                                        </span>
                                    </template>
                                </el-tree>
                            </div>
                        </koiCard>
                    </div>
                </div>
                <div style="width: 77%; float: left">
                    <div style="width: 100%; float: left;">
                        <koiCard style="height: 780px">
                            <el-tabs v-model="tab_active" type="card" closable class="demo-tabs" @tab-remove="removeTab"
                                @tab-click="tab_click">
                                <el-tab-pane v-for="(item, index) in tab_list" :key="index" :label="item.title"
                                    :name="item.name">
                                    <template #label><el-icon style="padding-right: 5px;"><Folder /></el-icon>{{ item.name }}</template>
                                    <koiCard style="height: 690px">
                                        <div>
                                            <el-form :inline="true">
                                                <el-form-item label="元素名称：">
                                                    <el-input placeholder="请输入元素名称："
                                                        v-model="item.searchParams.search.name__contains" clearable
                                                        style="width: 300px"></el-input>
                                                </el-form-item>
                                                <el-form-item>
                                                    <el-button type="primary" icon="search" plain
                                                        @click="element_list()">搜索</el-button>
                                                    <el-button type="success" icon="plus" plain
                                                        @click="Add_element(item, item.id)">新增元素</el-button>
                                                </el-form-item>
                                            </el-form>
                                            <el-table border :data="item.content.content" style="width: 100%">
                                                <el-table-column prop="id" label="ID" width="60" />
                                                <el-table-column prop="name" label="元素名称" />
                                                <el-table-column label="元素类型" width="65">
                                                    <template #default="{ row }">
                                                        <el-tag v-if="row.element.type === 1" type="success">网页</el-tag>
                                                        <el-tag v-if="row.element.type === 2" type="warning">元素</el-tag>
                                                    </template>
                                                </el-table-column>
                                                <el-table-column label="定位类型" width="70">
                                                    <template #default="{ row }">
                                                        <el-tag
                                                            v-if="row.element.locator_type === 1 && row.element.type === 1">标题</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 2 && row.element.type === 1">网址</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 3 && row.element.type === 2">定位器</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 4 && row.element.type === 2">选择器</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 5 && row.element.type === 2">自定义</el-tag>
                                                    </template>
                                                </el-table-column>
                                                <el-table-column label="定位方式" width="110">
                                                    <template #default="{ row }">
                                                        <el-tag v-if="row.element.type === 1">-</el-tag>
                                                        <el-tag v-if="row.element.locator_type === 5">-</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 3 && row.element.type === 2">-</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 4 && row.element.type === 2 && row.element.locator_select_type === 1">id</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 4 && row.element.type === 2 && row.element.locator_select_type === 2">text</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 4 && row.element.type === 2 && row.element.locator_select_type === 3">label</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 4 && row.element.type === 2 && row.element.locator_select_type === 4">title</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 4 && row.element.type === 2 && row.element.locator_select_type === 5">placeholder</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 4 && row.element.type === 2 && row.element.locator_select_type === 6">alt</el-tag>
                                                        <el-tag
                                                            v-if="row.element.locator_type === 4 && row.element.type === 2 && row.element.locator_select_type === 7">role</el-tag>
                                                    </template>
                                                </el-table-column>
                                                <el-table-column label="目标值" :show-overflow-tooltip="true">
                                                    <template #default="{ row }">
                                                        {{ row.element.value }}
                                                    </template>
                                                </el-table-column>
                                                <el-table-column prop="username" label="更新人" width="70" />
                                                <el-table-column prop="create_time" label="创建时间" width="138" />
                                                <el-table-column prop="update_time" label="更新时间" width="138" />
                                                <el-table-column label="操作">
                                                    <template #default="{ row }">
                                                        <el-button type="primary" icon="edit" plain
                                                            @click="Edit_element(item, row)">编辑</el-button>
                                                        <el-button type="danger" icon="delete" plain
                                                            @click="Del_element(item, row)">删除</el-button>
                                                    </template>
                                                </el-table-column>
                                            </el-table>
                                            <div class="h-10px" />
                                            <el-pagination v-model:current-page="refresh_tab.searchParams.currentPage"
                                                v-model:page-size="refresh_tab.searchParams.pageSize"
                                                :total="refresh_tab.content.total" :page-sizes="[10, 20, 50, 100]"
                                                layout="total, sizes, prev, pager, next, jumper"
                                                @size-change="element_list()" @current-change="element_list()" />
                                        </div>
                                    </koiCard>
                                </el-tab-pane>
                            </el-tabs>
                        </koiCard>
                    </div>
                </div>
            </div>
            <div>
                <KoiDialog ref="add_koiDialogRef" :title="title" @koi-confirm="add_menu_confirm"
                    @koi-cancel="add_menu_cancel" :height="100">
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
                <KoiDialog ref="edit_koiDialogRef" :title="title" @koi-confirm="edit_menu_confirm"
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
                <KoiDialog ref="add_element_dialogRef" :title="title" @koi-confirm="add_element_confirm"
                    @koi-cancel="add_element_cancel" :height="350" width="35%">
                    <template #content>
                        <el-form :model="add_element_form" label-width="100px">
                            <el-form-item label="元素名称：">
                                <el-input v-model="add_element_form.name" />
                            </el-form-item>
                            <el-form-item label="元素类型：">
                                <el-select v-model="add_element_form.element.type" placeholder="请选择元素类型">
                                    <el-option v-for="item in element_type_list" :key="item.value" :label="item.name"
                                        :value="item.value" />
                                </el-select>
                            </el-form-item>
                            <el-form-item v-if="add_element_form.element.type === 1" label="浏览器：">
                                <el-select v-model="add_element_form.element.locator_type" placeholder="请选择浏览器">
                                    <el-option v-for="item in browser_list" :key="item.value" :label="item.name"
                                        :value="item.value" />
                                </el-select>
                            </el-form-item>
                            <el-form-item v-if="add_element_form.element.type === 2" label="定位类型：">
                                <el-select v-model="add_element_form.element.locator_type" placeholder="请选择定位类型">
                                    <el-option v-for="item in locator_list" :key="item.value" :label="item.name"
                                        :value="item.value" />
                                </el-select>
                            </el-form-item>
                            <el-form-item
                                v-if="add_element_form.element.locator_type === 4 && add_element_form.element.type === 2"
                                label="定位方式：">
                                <el-select v-model="add_element_form.element.locator_select_type" placeholder="请选择定位方式">
                                    <el-option v-for="item in locator_selects" :key="item.value" :label="item.label"
                                        :value="item.value" />
                                </el-select>
                            </el-form-item>
                            <el-form-item
                                v-if="add_element_form.element.locator_select_type === 7 && add_element_form.element.type === 2"
                                label="role对象：">
                                <el-select v-model="add_element_form.element.locator_role_type"
                                    style="padding-left: 5px; padding-block-end: 5px">
                                    <el-option v-for="(item, index) in role_list" :key="index" :label="item.label"
                                        :value="item.value"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="目标值：">
                                <el-input v-model="add_element_form.element.value" />
                            </el-form-item>
                        </el-form>
                    </template>
                </KoiDialog>
            </div>
            <div>
                <KoiDialog ref="edit_element_dialogRef" :title="title" @koi-confirm="edit_element_confirm"
                    @koi-cancel="edit_element_cancel" :height="350" width="35%">
                    <template #content>
                        <el-form :model="add_element_form" label-width="100px">
                            <el-form-item label="元素名称：">
                                <el-input v-model="add_element_form.name" />
                            </el-form-item>
                            <el-form-item label="元素类型：">
                                <el-select v-model="add_element_form.element.type" placeholder="请选择元素类型">
                                    <el-option v-for="item in element_type_list" :key="item.value" :label="item.name"
                                        :value="item.value" />
                                </el-select>
                            </el-form-item>
                            <el-form-item v-if="add_element_form.element.type === 1" label="浏览器：">
                                <el-select v-model="add_element_form.element.locator_type" placeholder="请选择浏览器">
                                    <el-option v-for="item in browser_list" :key="item.value" :label="item.name"
                                        :value="item.value" />
                                </el-select>
                            </el-form-item>
                            <el-form-item v-if="add_element_form.element.type === 2" label="定位类型：">
                                <el-select v-model="add_element_form.element.locator_type" placeholder="请选择定位类型">
                                    <el-option v-for="item in locator_list" :key="item.value" :label="item.name"
                                        :value="item.value" />
                                </el-select>
                            </el-form-item>
                            <el-form-item
                                v-if="add_element_form.element.locator_type === 4 && add_element_form.element.type === 2"
                                label="定位方式：">
                                <el-select v-model="add_element_form.element.locator_select_type" placeholder="请选择定位方式">
                                    <el-option v-for="item in locator_selects" :key="item.value" :label="item.label"
                                        :value="item.value" />
                                </el-select>
                            </el-form-item>
                            <el-form-item
                                v-if="add_element_form.element.locator_select_type === 7 && add_element_form.element.type === 2"
                                label="role对象：">
                                <el-select v-model="add_element_form.element.locator_role_type"
                                    style="padding-left: 5px; padding-block-end: 5px">
                                    <el-option v-for="(item, index) in role_list" :key="index" :label="item.label"
                                        :value="item.value"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="目标值：">
                                <el-input v-model="add_element_form.element.value" />
                            </el-form-item>
                        </el-form>
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
</style>