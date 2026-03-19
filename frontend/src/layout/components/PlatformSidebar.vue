<template>
  <aside class="platform-sidebar" :class="{ 'is-collapsed': collapsed }">
    <div class="platform-sidebar__header">
      <div class="platform-sidebar__module">
        <span class="platform-sidebar__module-label">当前模块</span>
        <strong class="platform-sidebar__module-title">{{ collapsed ? moduleInitial : moduleTitle }}</strong>
      </div>
      <button type="button" class="platform-sidebar__toggle" @click="$emit('toggle-collapse')">
        <el-icon><component :is="collapsed ? Expand : Fold" /></el-icon>
      </button>
    </div>

    <el-scrollbar class="platform-sidebar__scrollbar">
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :collapse-transition="false"
        class="platform-sidebar__menu"
        @select="handleSelect"
      >
        <el-menu-item
          v-for="item in items"
          :key="item.key"
          :index="item.path || item.key"
          :disabled="!item.path"
        >
          <el-icon v-if="item.iconComponent"><component :is="item.iconComponent" /></el-icon>
          <el-icon v-else><Menu /></el-icon>
          <template #title>
            <div class="platform-sidebar__menu-title">
              <span>{{ item.title }}</span>
              <span v-if="item.status === futureMoveStatus && !collapsed" class="platform-sidebar__tag">迁移中</span>
              <span v-if="item.status === reservedStatus && !collapsed" class="platform-sidebar__tag is-muted">预留</span>
            </div>
          </template>
        </el-menu-item>
      </el-menu>
    </el-scrollbar>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { Expand, Fold, Menu } from '@element-plus/icons-vue'
import { NAV_ENTRY_STATUS } from '@/config/navigation'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  },
  moduleTitle: {
    type: String,
    default: ''
  },
  items: {
    type: Array,
    default: () => []
  },
  activeMenu: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['toggle-collapse', 'navigate'])

const futureMoveStatus = NAV_ENTRY_STATUS.FUTURE_MOVE
const reservedStatus = NAV_ENTRY_STATUS.RESERVED
const moduleInitial = computed(() => props.moduleTitle.slice(0, 2) || '模块')

const handleSelect = (index) => {
  const target = props.items.find((item) => (item.path || item.key) === index)
  if (target?.path) {
    emit('navigate', target)
  }
}
</script>

<style scoped lang="scss">
.platform-sidebar {
  display: flex;
  flex-direction: column;
  width: 272px;
  min-width: 272px;
  border-right: 1px solid rgba(15, 23, 42, 0.08);
  background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
  transition: width 0.2s ease, min-width 0.2s ease;
}

.platform-sidebar.is-collapsed {
  width: 84px;
  min-width: 84px;
}

.platform-sidebar__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 16px 14px;
}

.platform-sidebar__module {
  min-width: 0;
}

.platform-sidebar__module-label {
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
  color: #64748b;
}

.platform-sidebar__module-title {
  display: block;
  color: #0f172a;
  font-size: 16px;
  font-weight: 700;
}

.platform-sidebar__toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 12px;
  background: #ffffff;
  color: #334155;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.platform-sidebar__scrollbar {
  flex: 1;
  min-height: 0;
}

.platform-sidebar__menu {
  border-right: none;
  background: transparent;
  padding: 4px 10px 16px;
}

.platform-sidebar__menu :deep(.el-menu-item),
.platform-sidebar__menu :deep(.el-sub-menu__title) {
  height: 46px;
  margin-bottom: 6px;
  border-radius: 14px;
  color: #334155;
}

.platform-sidebar__menu :deep(.el-menu-item.is-active) {
  background: #dbeafe;
  color: #1d4ed8;
}

.platform-sidebar__menu-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
}

.platform-sidebar__tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 7px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 11px;
}

.platform-sidebar__tag.is-muted {
  background: #e2e8f0;
  color: #64748b;
}

.platform-sidebar.is-collapsed .platform-sidebar__header {
  flex-direction: column;
}

.platform-sidebar.is-collapsed .platform-sidebar__module-label,
.platform-sidebar.is-collapsed .platform-sidebar__tag {
  display: none;
}
</style>
