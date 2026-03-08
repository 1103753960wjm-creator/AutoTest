<script setup lang="ts" name="user  Page">
// 已使用字典案例
import { ref, onMounted } from "vue";
import { MsgBox, MsgSuccess, NoticeError } from "@/utils/koi.ts";
import { delete_img, img_list } from "@/api/api_app/img.ts";
import { app_menu_select } from "@/api/api_app/app";

// 搜索区域展示
const showSearch = ref<boolean>(true);

//总数
const total = ref<number>(0);

// 查询参数
const searchParams = ref({
  currentPage: 1, // 第几页
  pageSize: 10, // 每页显示多少条
  search: {
    file_name__icontains: "",
    menu_id: ""
  }
});
// 添加用户
const add_form = ref({
  file_list: [],
  type: ""
});

/** 添加 AND 修改抽屉 */
const koiDrawerRef = ref();

// 数据表格加载页面动画
const loading = ref(false);
// 表数据
const tableList = ref<any>([]);

const app_menu_list = ref<any>([]);
const get_app_select = async () => {
  const res: any = await app_menu_select({});
  app_menu_list.value = res.data;
  searchParams.value.search.menu_id = app_menu_list.value[0].id;
  await get_img_list();
};


const get_img_list = async () => {
  try {
    loading.value = true;
    tableList.value = []; // 重置表格数据
    const res: any = await img_list(searchParams.value);
    tableList.value = res.data.content;
    total.value = res.data.total;
    loading.value = false;
  } catch {
    NoticeError("数据查询失败，请刷新重试🌻");
  }
};
const resetsearch = async () => {
  searchParams.value = {
    currentPage: 1, // 第几页
    pageSize: 10, // 每页显示多少条
    search: {
      file_name__icontains: "",
      menu_id: ""
    }
  };
  await get_img_list();
};

/** 添加 */
const Add = () => {
  // 打开弹出框
  // eslint-disable-next-line @typescript-eslint/no-unused-expressions
  koiDrawerRef.value.koiOpen();
  // 重置表单
  resetForm();
  add_form.value.type = "add";
};

/** 清空表单数据 */
const resetForm = () => {
  add_form.value = {
    file_list: [],
    type: ""
  };
};

// 确定按钮是否显示loading
const confirmLoading = ref(false);

const add_Confirm = async () => {
  if (add_form.value.type === "add") {
    try {
      const res: any = await img_list(searchParams.value);
      confirmLoading.value = false;
      await get_img_list();
      koiDrawerRef.value.koiQuickClose(res.message);
      resetForm();
    } catch {
      confirmLoading.value = false;
      NoticeError("修改失败，请刷新重试🌻");
    }
  } else {
    const res: any = await img_list(searchParams.value);
    confirmLoading.value = false;
    koiDrawerRef.value.koiQuickClose(res.message);
    resetForm();
    await get_img_list();
  }
};

/** 取消 */
const add_Cancel = () => {
  koiDrawerRef.value.koiClose();
};

// 编辑用户
const Edit = async (row: any) => {
  add_form.value.type = "edit";
  add_form.value = row;
  koiDrawerRef.value.koiOpen();
};

const handleSelectionChange = (selection: any) => {
  console.log(selection);
};

const Delete = async (row: any) => {
  MsgBox("您确认需要删除用户名称[" + row.file_name + "]么？").then(async () => {
    const res: any = await delete_img({ id: row.id });
    MsgSuccess(res.message);
    await get_img_list();
  });
};

onMounted(() => {
  get_app_select();
});
</script>

<template>
  <div>
    <KoiCard>
      <!-- 搜索条件 -->
      <el-form v-show="showSearch" :inline="true">
        <el-form-item label="项目：">
          <el-select v-model="searchParams.search.menu_id" placeholder="请选择菜单名称" clearable style="width: 200px"
            @change="get_img_list">
            <el-option v-for="item in app_menu_list" :key="item.id" :label="item.name" :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="图像名称" prop="userName">
          <el-input placeholder="请输入图像名称" v-model="searchParams.search.file_name__icontains" clearable
            style="width: 200px"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="search" plain v-debounce="get_img_list">搜索</el-button>
          <el-button type="danger" icon="refresh" plain v-throttle="resetsearch">重置</el-button>
          <el-button type="primary" icon="plus" plain @click="Add()">新增</el-button>
        </el-form-item>
      </el-form>
      <div class="h-10px"></div>
      <!-- 数据表格 :data="tableList" -->
      <el-table v-loading="loading" border :data="tableList" empty-text="暂时没有数据哟🌻"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="序号" prop="id" width="80px" align="center" type="index"></el-table-column>
        <el-table-column label="名称" prop="file_name" width="300px" align="center"
          :show-overflow-tooltip="true"></el-table-column>
        <el-table-column label="预览" prop="avatar" align="center">
          <template #default="scope">
            <div class="flex justify-center">
              <el-image class="w-200px h-36px" :preview-teleported="true" :preview-src-list="[scope.row.file_path]"
                :src="scope.row.file_path != null && scope.row.file_path != ''
                  ? scope.row.file_path
                  : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
                  ">
                <template #error>
                  <el-icon class="c-[--el-color-primary]" :size="36">
                    <CircleCloseFilled />
                  </el-icon>
                </template>
              </el-image>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="create_time" width="180px" align="center"></el-table-column>
        <el-table-column label="操作" align="center" width="150" fixed="right">
          <template #default="{ row }">
            <el-tooltip content="修改🌻" placement="top">
              <el-button type="primary" icon="Edit" circle plain @click="Edit(row)"></el-button>
            </el-tooltip>
            <el-tooltip content="删除🌻" placement="top">
              <el-button type="danger" icon="Delete" circle plain @click="Delete(row)"></el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
      <div class="h-10px"></div>
      <el-pagination background v-model:current-page="searchParams.currentPage"
        v-model:page-size="searchParams.pageSize" v-show="total > 0" :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="get_img_list"
        @current-change="get_img_list" />

      <KoiDrawer ref="koiDrawerRef" title="用户" @koi-confirm="add_Confirm" @koi-cancel="add_Cancel">
        <template #content>
          <el-form ref="formRef" :model="add_form" label-width="80px" status-icon>
            <el-row>
              <el-col :xs="{ span: 24 }" :sm="{ span: 24 }">
                <el-form-item label="用户头像" prop="avatar">
                  <KoiUploadImages v-model:image-url="add_form.file_list" :app_menu_id="searchParams.search.menu_id">
                    <template #content>
                      <el-icon>
                        <Avatar />
                      </el-icon>
                      <span>请上传图片</span>
                    </template>
                    <template #tip>图片最大为 3M；最多上传9个；</template>
                  </KoiUploadImages>
                  <!-- <el-input v-model="form.avatar" placeholder="请输入用户头像地址" clearable /> -->
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </template>
      </KoiDrawer>
    </KoiCard>
  </div>
</template>

<style scoped lang="scss">
// 穿梭框高度调整
:deep(.el-transfer-panel__body) {
  height: 400px;
}
</style>
