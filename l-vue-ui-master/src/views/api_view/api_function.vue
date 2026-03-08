<script setup lang="ts">
import { api_function, add_function, del_function, edit_function } from "@/api/api_api/api";
import { MsgBox, MsgSuccess } from "@/utils/koi";
import { ref, onMounted } from "vue";

const searchParams = ref<any>({
  currentPage: 1,
  pageSize: 10,
  search: {
    name__contains: ""
  }
});
const function_list = ref<any>([]);
const total = ref(0);
const add_form = ref<any>({});
const add_koiDialogRef = ref();
const title = ref("");
const edit_koiDialogRef = ref();

const get_function = async () => {
  const res: any = await api_function(searchParams.value);
  function_list.value = res.data.content;
  total.value = res.data.total;
};

const reset_search = () => {
  searchParams.value = {
    currentPage: 1,
    pageSize: 10,
    search: {
      name__contains: ""
    }
  };
  get_function();
};

const Add_function = () => {
  add_form.value = {
    name: "",
    description: ""
  };
  title.value = "添加公共函数";
  add_koiDialogRef.value.koiOpen();
};

const add_confirm = async () => {
  const res: any = await add_function(add_form.value);
  add_koiDialogRef.value.koiQuickClose(res.message);
  await get_function();
};

const add_cancel = async () => {
  add_koiDialogRef.value.koiQuickClose("已取消");
};

const Edit_function = async (row: any) => {
  title.value = "编辑公共函数";
  add_form.value = row;
  edit_koiDialogRef.value.koiOpen();
};

const edit_confirm = async () => {
  const res: any = await edit_function(add_form.value);
  edit_koiDialogRef.value.koiQuickClose(res.message);
  await get_function();
};

const edit_cancel = async () => {
  edit_koiDialogRef.value.koiQuickClose("已取消");
};

const Del_function = async (data: any) => {
  MsgBox("您确认需要删除该函数：" + data.name + "么？").then(async () => {
    const res: any = await del_function({
      id: data.id
    });
    MsgSuccess(res.message);
    await get_function();
  });
};
onMounted(() => {
  get_function();
});
</script>

<template>
  <div style="padding: 5px">
    <koiCard>
      <div>
        <div>
          <el-form :inline="true">
            <el-form-item label="名称">
              <el-input
                placeholder="请输入名称："
                v-model="searchParams.search.name__contains"
                clearable
                style="width: 150px; padding-right: 10px"
              ></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" icon="search" plain v-debounce="get_function">搜索</el-button>
              <el-button type="danger" icon="refresh" plain v-throttle="reset_search">重置</el-button>
              <el-button type="success" icon="Plus" plain @click="Add_function">添加公共函数</el-button>
            </el-form-item>
          </el-form>
          <el-table
            v-model:data="function_list"
            :border="true"
            :stripe="true"
            :header-cell-style="{ background: '#f9fafc', color: '#606266' }"
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="100"></el-table-column>
            <el-table-column prop="name" label="名称"></el-table-column>
            <el-table-column prop="description" label="描述"></el-table-column>
            <el-table-column prop="username" label="最后更新人" width="100"> </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" plain @click="Edit_function(row)">编辑</el-button>
                <el-button type="danger" plain @click="Del_function(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="h-10px"></div>
          <el-pagination
            background
            v-model:current-page="searchParams.currentPage"
            v-model:page-size="searchParams.pageSize"
            v-show="total > 0"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="get_function"
            @current-change="get_function"
          />
        </div>
      </div>
      <div>
        <KoiDialog
          ref="add_koiDialogRef"
          :title="title"
          @koi-confirm="add_confirm"
          @koi-cancel="add_cancel"
          :height="100"
          width="20%"
        >
          <template #content>
            <div>
              <el-form :model="add_form" label-width="100px">
                <el-form-item label="名称：">
                  <el-input v-model="add_form.name" style="width: 80%" placeholder="请输入名称"></el-input>
                </el-form-item>
                <el-form-item label="描述：">
                  <el-input v-model="add_form.description" style="width: 80%" placeholder="请输入数据库密码"></el-input>
                </el-form-item>
              </el-form>
            </div>
          </template>
        </KoiDialog>
      </div>
      <div>
        <KoiDialog
          ref="edit_koiDialogRef"
          :title="title"
          @koi-confirm="edit_confirm"
          @koi-cancel="edit_cancel"
          :height="100"
          width="20%"
        >
          <template #content>
            <div>
              <el-form :model="add_form" label-width="100px">
                <el-form-item label="名称：">
                  <el-input v-model="add_form.name" style="width: 80%" placeholder="请输入名称"></el-input>
                </el-form-item>
                <el-form-item label="描述：">
                  <el-input v-model="add_form.description" style="width: 80%" placeholder="请输入数据库密码"></el-input>
                </el-form-item>
              </el-form>
            </div>
          </template>
        </KoiDialog>
      </div>
    </koiCard>
  </div>
</template>

<style lang="scss" scoped></style>
