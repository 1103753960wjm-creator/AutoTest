<template>
  <div class="configuration-center">
    <div class="content-area">
      <router-view v-slot="{ Component, route: currentRoute }">
        <transition name="fade" mode="out-in">
          <!-- 与 layout/index.vue 保持一致的 key 策略，按路由名称或路径区分实例 -->
          <component :is="Component" :key="currentRoute.name || currentRoute.path" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
// 配置中心子页面每个都有唯一的 name，不需要额外的 key 计算逻辑
</script>

<style scoped>
.configuration-center {
  height: 100%;
  width: 100%;
}

.content-area {
  height: 100%;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
