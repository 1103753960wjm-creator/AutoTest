<template>
  <StateBlock
    tone="loading"
    :compact="compact"
    :title="resolvedTitle"
    :description="resolvedDescription"
  >
    <template #icon>
      <el-icon class="is-spinning">
        <Loading />
      </el-icon>
    </template>

    <template v-if="$slots.actions" #actions>
      <slot name="actions" />
    </template>
  </StateBlock>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Loading } from '@element-plus/icons-vue'
import StateBlock from './StateBlock.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const { t } = useI18n()

const resolvedTitle = computed(() => props.title || t('common.uiState.loading.title'))
const resolvedDescription = computed(() => props.description || t('common.uiState.loading.description'))
</script>
