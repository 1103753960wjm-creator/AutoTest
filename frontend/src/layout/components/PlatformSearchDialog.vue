<template>
  <el-dialog
    :model-value="modelValue"
    width="760px"
    top="10vh"
    destroy-on-close
    append-to-body
    :show-close="false"
    class="platform-search-dialog"
    @close="emit('update:modelValue', false)"
  >
    <template #header>
      <div class="platform-search-dialog__header">
        <div>
          <h3 class="platform-search-dialog__title">全局搜索</h3>
          <p class="platform-search-dialog__description">第一版优先搜索页面、菜单、入口和少量低风险资产。</p>
        </div>
        <div class="platform-search-dialog__shortcut">
          <span>Ctrl / Cmd + K</span>
          <span>打开</span>
        </div>
      </div>
    </template>

    <div class="platform-search-dialog__body">
      <el-input
        ref="inputRef"
        :model-value="query"
        placeholder="搜索页面、入口、项目或测试用例"
        size="large"
        clearable
        @input="emit('update:query', $event)"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <div class="platform-search-dialog__hint">
        <span>Enter 打开</span>
        <span>↑ ↓ 切换</span>
        <span>Esc 关闭</span>
      </div>

      <StateLoading
        v-if="loading && !flattenedResults.length"
        compact
        title="正在整理搜索结果"
        description="页面 / 菜单结果会即时返回，轻资产结果在关键字达到最小长度后补充。"
      />

      <StateEmpty
        v-else-if="!flattenedResults.length"
        compact
        title="暂无匹配结果"
        description="可以先搜索页面或模块入口；轻资产搜索会在输入至少 2 个字符后触发。"
      />

      <div v-else class="platform-search-dialog__groups">
        <div v-if="loading" class="platform-search-dialog__loading-inline">
          轻资产结果补充加载中…
        </div>
        <section
          v-for="group in groups"
          :key="group.key"
          class="platform-search-dialog__group"
        >
          <div class="platform-search-dialog__group-title">{{ group.label }}</div>
          <button
            v-for="item in group.items"
            :key="item.id"
            type="button"
            class="platform-search-dialog__item"
            :class="{ 'is-active': item.id === activeResultId }"
            @mouseenter="activeResultId = item.id"
            @click="emit('navigate', item)"
          >
            <div class="platform-search-dialog__item-main">
              <span class="platform-search-dialog__item-title">{{ item.title }}</span>
              <p class="platform-search-dialog__item-description">
                {{ item.description || item.summary || item.route }}
              </p>
            </div>
            <div class="platform-search-dialog__item-meta">
              <span v-if="item.moduleLabel" class="platform-search-dialog__tag">{{ item.moduleLabel }}</span>
              <span v-if="item.pageTypeLabel" class="platform-search-dialog__tag is-muted">{{ item.pageTypeLabel }}</span>
              <span v-if="item.type === 'recent'" class="platform-search-dialog__tag is-soft">最近访问</span>
              <span v-if="item.type === 'project'" class="platform-search-dialog__tag is-soft">项目</span>
              <span v-if="item.type === 'testcase'" class="platform-search-dialog__tag is-soft">测试用例</span>
            </div>
          </button>
        </section>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { StateEmpty, StateLoading } from '@/components/ui-states'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  query: {
    type: String,
    default: ''
  },
  groups: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'update:query', 'navigate', 'open'])

const inputRef = ref()
const activeResultId = ref('')

const flattenedResults = computed(() => {
  return props.groups.flatMap((group) => group.items || [])
})

const focusInput = async () => {
  await nextTick()
  inputRef.value?.focus?.()
}

const syncActiveResult = () => {
  if (!flattenedResults.value.length) {
    activeResultId.value = ''
    return
  }

  if (!flattenedResults.value.some((item) => item.id === activeResultId.value)) {
    activeResultId.value = flattenedResults.value[0].id
  }
}

const moveSelection = (direction) => {
  if (!flattenedResults.value.length) {
    return
  }

  const currentIndex = flattenedResults.value.findIndex((item) => item.id === activeResultId.value)
  const nextIndex = currentIndex === -1
    ? 0
    : (currentIndex + direction + flattenedResults.value.length) % flattenedResults.value.length

  activeResultId.value = flattenedResults.value[nextIndex].id
}

const handleGlobalKeydown = async (event) => {
  const isOpenShortcut = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k'

  if (isOpenShortcut) {
    event.preventDefault()

    if (!props.modelValue) {
      emit('open')
      await focusInput()
    }

    return
  }

  if (!props.modelValue || event.isComposing) {
    return
  }

  if (event.key === 'Escape') {
    event.preventDefault()
    emit('update:modelValue', false)
    return
  }

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    moveSelection(1)
    return
  }

  if (event.key === 'ArrowUp') {
    event.preventDefault()
    moveSelection(-1)
    return
  }

  if (event.key === 'Enter') {
    const activeItem = flattenedResults.value.find((item) => item.id === activeResultId.value)

    if (activeItem) {
      event.preventDefault()
      emit('navigate', activeItem)
    }
  }
}

watch(() => props.modelValue, async (value) => {
  if (value) {
    syncActiveResult()
    await focusInput()
    return
  }

  activeResultId.value = ''
})

watch(flattenedResults, () => {
  syncActiveResult()
})

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<style scoped lang="scss">
.platform-search-dialog :deep(.el-dialog) {
  border-radius: 24px;
  overflow: hidden;
}

.platform-search-dialog :deep(.el-dialog__header) {
  margin: 0;
  padding: 22px 24px 0;
}

.platform-search-dialog :deep(.el-dialog__body) {
  padding: 18px 24px 24px;
}

.platform-search-dialog__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.platform-search-dialog__title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
}

.platform-search-dialog__description {
  margin: 6px 0 0;
  color: #64748b;
  line-height: 1.7;
}

.platform-search-dialog__shortcut {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: #f8fafc;
  color: #475569;
  font-size: 12px;
}

.platform-search-dialog__body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.platform-search-dialog__hint {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #64748b;
  font-size: 12px;
}

.platform-search-dialog__groups {
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-height: 60vh;
  overflow: auto;
}

.platform-search-dialog__loading-inline {
  font-size: 12px;
  color: #64748b;
}

.platform-search-dialog__group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.platform-search-dialog__group-title {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}

.platform-search-dialog__item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  padding: 14px 16px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 16px;
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition: all 0.18s ease;
}

.platform-search-dialog__item:hover,
.platform-search-dialog__item.is-active {
  border-color: rgba(59, 130, 246, 0.32);
  background: #f8fbff;
  box-shadow: 0 12px 30px rgba(59, 130, 246, 0.08);
}

.platform-search-dialog__item-main {
  min-width: 0;
}

.platform-search-dialog__item-title {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.platform-search-dialog__item-description {
  margin: 6px 0 0;
  color: #64748b;
  line-height: 1.6;
}

.platform-search-dialog__item-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  min-width: 120px;
}

.platform-search-dialog__tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 12px;
  white-space: nowrap;
}

.platform-search-dialog__tag.is-muted {
  background: #f1f5f9;
  color: #475569;
}

.platform-search-dialog__tag.is-soft {
  background: #ecfeff;
  color: #0f766e;
}

@media (max-width: 768px) {
  .platform-search-dialog :deep(.el-dialog) {
    width: calc(100vw - 24px) !important;
  }

  .platform-search-dialog__header,
  .platform-search-dialog__item {
    flex-direction: column;
  }

  .platform-search-dialog__item-meta {
    justify-content: flex-start;
    min-width: 0;
  }
}
</style>
