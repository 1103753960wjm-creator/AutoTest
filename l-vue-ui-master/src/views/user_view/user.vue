<script setup lang="ts" name="user  Page">
// 已使用字典案例
import { ref, onMounted } from "vue";
import { MsgBox, MsgSuccess, NoticeError } from "@/utils/koi.ts";
import { add_user, del_user, edit_user, get_user_list, role_select, change_role_user } from "@/api/api_user/user.ts";
import { Md5 } from "ts-md5";
// 搜索区域展示
const showSearch = ref<boolean>(true);

//总数
const total = ref<number>(0);

// 查询参数
const searchParams = ref({
  currentPage: 1, // 第几页
  pageSize: 10, // 每页显示多少条
  search: {
    username__icontains: "",
    phone__icontains: ""
  }
});
// 添加用户
const add_form = ref({
  account: "",
  username: "",
  password: "",
  phone: "",
  email: "",
  avatar: "",
  status: "0",
  type: "add"
});

/** 添加 AND 修改抽屉 */
const koiDrawerRef = ref();

// 数据表格加载页面动画
const loading = ref(false);
// 表数据
const tableList = ref<any>([]);

const user_list = async () => {
  try {
    loading.value = true;
    tableList.value = []; // 重置表格数据
    const res: any = await get_user_list(searchParams.value);
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
      username__icontains: "",
      phone__icontains: ""
    }
  };
  await user_list();
};

/** 添加 */
const Add = () => {
  // 打开弹出框
  // eslint-disable-next-line @typescript-eslint/no-unused-expressions
  koiDrawerRef.value.koiOpen();
  add_form.value.password = "";
  // 重置表单
  resetForm();
};

/** 清空表单数据 */
const resetForm = () => {
  add_form.value = {
    account: "",
    username: "",
    password: "",
    phone: "",
    email: "",
    avatar: "",
    status: "0",
    type: "add"
  };
};

// 确定按钮是否显示loading
const confirmLoading = ref(false);

const add_Confirm = async () => {
  const md5 = new Md5();
  if (add_form.value.type === "add") {
    try {
      const password: any = md5.appendStr(add_form.value.password.toString()).end()
      add_form.value.password = password;
      const res: any = await add_user(add_form.value);
      confirmLoading.value = false;
      koiDrawerRef.value.koiQuickClose(res.message);
      resetForm();
      await user_list();
    } catch {
      confirmLoading.value = false;
      NoticeError("修改失败，请刷新重试🌻");
    }
  } else {
    const res: any = await edit_user(add_form.value);
    confirmLoading.value = false;
    koiDrawerRef.value.koiQuickClose(res.message);
    resetForm();
    await user_list();
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
  add_form.value.password = "";
  koiDrawerRef.value.koiOpen();
};

const handleSelectionChange = (selection: any) => {
  distribute_form.value.user_list = selection.map((item: any) => item.id);
};

const Delete = async (row: any) => {
  console.log(row.username);
  MsgBox("您确认需要删除用户名称： " + row.username + " 么？").then(async () => {
    const res: any = await del_user({ id: row.id });
    MsgSuccess(res.message);
    await user_list();
  });
};

const role_list = ref<any>([]);
const title = ref<string>("");
const distribute_koiDialogRef = ref<any>(null);
const Distribute = async () => {
  await get_role_select();
  title.value = "分配角色";
  distribute_koiDialogRef.value.koiOpen();
};

const distribute_form = ref<any>({
  "role_id": null,
  "user_list": [],
});
const get_role_select = async () => {
  const res: any = await role_select({});
  role_list.value = res.data;
};

const distribute_confirm = async () => {
  const res: any = await change_role_user(distribute_form.value);
  if (res.code === 200) {
    distribute_koiDialogRef.value.koiQuickClose(res.message);
    await user_list();
  }
};

const distribute_cancel = () => {
  distribute_koiDialogRef.value.koiClose();
};

onMounted(() => {
  // 获取数据表格数据
  user_list();
});
</script>

<template>
  <div>
    <KoiCard>
      <!-- 搜索条件 -->
      <el-form v-show="showSearch" :inline="true">
        <el-form-item label="用户名称" prop="userName">
          <el-input placeholder="请输入用户名称" v-model="searchParams.search.username__icontains" clearable
            style="width: 200px"></el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input placeholder="请输入手机号" v-model="searchParams.search.phone__icontains" clearable
            style="width: 200px"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="search" plain v-debounce="user_list">搜索</el-button>
          <el-button type="danger" icon="refresh" plain v-throttle="resetsearch">重置</el-button>
          <el-button type="primary" icon="plus" plain @click="Add()">新增</el-button>
          <el-button type="success" icon="edit" plain @click="Distribute">分配角色</el-button>
        </el-form-item>
      </el-form>

      <div class="h-10px"></div>
      <!-- 数据表格 :data="tableList" -->
      <el-table v-loading="loading" border :data="tableList" empty-text="暂时没有数据哟🌻"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="序号" prop="userId" width="80px" align="center" type="index"></el-table-column>
        <el-table-column label="头像" prop="avatar" align="center" width="80px">
          <template #default="scope">
            <div class="flex justify-center">
              <el-image class="rounded-full w-36px h-36px" :preview-teleported="true"
                :preview-src-list="[scope.row.avatar]" :src="scope.row.avatar != null && scope.row.avatar != ''
                    ? scope.row.avatar
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
        <el-table-column label="用户名" prop="username" width="120px" align="center"
          :show-overflow-tooltip="true"></el-table-column>
        <el-table-column label="角色" prop="role_name" width="120px" align="center"
          :show-overflow-tooltip="true"></el-table-column>
        <el-table-column label="邮箱" prop="email" align="center" :show-overflow-tooltip="true"></el-table-column>
        <el-table-column label="手机号" prop="phone" align="center" :show-overflow-tooltip="true"></el-table-column>
        <!-- 注意：如果后端数据返回的是字符串"0" OR "1"，这里的active-value AND inactive-value不需要加冒号，会认为是字符串，否则：后端返回是0 AND 1数字，则需要添加冒号 -->
        <el-table-column label="用户状态" prop="userStatus" align="center">
          <template #default="scope">
            <!-- {{ scope.row.userStatus }} -->
            <el-switch v-model="scope.row.status" active-text="启用" inactive-text="停用" active-value="1"
              inactive-value="0" :inline-prompt="true" disabled>
            </el-switch>
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
        layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="user_list"
        @current-change="user_list" />
      <KoiDrawer ref="koiDrawerRef" title="用户" @koi-confirm="add_Confirm" @koi-cancel="add_Cancel">
        <template #content>
          <el-form ref="formRef" :model="add_form" label-width="80px" status-icon>
            <el-row>
              <el-col :xs="{ span: 24 }" :sm="{ span: 24 }">
                <el-form-item v-if="add_form.type === 'add'" label="用户名" prop="userTitle">
                  <el-input v-model="add_form.username" placeholder="用户名称" clearable />
                </el-form-item>
              </el-col>
              <el-col :xs="{ span: 24 }" :sm="{ span: 24 }">
                <el-form-item v-if="add_form.type === 'add'" label="账户" prop="userTitle">
                  <el-input v-model="add_form.account" placeholder="用来登录的账户名" clearable />
                </el-form-item>
              </el-col>
              <el-col :xs="{ span: 24 }" :sm="{ span: 24 }">
                <el-form-item v-if="add_form.type === 'add'" label="密码" prop="userTitle">
                  <el-input v-model="add_form.password" placeholder="请输入密码" clearable />
                </el-form-item>
              </el-col>
              <el-col :xs="{ span: 24 }" :sm="{ span: 24 }">
                <el-form-item label="用户头像" prop="avatar">
                  <KoiUploadImage v-model:image-url="add_form.avatar">
                    <template #content>
                      <el-icon>
                        <Avatar />
                      </el-icon>
                      <span>请上传头像</span>
                    </template>
                    <template #tip>图片最大为 3M；最多上传1个；</template>
                  </KoiUploadImage>
                  <!-- <el-input v-model="form.avatar" placeholder="请输入用户头像地址" clearable /> -->
                </el-form-item>
              </el-col>
              <el-col :xs="{ span: 24 }" :sm="{ span: 24 }">
                <el-form-item label="用户状态" prop="userStatus">
                  <el-switch v-model="add_form.status" active-text="启用" inactive-text="停用" active-value="1"
                    inactive-value="0" :inline-prompt="true">
                  </el-switch>
                </el-form-item>
              </el-col>
              <el-col :xs="{ span: 24 }" :sm="{ span: 24 }">
                <el-form-item label="手机" prop="phone">
                  <el-input v-model="add_form.phone" placeholder="请输入手机号"></el-input>
                </el-form-item>
              </el-col>
              <el-col :xs="{ span: 24 }" :sm="{ span: 24 }">
                <el-form-item label="邮箱" prop="remark">
                  <el-input v-model="add_form.email" :rows="5" type="textarea" placeholder="请输入用户邮箱" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </template>
      </KoiDrawer>
    </KoiCard>
    <div>
        <KoiDialog v-loading="loading" ref="distribute_koiDialogRef" :title="title" @koi-confirm="distribute_confirm"
          @koi-cancel="distribute_cancel" :height="100" width="20%">
          <template #content>
            <div>
              <el-form :model="distribute_form">
                <el-form-item label="选择角色：">
                  <el-select v-model="distribute_form.role_id" placeholder="请选择角色">
                    <el-option v-for="item in role_list" :key="item.value" :label="item.name" :value="item.value">
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-form>
            </div>
          </template>
        </koiDialog>
    </div>
  </div>
</template>

<style scoped lang="scss">
// 穿梭框高度调整
:deep(.el-transfer-panel__body) {
  height: 400px;
}
</style>
