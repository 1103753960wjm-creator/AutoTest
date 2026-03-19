<template>
  <component
    :is="tagName"
    class="quick-action-card"
    :class="[variantClass, accentClass, { 'is-clickable': clickable, 'is-disabled': disabled }]"
    :type="tagName === 'button' ? 'button' : undefined"
    @click="handleClick"
  >
    <div v-if="resolvedIcon" class="quick-action-card__icon">
      <el-icon><component :is="resolvedIcon" /></el-icon>
    </div>
    <div class="quick-action-card__body">
      <div class="quick-action-card__title-row">
        <h3 class="quick-action-card__title">{{ title }}</h3>
        <span v-if="badge" class="quick-action-card__badge">{{ badge }}</span>
      </div>
      <p v-if="description" class="quick-action-card__description">{{ description }}</p>
      <div v-if="$slots.default" class="quick-action-card__extra">
        <slot />
      </div>
    </div>
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  badge: {
    type: String,
    default: ''
  },
  icon: {
    type: [Object, Function],
    default: null
  },
  accent: {
    type: String,
    default: 'blue'
  },
  variant: {
    type: String,
    default: 'default'
  },
  clickable: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const tagName = computed(() => (props.clickable ? 'button' : 'div'))
const resolvedIcon = computed(() => props.icon || null)
const variantClass = computed(() => `is-${props.variant}`)
const accentClass = computed(() => `accent-${props.accent}`)

const handleClick = () => {
  if (!props.clickable || props.disabled) {
    return
  }

  emit('click')
}
</script>

<style scoped lang="scss">
.quick-action-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  min-height: 160px;
  padding: 22px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.94) 100%),
    radial-gradient(circle at top right, rgba(56, 189, 248, 0.12), transparent 42%);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
  color: inherit;
  text-align: left;
  cursor: default;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.quick-action-card.is-default {
  min-height: 210px;
}

.quick-action-card.is-compact {
  min-height: 128px;
  padding: 18px;
  border-radius: 20px;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
}

.quick-action-card.is-clickable {
  cursor: pointer;
}

.quick-action-card.is-clickable:hover {
  transform: translateY(-4px);
  border-color: rgba(59, 130, 246, 0.24);
  box-shadow: 0 22px 48px rgba(15, 23, 42, 0.12);
}

.quick-action-card.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quick-action-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  border-radius: 18px;
  background: rgba(226, 232, 240, 0.7);
  color: #0f172a;
  font-size: 26px;
}

.quick-action-card.is-compact .quick-action-card__icon {
  width: 46px;
  height: 46px;
  font-size: 22px;
}

.quick-action-card.accent-blue .quick-action-card__icon {
  background: rgba(59, 130, 246, 0.16);
  color: #1d4ed8;
}

.quick-action-card.accent-green .quick-action-card__icon {
  background: rgba(16, 185, 129, 0.16);
  color: #047857;
}

.quick-action-card.accent-purple .quick-action-card__icon {
  background: rgba(124, 58, 237, 0.16);
  color: #6d28d9;
}

.quick-action-card.accent-cyan .quick-action-card__icon {
  background: rgba(6, 182, 212, 0.16);
  color: #0f766e;
}

.quick-action-card.accent-orange .quick-action-card__icon {
  background: rgba(249, 115, 22, 0.16);
  color: #c2410c;
}

.quick-action-card.accent-pink .quick-action-card__icon {
  background: rgba(244, 114, 182, 0.16);
  color: #be185d;
}

.quick-action-card.accent-slate .quick-action-card__icon {
  background: rgba(100, 116, 139, 0.16);
  color: #334155;
}

.quick-action-card__body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.quick-action-card__title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.quick-action-card__title {
  margin: 0;
  font-size: 20px;
  color: #0f172a;
}

.quick-action-card.is-compact .quick-action-card__title {
  font-size: 16px;
}

.quick-action-card__badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 12px;
  font-weight: 700;
}

.quick-action-card__description {
  margin: 0;
  color: #475569;
  line-height: 1.7;
}

.quick-action-card.is-compact .quick-action-card__description {
  font-size: 13px;
  line-height: 1.6;
}

.quick-action-card__extra {
  margin-top: auto;
}

@media (max-width: 768px) {
  .quick-action-card {
    min-height: 150px;
    padding: 18px;
  }

  .quick-action-card.is-default {
    min-height: 180px;
  }
}
</style>
