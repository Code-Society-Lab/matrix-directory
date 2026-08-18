<script setup lang="ts">
import { MilkdownProvider } from '@milkdown/vue'

import MarkdownContentInner from './MarkdownContentInner.vue'

withDefaults(
  defineProps<{
    source: string
    ariaLabel?: string
  }>(),
  {
    ariaLabel: 'Markdown content',
  },
)
</script>

<template>
  <MilkdownProvider>
    <MarkdownContentInner
      :source="source"
      :aria-label="ariaLabel"
    />
  </MilkdownProvider>
</template>
