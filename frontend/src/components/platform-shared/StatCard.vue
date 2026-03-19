<template>
  <el-card shadow="hover" class="stat-card" :body-style="{ padding: compact ? '18px' : '20px' }">
    <div class="stat-card__content">
      <div v-if="resolvedIcon" class="stat-card__icon" :class="accentClass">
        <el-icon><component :is="resolvedIcon" /></el-icon>
      </div>
      <div class="stat-card__body">
        <div class="stat-card__label-row">
          <span class="stat-card__label">{{ title }}</span>
          <span v-if="trendText" class="stat-card__trend">{{ trendText }}</span>
        </div>
        <el-skeleton v-if="loading" :rows="1" animated>
          <template #template>
            <el-skeleton-item variant="text" style="width: 76px; height: 30px;" />
          </template>
        </el-skeleton>
        <div v-else class="stat-card__value">{{ value }}</div>
        <p v-if="description" class="stat-card__description">{{ description }}</p>
        <div v-if="$slots.footer" class="stat-card__footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  value: {
    type: [String, Number],
    default: '--'
  },
  description: {
    type: String,
    default: ''
  },
  trendText: {
    type: String,
    default: ''
  },
  accent: {
    type: String,
    default: 'blue'
  },
  icon: {
    type: [Object, Function],
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const resolvedIcon = computed(() => props.icon || null)
const accentClass = computed(() => `is-${props.accent}`)
</script>

<style scoped lang="scss">
.stat-card {
  height: 100%;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
}

.stat-card__content {
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 92px;
}

.stat-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 18px;
  font-size: 24px;
  color: #0f172a;
  background: rgba(226, 232, 240, 0.8);
}

.stat-card__icon.is-blue {
  background: rgba(59, 130, 246, 0.14);
  color: #1d4ed8;
}

.stat-card__icon.is-green {
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
}

.stat-card__icon.is-purple {
  background: rgba(124, 58, 237, 0.14);
  color: #6d28d9;
}

.stat-card__icon.is-orange {
  background: rgba(249, 115, 22, 0.16);
  color: #c2410c;
}

.stat-card__icon.is-cyan {
  background: rgba(6, 182, 212, 0.16);
  color: #0f766e;
}

.stat-card__body {
  flex: 1;
  min-width: 0;
}

.stat-card__label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.stat-card__label {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

.stat-card__trend {
  font-size: 12px;
  color: #94a3b8;
}

.stat-card__value {
  margin-top: 10px;
  font-size: 30px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
}

.stat-card__description {
  margin: 8px 0 0;
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}

.stat-card__footer {
  margin-top: 12px;
}

@media (max-width: 768px) {
  .stat-card__content {
    min-height: auto;
  }

  .stat-card__icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }

  .stat-card__value {
    font-size: 24px;
  }
}
</style>
