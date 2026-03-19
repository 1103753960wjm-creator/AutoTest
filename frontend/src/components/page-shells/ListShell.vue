<template>
  <div class="list-shell">
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

    <el-card v-if="slots.toolbar || slots.filters" shadow="never" class="shell-toolbar-card">
      <div v-if="slots.toolbar" class="shell-toolbar">
        <slot name="toolbar" />
      </div>
      <div v-if="slots.filters" class="shell-filters">
        <slot name="filters" />
      </div>
    </el-card>

    <el-card shadow="never" class="shell-content-card">
      <slot />
    </el-card>

    <div v-if="slots.pagination" class="shell-pagination">
      <slot name="pagination" />
    </div>

    <div v-if="slots.dialogs" class="shell-dialogs">
      <slot name="dialogs" />
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
  }
})

const slots = useSlots()

const hasHeader = computed(() => {
  return Boolean(props.title || props.description || props.eyebrow || slots.header || slots.actions)
})
</script>

<style scoped lang="scss">
.list-shell {
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

.shell-toolbar-card,
.shell-content-card {
  border: 1px solid #e8eef5;
  border-radius: 18px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.shell-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.shell-toolbar:last-child {
  margin-bottom: 0;
}

.shell-filters {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shell-pagination {
  display: flex;
  justify-content: flex-end;
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
}
</style>
