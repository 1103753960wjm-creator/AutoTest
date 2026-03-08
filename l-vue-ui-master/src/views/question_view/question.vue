<script setup lang="ts">
import {
  add_answer,
  add_question,
  del_answer,
  del_question,
  edit_answer,
  edit_question,
  question_list
} from "@/api/api_question/question";
import { MsgBox, MsgSuccess } from "@/utils/koi";
import { onMounted, ref } from "vue";

const tableData = ref<any>([]);
const searchParams = ref({
  currentPage: 1,
  pageSize: 10,
  search: {
    title__icontains: ""
  }
});
const total = ref(0);
const title = ref<any>("");
const add_form = ref<any>({});
const add_koiDialogRef = ref<any>(null);
const edit_koiDialogRef = ref<any>(null);
const resetsearch = () => {
  searchParams.value = {
    currentPage: 1,
    pageSize: 10,
    search: {
      title__icontains: ""
    }
  };
  get_question();
};
const get_question = async () => {
  const res: any = await question_list(searchParams.value);
  tableData.value = res.data.content;
  total.value = res.data.total;
};

const Add = async () => {
  add_koiDialogRef.value.koiOpen();
  title.value = "新增问题";
  add_form.value.type = 1;
  add_form.value.title = "";
};

const Answer = async (row: any) => {
  title.value = "新增回复";
  add_form.value.title = "";
  add_koiDialogRef.value.koiOpen();
  add_form.value.id = row.id;
  add_form.value.uuid = row.uuid;
  add_form.value.type = 2;
};

const add_confirm = async () => {
  let res: any = {};
  if (add_form.value.type === 1) {
    res = await add_question(add_form.value);
  } else {
    res = await add_answer(add_form.value);
  }
  await get_question();
  add_koiDialogRef.value.koiQuickClose(res.message);
};

const add_cancel = async () => {
  add_koiDialogRef.value.koiQuickClose("已取消");
};

const Edit = (row: any) => {
  add_form.value = row;
  edit_koiDialogRef.value.koiOpen();
  title.value = "编辑内容";
};

const edit_confirm = async () => {
  if (add_form.value.type === 1) {
    const res: any = await edit_question(add_form.value);
    edit_koiDialogRef.value.koiQuickClose(res.message);
  } else {
    const res: any = await edit_answer(add_form.value);
    edit_koiDialogRef.value.koiQuickClose(res.message);
  }
  await get_question();
};

const edit_cancel = async () => {
  edit_koiDialogRef.value.koiQuickClose("已取消");
};

const Del = (row: any) => {
  const msg = "您确认需要删除： " + row.title + " 么？";
  MsgBox(msg).then(async () => {
    if (row.type === 1) {
      const res: any = await del_question({ id: row.id });
      MsgSuccess(res.message);
    } else {
      const res: any = await del_answer({ uuid: row.uuid, id: row.id });
      MsgSuccess(res.message);
    }
    await get_question();
  });
};

onMounted(() => {
  get_question();
});
</script>

<template>
  <div style="padding: 10px">
    <div>
      <koiCard>
        <div>
          <el-form :inline="true">
            <el-form-item label="标题：" prop="userName">
              <el-input
                placeholder="请输入问题标题"
                v-model="searchParams.search.title__icontains"
                clearable
                style="width: 400px"
              ></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" icon="search" plain v-debounce="get_question">搜索</el-button>
              <el-button type="danger" icon="refresh" plain v-throttle="resetsearch">重置</el-button>
            </el-form-item>
            <el-form-item>
              <el-button type="success" icon="Plus" plain @click="Add">提问</el-button>
            </el-form-item>
          </el-form>
          <div class="h-10px"></div>
          <el-table
            :data="tableData"
            style="width: 100%; margin-bottom: 20px"
            row-key="uuid"
            border
            default-expand-all
            :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
          >
            <el-table-column label="ID" width="100">
              <template #default="{ row }">
                <text type="danger" v-if="row.type == 1">{{ row.id }}</text>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="标题" :show-overflow-tooltip="true" />
            <el-table-column label="类型" width="80">
              <template #default="{ row }">
                <el-tag type="danger" v-if="row.type == 1"
                  ><el-icon><QuestionFilled /></el-icon>提问</el-tag
                >
                <el-tag type="success" v-if="row.type == 2"
                  ><el-icon><UserFilled /></el-icon>回复</el-tag
                >
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="提问时间" sortable width="200" />
            <el-table-column prop="update_time" label="最后更新时间" sortable width="200" />
            <el-table-column prop="username" label="创建人" sortable width="200" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button v-if="row.type === 1" type="success" plain @click="Answer(row)">回复</el-button>
                <el-button type="primary" plain @click="Edit(row)">编辑</el-button>
                <el-button type="danger" plain @click="Del(row)">删除</el-button>
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
            @size-change="get_question"
            @current-change="get_question"
          />
        </div>
      </koiCard>
    </div>
    <div>
      <KoiDialog
        ref="add_koiDialogRef"
        :title="title"
        @koi-confirm="add_confirm"
        @koi-cancel="add_cancel"
        :height="200"
        width="30%"
      >
        <template #content>
          <div>
            <el-form :model="add_form" label-width="100px">
              <el-form-item label="内容：">
                <textarea v-model="add_form.title" style="width: 85%; height: 150px" placeholder="请输入内容"></textarea>
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
        :height="200"
        width="30%"
      >
        <template #content>
          <div>
            <el-form :model="add_form" label-width="100px">
              <el-form-item label="内容：">
                <textarea v-model="add_form.title" style="width: 85%; height: 150px" placeholder="请输入内容"></textarea>
              </el-form-item>
            </el-form>
          </div>
        </template>
      </KoiDialog>
    </div>
  </div>
</template>

<style lang="less" scoped></style>
