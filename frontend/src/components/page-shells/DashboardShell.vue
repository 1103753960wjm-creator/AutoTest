<template>
  <div class="dashboard-shell">
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

    <section v-if="slots.metrics" class="shell-metrics">
      <slot name="metrics" />
    </section>

    <section v-if="slots.overview" class="shell-overview">
      <slot name="overview" />
    </section>

    <div class="shell-body" :class="{ 'has-secondary': hasSecondary }">
      <section class="shell-main">
        <slot />
      </section>
      <aside v-if="hasSecondary" class="shell-secondary">
        <slot name="secondary" />
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

const hasSecondary = computed(() => Boolean(slots.secondary))
</script>

<style scoped lang="scss">
.dashboard-shell {
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
  padding: 24px;
  border-radius: 18px;
  background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
  border: 1px solid #e8eef5;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
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

.shell-metrics,
.shell-overview,
.shell-main,
.shell-secondary,
.shell-footer {
  min-width: 0;
}

.shell-body {
  display: grid;
  gap: 20px;
  grid-template-columns: minmax(0, 1fr);
}

.shell-body.has-secondary {
  grid-template-columns: minmax(0, 1.6fr) minmax(300px, 0.9fr);
}

@media (max-width: 1200px) {
  .shell-body.has-secondary {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 768px) {
  .shell-header {
    padding: 20px;
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
