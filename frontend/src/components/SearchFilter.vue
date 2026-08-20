<script setup lang="ts">
import { computed } from 'vue'
import SearchBar from './SearchBar.vue'

type FilterKind = 'projectType' | 'label'

type FilterChip = {
  kind: FilterKind
  name: string
}

const props = defineProps<{
  projectTypes: string[]
  labels: string[]
  placeholder: string
}>()

const query = defineModel<string>('query', { required: true })

const projectTypeFilter = defineModel<string>(
  'projectTypeFilter',
  { required: true },
)

const labelFilter = defineModel<string>(
  'labelFilter',
  { required: true },
)

const filterChips = computed<FilterChip[]>(() => [
  ...props.projectTypes.map((name) => ({
    kind: 'projectType' as const,
    name,
  })),
  ...props.labels
    .filter((name) => !props.projectTypes.includes(name))
    .map((name) => ({
      kind: 'label' as const,
      name,
    })),
])

const activeFilterLabel = computed(
  () => projectTypeFilter.value || labelFilter.value,
)

function selectFilter(filter: FilterChip) {
  if (filter.kind === 'projectType') {
    projectTypeFilter.value = filter.name
    labelFilter.value = ''
  } else {
    labelFilter.value = filter.name
    projectTypeFilter.value = ''
  }
}

function clearFacetFilters() {
  projectTypeFilter.value = ''
  labelFilter.value = ''
}
</script>

<template>
  <section
    class="min-w-0 max-w-full"
    aria-label="Search and filter projects"
  >
    <SearchBar
      v-model="query"
      :placeholder="placeholder"
    />

    <fieldset
      v-if="filterChips.length"
      class="mt-4 min-w-0 max-w-full"
    >
      <legend class="sr-only">
        Filter projects
      </legend>

      <div
        class="flex w-full max-w-full gap-2 overflow-x-auto overscroll-x-contain pb-2 sm:flex-wrap"
      >
        <button
          type="button"
          class="shrink-0 cursor-pointer rounded-full border px-3.5 py-1.5 text-[12px] transition"
          :class="!activeFilterLabel
            ? 'border-[var(--accent)] bg-[var(--accent-soft)] font-medium text-[var(--accent-ink)]'
            : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted)] hover:border-[var(--border-strong)] hover:text-[var(--text)]'"
          :aria-pressed="!activeFilterLabel"
          @click="clearFacetFilters"
        >
          All
        </button>

        <button
          v-for="filter in filterChips"
          :key="`${filter.kind}:${filter.name}`"
          type="button"
          class="shrink-0 cursor-pointer rounded-full border px-3.5 py-1.5 text-[12px] transition"
          :class="activeFilterLabel === filter.name
            ? 'border-[var(--accent)] bg-[var(--accent-soft)] font-medium text-[var(--accent-ink)]'
            : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted)] hover:border-[var(--border-strong)] hover:text-[var(--text)]'"
          :aria-pressed="activeFilterLabel === filter.name"
          @click="selectFilter(filter)"
        >
          {{ filter.name }}
        </button>
      </div>
    </fieldset>
  </section>
</template>
