<script setup lang="ts">
import { add_api_db, api_db, del_api_db, edit_api_db } from "@/api/api_api/api";
import { MsgBox, MsgSuccess } from "@/utils/koi";
import { ref, onMounted } from "vue";

const searchParams = ref<any>({
  currentPage: 1,
  pageSize: 10,
  search: {
    name__contains: ""
  }
});
const db_list = ref<any>([]);
const total = ref(0);
const add_form = ref<any>({});
const add_koiDialogRef = ref();
const title = ref("");
const edit_koiDialogRef = ref();

const get_db = async () => {
  const res: any = await api_db(searchParams.value);
  db_list.value = res.data.content;
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
  get_db();
};

const Add_db = () => {
  add_form.value = {
    name: "",
    config: {
      host: "",
      port: "",
      database: "",
      user: "",
      password: ""
    }
  };
  title.value = "添加数据库";
  add_koiDialogRef.value.koiOpen();
};

const add_confirm = async () => {
    const res: any = await add_api_db(add_form.value);
    add_koiDialogRef.value.koiQuickClose(res.message);
    await get_db();

};

const add_cancel = async () => {
    add_koiDialogRef.value.koiQuickClose("已取消");
};

const Edit_db = async (row: any) => {
    title.value = "编辑数据库"
    add_form.value = row;
    edit_koiDialogRef.value.koiOpen();
};

const edit_confirm = async () => {
    const res: any = await edit_api_db(add_form.value);
    edit_koiDialogRef.value.koiQuickClose(res.message);
    await get_db();
};

const edit_cancel = async () => {
    edit_koiDialogRef.value.koiQuickClose("已取消");
};

const Del_db = async (data: any) => {
    MsgBox("您确认需要删除该数据库：" + data.name + "么？").then(async () => {
        const res: any = await del_api_db({
            id: data.id
        });
        MsgSuccess(res.message);
        await get_db();
    });
};
onMounted(() => {
  get_db();
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
              <el-button type="primary" icon="search" plain v-debounce="get_db">搜索</el-button>
              <el-button type="danger" icon="refresh" plain v-throttle="reset_search">重置</el-button>
              <el-button type="success" icon="Plus" plain @click="Add_db">添加数据库</el-button>
            </el-form-item>
          </el-form>
          <el-table
            :data="db_list"
            :border="true"
            :stripe="true"
            :header-cell-style="{ background: '#f9fafc', color: '#606266' }"
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="name" label="名称"></el-table-column>
            <el-table-column prop="host" label="数据库地址">
              <template #default="{ row }">
                {{ row.config.host }}
              </template>
            </el-table-column>
            <el-table-column prop="port" label="数据库端口">
              <template #default="{ row }">
                {{ row.config.port }}
              </template>
            </el-table-column>
            <el-table-column prop="db" label="数据库名称">
              <template #default="{ row }">
                {{ row.config.database }}
              </template>
            </el-table-column>
            <el-table-column prop="user" label="数据库用户">
              <template #default="{ row }">
                {{ row.config.user }}
              </template>
            </el-table-column>
            <el-table-column prop="update_time" label="更新时间"></el-table-column>
            <el-table-column prop="username" label="最后更新人" width="100">
            </el-table-column>
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button type="primary" plain @click="Edit_db(row)">编辑</el-button>
                <el-button type="danger" plain @click="Del_db(row)">删除</el-button>
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
            @size-change="get_db"
            @current-change="get_db"
          />
        </div>
      </div>
      <div>
        <KoiDialog
          ref="add_koiDialogRef"
          :title="title"
          @koi-confirm="add_confirm"
          @koi-cancel="add_cancel"
          :height="260"
          width="40%"
        >
          <template #content>
            <div>
              <el-form :model="add_form" label-width="100px">
                <el-form-item label="名称：">
                  <el-input v-model="add_form.name" style="width: 85%" placeholder="请输入名称"></el-input>
                </el-form-item>
                <el-form-item label="数据库地址：">
                    <el-input v-model="add_form.config.host" style="width: 85%" placeholder="请输入数据库地址"></el-input>
                </el-form-item>
                <el-form-item label="数据库端口：">
                    <el-input v-model="add_form.config.port" style="width: 85%" placeholder="请输入数据库端口"></el-input>
                </el-form-item>
                <el-form-item label="数据库名称：">
                    <el-input v-model="add_form.config.database" style="width: 85%" placeholder="请输入数据库名称"></el-input>
                </el-form-item>
                <el-form-item label="数据库用户：">
                    <el-input v-model="add_form.config.user" style="width: 85%" placeholder="请输入数据库用户"></el-input>
                </el-form-item>
                <el-form-item label="数据库密码：">
                    <el-input v-model="add_form.config.password" style="width: 85%" placeholder="请输入数据库密码"></el-input>
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
          :height="260"
          width="40%"
        >
          <template #content>
            <div>
              <el-form :model="add_form" label-width="100px">
                <el-form-item label="名称：">
                  <el-input v-model="add_form.name" style="width: 85%" placeholder="请输入名称"></el-input>
                </el-form-item>
                <el-form-item label="数据库地址：">
                    <el-input v-model="add_form.config.host" style="width: 85%" placeholder="请输入数据库地址"></el-input>
                </el-form-item>
                <el-form-item label="数据库端口：">
                    <el-input v-model="add_form.config.port" style="width: 85%" placeholder="请输入数据库端口"></el-input>
                </el-form-item>
                <el-form-item label="数据库名称：">
                    <el-input v-model="add_form.config.database" style="width: 85%" placeholder="请输入数据库名称"></el-input>
                </el-form-item>
                <el-form-item label="数据库用户：">
                    <el-input v-model="add_form.config.user" style="width: 85%" placeholder="请输入数据库用户"></el-input>
                </el-form-item>
                <el-form-item label="数据库密码：">
                    <el-input v-model="add_form.config.password" style="width: 85%" placeholder="请输入数据库密码"></el-input>
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
