<template>
  <StateBlock
    tone="empty"
    :compact="compact"
    :title="resolvedTitle"
    :description="resolvedDescription"
    :primary-action-text="resolvedPrimaryActionText"
    :secondary-action-text="secondaryActionText"
    :primary-action-type="primaryActionType"
    :secondary-action-type="secondaryActionType"
    :primary-action-plain="primaryActionPlain"
    :secondary-action-plain="secondaryActionPlain"
    @primary-action="handlePrimaryAction"
    @secondary-action="$emit('secondary-action')"
  >
    <template #icon>
      <el-icon>
        <Files />
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
import { Files } from '@element-plus/icons-vue'
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
  actionText: {
    type: String,
    default: ''
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
    default: true
  },
  secondaryActionPlain: {
    type: Boolean,
    default: true
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['action', 'primary-action', 'secondary-action'])

const { t } = useI18n()

const resolvedTitle = computed(() => props.title || t('common.uiState.empty.title'))
const resolvedDescription = computed(() => props.description || t('common.uiState.empty.description'))
const resolvedPrimaryActionText = computed(() => props.actionText || props.primaryActionText)

const handlePrimaryAction = () => {
  emit('action')
  emit('primary-action')
}
</script>
