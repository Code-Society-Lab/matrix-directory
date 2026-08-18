<script setup lang="ts">
import { MilkdownProvider } from '@milkdown/vue'

import MarkdownEditorInner from './MarkdownEditorInner.vue'

withDefaults(
  defineProps<{
    modelValue: string
    maxlength?: number
    placeholder?: string
    ariaLabel?: string
  }>(),
  {
    maxlength: undefined,
    placeholder: 'Write a description…',
    ariaLabel: 'Markdown editor',
  },
)

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <MilkdownProvider>
    <MarkdownEditorInner
      :model-value="modelValue"
      :maxlength="maxlength"
      :placeholder="placeholder"
      :aria-label="ariaLabel"
      @update:model-value="$emit('update:modelValue', $event)"
    />
  </MilkdownProvider>
</template>
