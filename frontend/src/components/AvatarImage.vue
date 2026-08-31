<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { initialsFrom } from '../utils/initials'

const props = defineProps<{
  src: string | null | undefined
  name?: string | null
  alt?: string
}>()

const failed = ref(false)

const shouldShowImage = computed(() => Boolean(props.src) && !failed.value)
const initials = computed(() => initialsFrom(props.name))

watch(
  () => props.src,
  () => {
    failed.value = false
  },
)
</script>

<template>
  <img
    v-if="shouldShowImage"
    :src="src ?? undefined"
    :alt="alt ?? ''"
    class="size-full object-cover"
    @error="failed = true"
  >

  <slot v-else>
    <span>{{ initials }}</span>
  </slot>
</template>
