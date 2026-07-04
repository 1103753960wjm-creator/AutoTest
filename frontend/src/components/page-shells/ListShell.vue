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
  gap: var(--th-space-20);
  min-height: 100%;
}

.shell-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--th-space-16);
}

.shell-heading {
  min-width: 0;
}

.shell-eyebrow {
  margin-bottom: var(--th-space-8);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--th-color-primary);
}

.shell-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--th-text-primary);
}

.shell-description {
  margin: 10px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--th-text-secondary);
}

.shell-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--th-space-12);
}

.shell-toolbar-card,
.shell-content-card {
  border: 1px solid var(--th-border-color);
  border-radius: var(--th-radius-lg);
  box-shadow: var(--th-shadow-card);
}

.shell-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--th-space-12);
  margin-bottom: var(--th-space-16);
}

.shell-toolbar:last-child {
  margin-bottom: 0;
}

.shell-filters {
  display: flex;
  flex-direction: column;
  gap: var(--th-space-12);
}

.shell-filters :deep(.el-row) {
  width: 100%;
}

.shell-filters :deep(.el-input),
.shell-filters :deep(.el-select),
.shell-filters :deep(.el-date-editor) {
  width: 100%;
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
