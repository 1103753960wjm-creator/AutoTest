<template>
  <div class="platform-productivity-panel">
    <div class="platform-productivity-panel__header">
      <div>
        <h4 class="platform-productivity-panel__title">{{ title }}</h4>
        <p v-if="description" class="platform-productivity-panel__description">{{ description }}</p>
      </div>
      <el-button v-if="showClear" text type="primary" @click="$emit('clear')">{{ clearText }}</el-button>
    </div>

    <StateEmpty
      v-if="!items.length"
      compact
      :title="emptyTitle"
      :description="emptyDescription"
    />

    <div v-else class="platform-productivity-panel__list">
      <div
        v-for="item in items"
        :key="item.id || item.fullPath"
        class="platform-productivity-panel__item"
      >
        <button type="button" class="platform-productivity-panel__link" @click="$emit('navigate', item)">
          <span class="platform-productivity-panel__item-title">{{ item.title }}</span>
          <span class="platform-productivity-panel__item-summary">{{ item.summary }}</span>
        </button>
        <div class="platform-productivity-panel__meta">
          <span>{{ resolveTimeText(item) }}</span>
          <el-button
            v-if="showFavoriteAction"
            text
            type="warning"
            @click="$emit('toggle-favorite', item)"
          >
            {{ favoriteActionText }}
          </el-button>
          <el-button
            v-if="showRemoveAction"
            text
            type="danger"
            @click="$emit('remove', item)"
          >
            {{ removeActionText }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { StateEmpty } from '@/components/ui-states'

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
  emptyTitle: {
    type: String,
    default: '暂无记录'
  },
  emptyDescription: {
    type: String,
    default: ''
  },
  showClear: {
    type: Boolean,
    default: false
  },
  clearText: {
    type: String,
    default: '清空'
  },
  showFavoriteAction: {
    type: Boolean,
    default: false
  },
  favoriteActionText: {
    type: String,
    default: '收藏'
  },
  showRemoveAction: {
    type: Boolean,
    default: false
  },
  removeActionText: {
    type: String,
    default: '移除'
  }
})

defineEmits(['navigate', 'toggle-favorite', 'clear', 'remove'])

const resolveTimeText = (item) => {
  const raw = item.visitedAt || item.createdAt || ''

  if (!raw) {
    return ''
  }

  const date = new Date(raw)

  if (Number.isNaN(date.getTime())) {
    return raw
  }

  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped lang="scss">
.platform-productivity-panel {
  width: 320px;
}

.platform-productivity-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.platform-productivity-panel__title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.platform-productivity-panel__description {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.6;
  color: #64748b;
}

.platform-productivity-panel__list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: min(60vh, 480px);
  overflow-y: auto;
  padding-right: 4px;
}

.platform-productivity-panel__item {
  padding: 10px 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
}

.platform-productivity-panel__item:last-child {
  border-bottom: none;
}

.platform-productivity-panel__link {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  padding: 0;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.platform-productivity-panel__item-title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.platform-productivity-panel__item-summary {
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
}

.platform-productivity-panel__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}
</style>
