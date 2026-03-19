<template>
  <div class="workspace-shell">
    <header v-if="hasHeader" class="shell-header">
      <div class="shell-heading">
        <slot name="header">
          <div v-if="eyebrow" class="shell-eyebrow">{{ eyebrow }}</div>
          <h1 v-if="title" class="shell-title">{{ title }}</h1>
          <p v-if="description" class="shell-description">{{ description }}</p>
        </slot>
      </div>
      <div v-if="slots.actions" class="shell-actions">
        <slot name="actions" />
      </div>
    </header>

    <div class="workspace-grid" :style="gridStyle">
      <aside v-if="slots.sidebar" class="workspace-panel workspace-sidebar">
        <slot name="sidebar" />
      </aside>

      <section class="workspace-panel workspace-main">
        <div v-if="slots.toolbar" class="workspace-toolbar">
          <slot name="toolbar" />
        </div>
        <div class="workspace-content">
          <slot />
        </div>
      </section>

      <aside v-if="slots.aside" class="workspace-panel workspace-aside">
        <slot name="aside" />
      </aside>
    </div>

    <footer v-if="slots.footer" class="shell-footer">
      <slot name="footer" />
    </footer>
  </div>
</template>

<script setup>
import { computed, useSlots } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  eyebrow: {
    type: String,
    default: ''
  },
  sidebarWidth: {
    type: String,
    default: '320px'
  },
  asideWidth: {
    type: String,
    default: ''
  }
})

const slots = useSlots()

const hasHeader = computed(() => {
  return Boolean(props.title || props.description || props.eyebrow || slots.header || slots.actions)
})

const gridStyle = computed(() => {
  const columns = []

  if (slots.sidebar) {
    columns.push(`minmax(260px, ${props.sidebarWidth})`)
  }

  columns.push('minmax(0, 1fr)')

  if (slots.aside) {
    columns.push(props.asideWidth ? `minmax(280px, ${props.asideWidth})` : 'minmax(280px, 360px)')
  }

  return {
    gridTemplateColumns: columns.join(' ')
  }
})
</script>

<style scoped lang="scss">
.workspace-shell {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 100%;
}

.shell-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.shell-heading {
  min-width: 0;
}

.shell-eyebrow {
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: #409eff;
}

.shell-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #1f2d3d;
}

.shell-description {
  margin: 10px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: #606266;
}

.shell-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.workspace-grid {
  display: grid;
  gap: 20px;
  min-height: 640px;
}

.workspace-panel {
  min-width: 0;
  min-height: 0;
  padding: 20px;
  border: 1px solid #e8eef5;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.workspace-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.workspace-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eef2f7;
}

.workspace-content {
  min-height: 0;
  flex: 1;
}

@media (max-width: 1200px) {
  .workspace-grid {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}

@media (max-width: 768px) {
  .shell-header {
    flex-direction: column;
  }

  .shell-title {
    font-size: 24px;
  }

  .shell-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .workspace-panel {
    padding: 16px;
  }
}
</style>
