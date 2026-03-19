<template>
  <section class="platform-page-header">
    <div v-if="breadcrumbItems.length" class="platform-page-header__top">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item
          v-for="(item, index) in breadcrumbItems"
          :key="`${item.title}-${index}`"
          :to="item.current || !item.to ? undefined : { path: item.to }"
        >
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="platform-page-header__main">
      <div class="platform-page-header__title-group">
        <div v-if="resolvedIcon" class="platform-page-header__icon">
          <el-icon><component :is="resolvedIcon" /></el-icon>
        </div>
        <div class="platform-page-header__content">
          <div class="platform-page-header__meta-row">
            <span v-if="moduleName" class="platform-page-header__module">{{ moduleName }}</span>
            <span v-if="pageTypeLabel" class="platform-page-header__page-type">{{ pageTypeLabel }}</span>
            <el-tag
              v-for="(tag, index) in statusTags"
              :key="`${tag.label || tag.text}-${index}`"
              :type="tag.type || 'info'"
              :effect="tag.effect || 'light'"
              round
              size="small"
            >
              {{ tag.label || tag.text }}
            </el-tag>
          </div>
          <div class="platform-page-header__title-row">
            <h1 class="platform-page-header__title">{{ pageTitle }}</h1>
            <span v-if="updateText" class="platform-page-header__update-text">{{ updateText }}</span>
          </div>
          <p v-if="description" class="platform-page-header__description">{{ description }}</p>
          <div v-if="helperText || metaItems.length" class="platform-page-header__info-row">
            <span
              v-for="(item, index) in metaItems"
              :key="`${resolveMetaItemText(item)}-${index}`"
              class="platform-page-header__info-item"
            >
              <span v-if="item.label" class="platform-page-header__info-label">{{ item.label }}</span>
              <span class="platform-page-header__info-value">{{ resolveMetaItemText(item) }}</span>
            </span>
            <span v-if="helperText" class="platform-page-header__helper-text">{{ helperText }}</span>
          </div>
        </div>
      </div>
      <div v-if="hasActions" class="platform-page-header__actions">
        <el-button
          v-for="(action, index) in actions"
          :key="action.key || `${action.label}-${index}`"
          :type="action.type || 'default'"
          :plain="Boolean(action.plain)"
          :text="Boolean(action.text)"
          :link="Boolean(action.link)"
          :disabled="Boolean(action.disabled)"
          :loading="Boolean(action.loading)"
          @click="handleActionClick(action)"
        >
          <el-icon v-if="action.icon">
            <component :is="action.icon" />
          </el-icon>
          {{ action.label }}
        </el-button>
        <slot name="actions" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, useSlots } from 'vue'

const props = defineProps({
  breadcrumbItems: {
    type: Array,
    default: () => []
  },
  moduleName: {
    type: String,
    default: ''
  },
  pageTypeLabel: {
    type: String,
    default: ''
  },
  pageTitle: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  resolvedIcon: {
    type: [Object, Function],
    default: null
  },
  statusTags: {
    type: Array,
    default: () => []
  },
  updateText: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  metaItems: {
    type: Array,
    default: () => []
  },
  actions: {
    type: Array,
    default: () => []
  }
})

const slots = useSlots()

const hasActions = computed(() => {
  return Boolean(props.actions.length || slots.actions)
})

const resolveMetaItemText = (item) => {
  if (typeof item === 'string') {
    return item
  }

  return item.value || item.text || ''
}

const handleActionClick = (action) => {
  if (typeof action?.onClick === 'function') {
    action.onClick()
  }
}
</script>

<style scoped lang="scss">
.platform-page-header {
  padding: 18px 24px 20px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.platform-page-header__top {
  margin-bottom: 14px;
}

.platform-page-header__main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.platform-page-header__title-group {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  min-width: 0;
}

.platform-page-header__content {
  min-width: 0;
}

.platform-page-header__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 16px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 22px;
}

.platform-page-header__meta-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.platform-page-header__module,
.platform-page-header__page-type {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.platform-page-header__module {
  background: #dbeafe;
  color: #1d4ed8;
}

.platform-page-header__page-type {
  background: #f1f5f9;
  color: #475569;
}

.platform-page-header__title-row {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 12px;
}

.platform-page-header__title {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
}

.platform-page-header__update-text {
  font-size: 13px;
  color: #64748b;
}

.platform-page-header__description {
  margin: 8px 0 0;
  color: #64748b;
  line-height: 1.7;
}

.platform-page-header__info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-top: 12px;
}

.platform-page-header__info-item,
.platform-page-header__helper-text {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #475569;
}

.platform-page-header__info-label {
  color: #94a3b8;
}

.platform-page-header__actions {
  flex-shrink: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 960px) {
  .platform-page-header {
    padding: 16px;
  }

  .platform-page-header__main {
    flex-direction: column;
  }

  .platform-page-header__actions {
    width: 100%;
    justify-content: flex-start;
  }

  .platform-page-header__title {
    font-size: 24px;
  }
}
</style>
