<template>
  <div class="detail-result-shell">
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

    <section v-if="slots.summary" class="shell-summary">
      <slot name="summary" />
    </section>

    <el-card v-if="slots.meta" shadow="never" class="shell-meta-card">
      <slot name="meta" />
    </el-card>

    <div class="shell-body" :class="{ 'has-aside': hasAside }">
      <section class="shell-main">
        <slot />
      </section>
      <aside v-if="hasAside" class="shell-aside">
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
  }
})

const slots = useSlots()

const hasHeader = computed(() => {
  return Boolean(props.title || props.description || props.eyebrow || slots.header || slots.actions)
})

const hasAside = computed(() => Boolean(slots.aside))
</script>

<style scoped lang="scss">
.detail-result-shell {
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

.shell-meta-card {
  border: 1px solid var(--th-border-color);
  border-radius: var(--th-radius-lg);
  box-shadow: var(--th-shadow-card);
}

.shell-body {
  display: grid;
  gap: var(--th-space-20);
  grid-template-columns: minmax(0, 1fr);
}

.shell-body.has-aside {
  grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.9fr);
}

.shell-main,
.shell-aside {
  min-width: 0;
}

@media (max-width: 1200px) {
  .shell-body.has-aside {
    grid-template-columns: minmax(0, 1fr);
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
}
</style>
