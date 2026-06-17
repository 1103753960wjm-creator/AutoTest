<template>
  <el-config-provider :locale="elementLocale">
    <div id="app">
      <router-view v-slot="{ Component, route }">
        <transition name="fade-fast" mode="out-in">
          <component :is="Component" :key="getLayoutRouteKey(route)" />
        </transition>
      </router-view>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { ElConfigProvider } from 'element-plus'
import { useAppStore } from '@/stores/app'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'

const appStore = useAppStore()

// 根据 Element Plus 需要的 locale 配置
const elementLocale = computed(() => {
  return appStore.language === 'zh-cn' ? zhCn : en
})

const getLayoutRouteKey = (route) => {
  // 登录后所有业务模块共用同一个 Layout 实例，避免跨模块切换时销毁侧边栏和导航队列。
  if (route?.matched?.some((record) => record.meta?.requiresAuth)) {
    return 'layout:authenticated'
  }

  return route?.matched?.[0]?.path || route?.name || route?.path || 'layout:default'
}

// 认证初始化由路由守卫 beforeEach 统一处理，此处不再重复调用
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 
    'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  width: 100vw;
}

/* 根层级的快速切换动画，防止跨模块切换时 DOM 挂起卡死 */
.fade-fast-enter-active,
.fade-fast-leave-active {
  transition: opacity 0.15s ease;
}

.fade-fast-enter-from,
.fade-fast-leave-to {
  opacity: 0;
}
</style>
