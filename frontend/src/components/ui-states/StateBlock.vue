<template>
  <section class="state-block" :class="[`state-${tone}`, { 'is-compact': compact }]">
    <div class="state-icon">
      <slot name="icon" />
    </div>

    <div class="state-body">
      <h3 class="state-title">{{ title }}</h3>
      <p v-if="description" class="state-description">{{ description }}</p>
      <div v-if="hasActions" class="state-actions">
        <slot name="actions">
          <el-button
            v-if="primaryActionText"
            :type="primaryActionType"
            :plain="primaryActionPlain"
            @click="handlePrimaryAction"
          >
            {{ primaryActionText }}
          </el-button>
          <el-button
            v-if="secondaryActionText"
            :type="secondaryActionType"
            :plain="secondaryActionPlain"
            @click="handleSecondaryAction"
          >
            {{ secondaryActionText }}
          </el-button>
        </slot>
      </div>
      <div v-if="$slots.default" class="state-extra">
        <slot />
      </div>
    </div>
  </section>
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
  tone: {
    type: String,
    default: 'default'
  },
  compact: {
    type: Boolean,
    default: false
  },
  primaryActionText: {
    type: String,
    default: ''
  },
  secondaryActionText: {
    type: String,
    default: ''
  },
  primaryActionType: {
    type: String,
    default: 'primary'
  },
  secondaryActionType: {
    type: String,
    default: 'default'
  },
  primaryActionPlain: {
    type: Boolean,
    default: false
  },
  secondaryActionPlain: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['primary-action', 'secondary-action'])
const slots = useSlots()

const hasActions = computed(() => {
  return Boolean(
    props.primaryActionText ||
    props.secondaryActionText ||
    slots.actions
  )
})

const handlePrimaryAction = () => {
  emit('primary-action')
}

const handleSecondaryAction = () => {
  emit('secondary-action')
}
</script>

<style scoped lang="scss">
.state-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  min-height: 320px;
  padding: 40px 24px;
  border: 1px dashed #dbe5f0;
  border-radius: 20px;
  background:
    radial-gradient(circle at top, rgba(64, 158, 255, 0.08), transparent 45%),
    linear-gradient(180deg, #fbfdff 0%, #f5f8fc 100%);
  text-align: center;
}

.state-block.is-compact {
  min-height: 220px;
  padding: 28px 20px;
  border-radius: 18px;
}

.state-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: 999px;
  background: rgba(64, 158, 255, 0.12);
  color: #409eff;
  font-size: 34px;
}

.state-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  max-width: 480px;
}

.state-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #1f2d3d;
}

.state-description {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: #606266;
}

.state-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 6px;
}

.state-extra {
  width: 100%;
}

.state-error .state-icon {
  background: rgba(245, 108, 108, 0.14);
  color: #f56c6c;
}

.state-forbidden .state-icon {
  background: rgba(230, 162, 60, 0.16);
  color: #e6a23c;
}

.state-empty .state-icon,
.state-search-empty .state-icon {
  background: rgba(144, 147, 153, 0.14);
  color: #909399;
}

.state-loading .state-icon {
  background: rgba(64, 158, 255, 0.12);
  color: #409eff;
}

@media (max-width: 768px) {
  .state-block {
    min-height: 280px;
    padding: 32px 18px;
  }

  .state-title {
    font-size: 20px;
  }
}
</style>

