<template>
  <section class="filter-bar-block" :class="{ 'has-actions': hasActions, 'has-extra': hasExtra }">
    <div class="filter-bar-block__main">
      <slot />
    </div>
    <div v-if="hasActions" class="filter-bar-block__actions">
      <slot name="actions" />
    </div>
    <div v-if="hasExtra" class="filter-bar-block__extra">
      <slot name="extra" />
    </div>
  </section>
</template>

<script setup>
import { computed, useSlots } from 'vue'

const slots = useSlots()

const hasActions = computed(() => Boolean(slots.actions))
const hasExtra = computed(() => Boolean(slots.extra))
</script>

<style scoped lang="scss">
.filter-bar-block {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
  padding: 18px 20px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.94) 100%);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}

.filter-bar-block__main {
  flex: 1;
  min-width: min(100%, 320px);
}

.filter-bar-block__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-left: auto;
}

.filter-bar-block__extra {
  width: 100%;
}

@media (max-width: 1024px) {
  .filter-bar-block {
    margin-bottom: 12px;
    padding: 16px;
  }

  .filter-bar-block__actions {
    width: 100%;
    justify-content: flex-start;
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .filter-bar-block {
    gap: 12px;
    margin-bottom: 8px;
    padding: 14px;
  }
}

@media (max-width: 480px) {
  .filter-bar-block {
    margin-bottom: 6px;
    padding: 12px;
  }
}
</style>
