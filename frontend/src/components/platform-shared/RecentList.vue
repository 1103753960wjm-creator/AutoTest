<template>
  <el-card shadow="hover" class="recent-list-card">
    <template #header>
      <div class="recent-list-card__header">
        <div class="recent-list-card__heading">
          <slot name="header">
            <span class="recent-list-card__title">{{ title }}</span>
            <span v-if="description" class="recent-list-card__description">{{ description }}</span>
          </slot>
        </div>
        <div v-if="$slots.actions" class="recent-list-card__actions">
          <slot name="actions" />
        </div>
      </div>
    </template>

    <StateLoading
      v-if="loading"
      compact
      :title="loadingTitle"
      :description="loadingDescription"
    />
    <StateError
      v-else-if="error"
      compact
      :title="errorTitle"
      :description="errorDescription"
      :primary-action-text="errorActionText"
      @primary-action="emit('retry')"
    />
    <StateEmpty
      v-else-if="!items.length"
      compact
      :title="emptyTitle"
      :description="emptyDescription"
    />
    <div v-else class="recent-list-card__list">
      <slot
        v-for="(item, index) in items"
        :key="resolveItemKey(item, index)"
        name="item"
        :item="item"
        :index="index"
      />
    </div>
  </el-card>
</template>

<script setup>
import { StateEmpty, StateError, StateLoading } from '@/components/ui-states'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  items: {
    type: Array,
    default: () => []
  },
  itemKey: {
    type: [String, Function],
    default: 'id'
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: Boolean,
    default: false
  },
  loadingTitle: {
    type: String,
    default: '加载中'
  },
  loadingDescription: {
    type: String,
    default: ''
  },
  emptyTitle: {
    type: String,
    default: '暂无数据'
  },
  emptyDescription: {
    type: String,
    default: ''
  },
  errorTitle: {
    type: String,
    default: '加载失败'
  },
  errorDescription: {
    type: String,
    default: ''
  },
  errorActionText: {
    type: String,
    default: '重试'
  }
})

const emit = defineEmits(['retry'])

const resolveItemKey = (item, index) => {
  if (typeof props.itemKey === 'function') {
    return props.itemKey(item, index)
  }

  return item?.[props.itemKey] ?? index
}
</script>

<style scoped lang="scss">
.recent-list-card {
  height: 100%;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
}

.recent-list-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.recent-list-card__heading {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recent-list-card__title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.recent-list-card__description {
  font-size: 13px;
  color: #64748b;
}

.recent-list-card__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.recent-list-card__list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
</style>
