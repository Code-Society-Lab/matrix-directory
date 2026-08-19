<script setup lang="ts">
import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  useId,
} from 'vue'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const query = defineModel<string>({ required: true })

const props = withDefaults(
  defineProps<{
    placeholder?: string
    label?: string
    enableShortcut?: boolean
  }>(),
  {
    placeholder: 'Search projects…',
    label: 'Search projects',
    enableShortcut: true,
  },
)

const searchInput = ref<HTMLInputElement | null>(null)
const inputId = useId()

function clearSearch() {
  query.value = ''
  void nextTick(() => searchInput.value?.focus())
}

function handleShortcut(event: KeyboardEvent) {
  const target = event.target as HTMLElement | null
  const isTyping =
    target?.tagName === 'INPUT' ||
    target?.tagName === 'TEXTAREA' ||
    target?.isContentEditable

  if (event.key === '/' && !isTyping) {
    event.preventDefault()
    searchInput.value?.focus()
  }
}

onMounted(() => {
  if (props.enableShortcut) {
    window.addEventListener('keydown', handleShortcut)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleShortcut)
})
</script>

<template>
  <div class="relative block">
    <label
      :for="inputId"
      class="sr-only"
    >
      {{ label }}
    </label>

    <MagnifyingGlassIcon
      class="pointer-events-none absolute left-4 top-1/2 size-[18px] -translate-y-1/2 text-[var(--faint)]"
    />

    <input
      :id="inputId"
      ref="searchInput"
      v-model="query"
      type="search"
      :placeholder="placeholder"
      class="h-[58px] w-full rounded-[13px] border border-[var(--border-strong)] bg-[var(--surface)] pl-12 pr-20 text-[14px] text-[var(--text)] outline-none transition placeholder:text-[var(--faint)] focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)] sm:text-[15px]"
    >

    <button
      v-if="query"
      type="button"
      class="absolute right-4 top-1/2 -translate-y-1/2 rounded-md px-2 py-1 text-xs text-[var(--muted)] transition hover:bg-[var(--sunk)] hover:text-[var(--text)]"
      @click="clearSearch"
    >
      Clear
    </button>
  </div>
</template>
