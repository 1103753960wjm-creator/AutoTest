<template>
  <div class="h-full">
    <el-row class="h-100%">
      <div class="absolute top-10px right-10px flex flex-items-center">
        <KoiLanguage></KoiLanguage>
        <KoiDark></KoiDark>
      </div>
      <el-col :lg="16" :md="12" :sm="15" :xs="0" class="flex items-center justify-center">
        <div class="login-background w-85% h-100%"></div>
        <div class="absolute text-center select-none">
          <el-image class="w-400px h-360px mb-50px animate-float <md:hidden <lg:w-360px h-320px" :src="bg" />
          <div class="font-bold text-3xl chroma-text mb-6px text-center <lg:text-2xl <md:hidden">
            {{ $t("login.welcome") }} {{ loginTitle || "L-Tester 管理平台" }}
          </div>
          <div class="chroma-text text-lg text-center <md:hidden">{{ $t("login.description") }}</div>
        </div>
      </el-col>
      <el-col :lg="8" :md="12" :sm="9" :xs="24"
        class="dark:bg-#161616 bg-gray-100 flex items-center justify-center flex-col">
        <div class="flex items-center">
          <el-image class="rounded-full w-36px h-36px" :src="logo" />
          <div class="ml-6px font-bold text-xl">{{ loginTitle || "L-Tester 管理平台" }}</div>
        </div>
        <div class="flex items-center space-x-3 text-gray-400 mt-16px mb-16px">
          <span class="h-1px w-16 bg-gray-300 inline-block"></span>
          <span class="text-center">{{ $t("login.username") }}</span>
          <span class="h-1px w-16 bg-gray-300 inline-block"></span>
        </div>
        <!-- 输入框盒子 -->
        <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="w-260px">
          <el-form-item prop="username">
            <el-input type="text" :placeholder="$t('login.username')" :suffix-icon="User" v-model="loginForm.username" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input type="password" :placeholder="$t('login.password')" show-password :suffix-icon="Lock"
              v-model="loginForm.password" />
          </el-form-item>
          <!-- 登录按钮 -->
          <el-form-item>
            <el-button name="login_button" type="primary" v-if="!loading" class="w-245px bg-[--el-color-primary]" round
              v-throttle:3000="handleLogin">{{ $t("login.in") }}
            </el-button>
            <el-button type="primary" id="login_button" v-else class="w-245px bg-[--el-color-primary]" round
              :loading="loading">{{
                $t("login.center")
              }}</el-button>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>

    <KoiLoading></KoiLoading>
  </div>
</template>

<script lang="ts" setup>
import { User, Lock } from "@element-plus/icons-vue";
import { ref, reactive, computed } from "vue";

import type { FormInstance, FormRules } from "element-plus";
import { MsgWarning, MsgError } from "@/utils/koi.ts";
import { useRouter } from "vue-router";
// import { koiLogin, getCaptcha } from "@/api/system/login/index.ts";
import useUserStore from "@/stores/modules/user.ts";
import useKeepAliveStore from "@/stores/modules/keepAlive.ts";
import { HOME_URL, LOGIN_URL } from "@/config/index.ts";
import { initDynamicRouter } from "@/routers/modules/dynamicRouter.ts";
import useTabsStore from "@/stores/modules/tabs.ts";
import { getAssets } from "@/utils/index.ts";
import settings from "@/settings";
import KoiDark from "./components/KoiDark.vue";
import KoiLoading from "./components/KoiLoading.vue";
import KoiLanguage from "./components/KoiLanguage.vue";
import { getLanguage } from "@/utils/index.ts";
import useGlobalStore from "@/stores/modules/global.ts";
import { Login } from "@/api/api_user/user.ts";
import { Md5 } from "ts-md5";

// 标题语言切换
const loginTitle = ref(settings.loginTitle);
loginTitle.value = computed(() => {
  return getLanguage(globalStore.language, settings.loginTitle, settings.loginEnTitle);
});

const globalStore = useGlobalStore();
const userStore = useUserStore();
const tabsStore = useTabsStore();
const keepAliveStore = useKeepAliveStore();
const router = useRouter();

/** 用户登录代码 */
const logo = getAssets("images/logo/logo.webp");
const bg = getAssets("images/login/bg.png");
const loginFormRef = ref<FormInstance>();
const loading = ref(false);

interface ILoginUser {
  username: string;
  password: string | number;
}

const loginForm = reactive<ILoginUser>({
  username: "",
  password: ""
});

let loginRules: any = reactive<FormRules<ILoginUser>>({});
loginRules = computed(() => {
  if (globalStore.language === "en") {
    return reactive<FormRules<ILoginUser>>({
      username: [{ required: true, message: "The user name cannot be empty", trigger: "blur" }],
      password: [{ required: true, message: "The password cannot be empty", trigger: "blur" }]
    });
  } else {
    return reactive<FormRules<ILoginUser>>({
      username: [{ required: true, message: "用户名不能为空", trigger: "blur" }],
      password: [{ required: true, message: "密码不能为空", trigger: "blur" }]
    });
  }
});

/** 登录 */
const handleLogin = () => {
  if (!loginFormRef.value) return;
  (loginFormRef.value as any).validate(async (valid: any, fields: any) => {
    const md5 = new Md5();
    const username = loginForm.username;
    const password = md5.appendStr(loginForm.password.toString()).end();
    if (valid) {
      loading.value = true;
      try {
        // 1、执行登录接口
        const res: any = await Login({ username, password });
        userStore.setToken(res.data.token, res.data.user_id, res.data.avatar, res.data.username);
        // 2、添加动态路由 AND 用户按钮 AND 角色信息 AND 用户个人信息
        if (userStore?.token) {
          await initDynamicRouter();
        } else {
          MsgWarning("请重新登录🌻");
          router.replace(LOGIN_URL);
          return;
        }
        // 3、清空 tabs数据、keepAlive缓存数据
        tabsStore.setTab([]);
        keepAliveStore.setKeepAliveName([]);

        // 4、跳转到首页
        router.replace(HOME_URL);
      } catch {
        // 等待1秒关闭loading
        let loadingTime = 1;
        setInterval(() => {
          loadingTime--;
          if (loadingTime === 0) {
            loading.value = false;
          }
        }, 1000);
      }
    } else {
      console.log("登录校验失败", fields);
      MsgError("校验失败，信息填写有误🌻");
    }
  });
};
</script>

<style lang="scss" scoped>
/** 备案号 */
.beianhao {
  position: absolute;
  bottom: 10px;
  left: auto;
  font-size: 12px;
  font-weight: bold;
}

.login-background {
  background: linear-gradient(155deg, #07070915 12%, var(--el-color-primary) 36%, #07070915 76%);
  filter: blur(100px);
}

.animate-float {
  animation: float 5s linear 0ms infinite;
}

@keyframes float {
  0% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-20px);
  }

  100% {
    transform: translateY(0);
  }
}
</style>
