<script setup lang="ts">
import { add_var, api_var_list, del_var, edit_var } from "@/api/api_api/api";
import { MsgBox, MsgSuccess } from "@/utils/koi";
import { ref, onMounted } from "vue";

const searchParams = ref<any>({
  currentPage: 1,
  pageSize: 10,
  search: {
    name__contains: ""
  }
});
const var_list = ref<any>([]);
const total = ref(0);
const add_form = ref<any>({});
const add_koiDialogRef = ref();
const title = ref("");
const edit_koiDialogRef = ref();

const get_var = async () => {
  const res: any = await api_var_list(searchParams.value);
  var_list.value = res.data.content;
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
  get_var();
};

const Add_var = () => {
  add_form.value = {
    name: "",
    value: ""
  };
  title.value = "添加全局变量";
  add_koiDialogRef.value.koiOpen();
};

const add_confirm = async () => {
    const res: any = await add_var(add_form.value);
    add_koiDialogRef.value.koiQuickClose(res.message);
    await get_var();

};

const add_cancel = async () => {
    add_koiDialogRef.value.koiQuickClose("已取消");
};

const Edit_var = async (row: any) => {
    title.value = "编辑变量"
    add_form.value = row;
    edit_koiDialogRef.value.koiOpen();
};

const edit_confirm = async () => {
    const res: any = await edit_var(add_form.value);
    edit_koiDialogRef.value.koiQuickClose(res.message);
    await get_var();
};

const edit_cancel = async () => {
    edit_koiDialogRef.value.koiQuickClose("已取消");
};

const Del_var = async (data: any) => {
    MsgBox("您确认需要删除该数据库：" + data.name + "么？").then(async () => {
        const res: any = await del_var({
            id: data.id
        });
        MsgSuccess(res.message);
        await get_var();
    });
};
onMounted(() => {
  get_var();
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
                style="width: 200px"
              ></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" icon="search" plain v-debounce="get_var">搜索</el-button>
              <el-button type="danger" icon="refresh" plain v-throttle="reset_search">重置</el-button>
              <el-button type="success" icon="Plus" plain @click="Add_var">添加变量</el-button>
            </el-form-item>
          </el-form>
          <el-table
            :data="var_list"
            :border="true"
            :stripe="true"
            :header-cell-style="{ background: '#f9fafc', color: '#606266' }"
            style="width: 100%"
          >
            <el-table-column prop="name" label="变量名"></el-table-column>
            <el-table-column prop="value" label="变量值" :show-overflow-tooltip="true"></el-table-column>
            <el-table-column prop="update_time" label="更新时间"></el-table-column>
            <el-table-column prop="username" label="最后更新人">
            </el-table-column>
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button type="primary" plain @click="Edit_var(row)">编辑</el-button>
                <el-button type="danger" plain @click="Del_var(row)">删除</el-button>
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
            @size-change="get_var"
            @current-change="get_var"
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
          width="40%"
        >
          <template #content>
            <div>
              <el-form :model="add_form" label-width="100px">
                <el-form-item label="变量名：">
                  <el-input v-model="add_form.name" style="width: 85%" placeholder="请输入名称"></el-input>
                </el-form-item>
                <el-form-item label="变量值：">
                  <el-input v-model="add_form.value" style="width: 85%" placeholder="请输入名称"></el-input>
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
          width="40%"
        >
          <template #content>
            <div>
                <el-form :model="add_form" label-width="100px">
                <el-form-item label="变量名：">
                  <el-input v-model="add_form.name" style="width: 85%" placeholder="请输入名称"></el-input>
                </el-form-item>
                <el-form-item label="变量值：">
                  <el-input v-model="add_form.value" style="width: 85%" placeholder="请输入名称"></el-input>
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
