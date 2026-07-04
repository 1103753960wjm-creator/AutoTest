import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { ElLoading } from 'element-plus'
import 'element-plus/es/components/loading/style/css'
import 'element-plus/es/components/message/style/css'
import 'element-plus/es/components/message-box/style/css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import i18n from './locales'

import App from './App.vue'
import router from './router'
import './assets/css/global.scss'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)

async function init() {
  try {
    const userStore = useUserStore()
    await userStore.initAuth()
  } catch (error) {
    // 获取用户信息失败，说明未登录，无需处理
  }

  // 注册所有图标
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.use(router)
  app.use(i18n)

  // 页面组件改为按需引入，仅保留全局 loading 指令
  app.use(ElLoading)

  app.mount('#app')
}

init()
