<template>
  <header class="platform-global-header">
    <div class="platform-global-header__left">
      <button class="platform-brand" type="button" @click="$emit('go-home')">
        <img :src="logoSrc" alt="TestHub" class="platform-brand__logo" />
        <div class="platform-brand__content">
          <span class="platform-brand__name">TestHub</span>
          <span class="platform-brand__tagline">智能测试平台</span>
        </div>
      </button>

      <nav class="platform-module-nav" aria-label="平台模块切换">
        <button
          v-for="item in topLevelItems"
          :key="item.key"
          type="button"
          class="platform-module-nav__item"
          :class="{
            'is-active': item.key === currentModuleKey,
            'is-disabled': !item.route
          }"
          :disabled="!item.route"
          @click="$emit('navigate-module', item)"
        >
          {{ item.title }}
        </button>
      </nav>

      <button
        v-if="showProjectContext"
        type="button"
        class="platform-context-trigger"
        @click="$emit('open-placeholder', 'project-context')"
      >
        <el-icon><FolderOpened /></el-icon>
        <span>{{ projectContextLabel }}</span>
      </button>
    </div>

    <div class="platform-global-header__right">
      <button
        type="button"
        class="platform-tool-button"
        :title="searchLabel"
        @click="$emit('open-global-search')"
      >
        <el-icon><Search /></el-icon>
      </button>
      <button
        type="button"
        class="platform-tool-button"
        :title="recentLabel"
        @click="$emit('toggle-productivity-panel', 'recent-visits')"
      >
        <el-icon><Clock /></el-icon>
      </button>
      <button
        type="button"
        class="platform-tool-button"
        :title="favoriteLabel"
        @click="$emit('toggle-productivity-panel', 'favorites')"
      >
        <el-icon><Star /></el-icon>
      </button>
      <button
        type="button"
        class="platform-tool-button"
        :title="notificationLabel"
        @click="$emit('open-placeholder', 'notifications')"
      >
        <el-icon><Bell /></el-icon>
      </button>
      <button
        type="button"
        class="platform-tool-button is-ai"
        :title="assistantLabel"
        @click="$emit('open-assistant')"
      >
        <el-icon><MagicStick /></el-icon>
      </button>

      <el-dropdown class="platform-language-dropdown" @command="$emit('language-change', $event)">
        <button type="button" class="platform-language-trigger">
          <span class="platform-language-trigger__flag">{{ languageCode === 'zh-cn' ? 'CN' : 'EN' }}</span>
          <span>{{ languageLabel }}</span>
          <el-icon><ArrowDown /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="zh-cn" :disabled="languageCode === 'zh-cn'">简体中文</el-dropdown-item>
            <el-dropdown-item command="en" :disabled="languageCode === 'en'">English</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <el-dropdown class="platform-user-dropdown" @command="$emit('user-command', $event)">
        <button type="button" class="platform-user-trigger">
          <el-avatar :size="34" :src="user?.avatar">{{ fallbackInitial }}</el-avatar>
          <div class="platform-user-trigger__content">
            <span class="platform-user-trigger__name">{{ user?.username || anonymousLabel }}</span>
            <span class="platform-user-trigger__role">{{ userRoleLabel }}</span>
          </div>
          <el-icon><ArrowDown /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">{{ profileLabel }}</el-dropdown-item>
            <el-dropdown-item divided command="logout">{{ logoutLabel }}</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import {
  ArrowDown,
  Bell,
  Clock,
  FolderOpened,
  MagicStick,
  Search,
  Star
} from '@element-plus/icons-vue'

const props = defineProps({
  logoSrc: {
    type: String,
    default: ''
  },
  topLevelItems: {
    type: Array,
    default: () => []
  },
  currentModuleKey: {
    type: String,
    default: ''
  },
  showProjectContext: {
    type: Boolean,
    default: false
  },
  languageCode: {
    type: String,
    default: 'zh-cn'
  },
  languageLabel: {
    type: String,
    default: ''
  },
  user: {
    type: Object,
    default: null
  }
})

defineEmits([
  'go-home',
  'navigate-module',
  'open-placeholder',
  'open-global-search',
  'toggle-productivity-panel',
  'open-assistant',
  'language-change',
  'user-command'
])

const isChinese = computed(() => props.languageCode === 'zh-cn')
const projectContextLabel = computed(() => (isChinese.value ? '项目上下文（阶段 1 占位）' : 'Project context (Stage 1 placeholder)'))
const searchLabel = computed(() => (isChinese.value ? '全局搜索' : 'Global search'))
const recentLabel = computed(() => (isChinese.value ? '最近访问' : 'Recent visits'))
const favoriteLabel = computed(() => (isChinese.value ? '收藏入口' : 'Favorites'))
const notificationLabel = computed(() => (isChinese.value ? '消息通知（阶段 1 占位）' : 'Notifications (Stage 1 placeholder)'))
const assistantLabel = computed(() => (isChinese.value ? 'AI 助手' : 'AI Assistant'))
const anonymousLabel = computed(() => (isChinese.value ? '未登录用户' : 'Anonymous'))
const userRoleLabel = computed(() => (isChinese.value ? '平台成员' : 'Platform member'))
const profileLabel = computed(() => (isChinese.value ? '个人资料' : 'Profile'))
const logoutLabel = computed(() => (isChinese.value ? '退出登录' : 'Logout'))
const fallbackInitial = computed(() => props.user?.username?.slice(0, 1)?.toUpperCase() || 'T')
</script>

<style scoped lang="scss">
.platform-global-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 72px;
  padding: 14px 24px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  background: linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%);
}

.platform-global-header__left,
.platform-global-header__right {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.platform-global-header__left {
  flex: 1;
}

.platform-global-header__right {
  flex-shrink: 0;
}

.platform-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.platform-brand__logo {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  object-fit: cover;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.14);
}

.platform-brand__content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.platform-brand__name {
  font-size: 16px;
  font-weight: 700;
  line-height: 1.1;
  color: #0f172a;
}

.platform-brand__tagline {
  font-size: 12px;
  color: #64748b;
}

.platform-module-nav {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  overflow-x: auto;
  padding-bottom: 2px;
}

.platform-module-nav__item,
.platform-context-trigger,
.platform-tool-button,
.platform-language-trigger,
.platform-user-trigger {
  border: none;
  background: transparent;
}

.platform-module-nav__item {
  flex-shrink: 0;
  padding: 9px 14px;
  border-radius: 999px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
}

.platform-module-nav__item:hover:not(.is-disabled),
.platform-module-nav__item.is-active {
  background: #e2e8f0;
  color: #0f172a;
}

.platform-module-nav__item.is-active {
  font-weight: 700;
}

.platform-module-nav__item.is-disabled {
  color: #94a3b8;
  cursor: not-allowed;
}

.platform-context-trigger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  padding: 9px 12px;
  border-radius: 12px;
  background: #eef2ff;
  color: #334155;
  cursor: pointer;
}

.platform-tool-button,
.platform-language-trigger,
.platform-user-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
}

.platform-tool-button {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #f8fafc;
  color: #334155;
  transition: all 0.2s ease;
}

.platform-tool-button:hover,
.platform-language-trigger:hover,
.platform-user-trigger:hover,
.platform-context-trigger:hover {
  background: #e2e8f0;
}

.platform-tool-button.is-ai {
  background: #ecfeff;
  color: #0f766e;
}

.platform-language-trigger {
  padding: 8px 12px;
  border-radius: 12px;
  color: #334155;
}

.platform-language-trigger__flag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 22px;
  padding: 0 6px;
  border-radius: 999px;
  background: #e2e8f0;
  font-size: 11px;
  font-weight: 700;
}

.platform-user-trigger {
  padding: 4px 10px 4px 4px;
  border-radius: 16px;
  color: #0f172a;
}

.platform-user-trigger__content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.15;
}

.platform-user-trigger__name {
  font-weight: 700;
}

.platform-user-trigger__role {
  font-size: 12px;
  color: #64748b;
}

@media (max-width: 1360px) {
  .platform-brand__content,
  .platform-module-nav,
  .platform-user-trigger__role {
    display: none;
  }
}

@media (max-width: 960px) {
  .platform-context-trigger,
  .platform-language-trigger span,
  .platform-user-trigger__content {
    display: none;
  }

  .platform-global-header {
    padding: 12px 16px;
  }
}
</style>
