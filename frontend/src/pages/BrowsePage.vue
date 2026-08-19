<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from 'vue'
import {
  ExclamationTriangleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'
import { useRoute, useRouter } from 'vue-router'

import ProjectBrowseRow from '../components/ProjectBrowseRow.vue'
import { useProjectDirectory } from '../composables/useProjectDirectory'

import SearchFilter from '../components/SearchFilter.vue'

type SortOption = 'newest' | 'oldest' | 'name'

const sortBy = ref<SortOption>('newest')
const route = useRoute()
const router = useRouter()
let searchTimer: ReturnType<typeof setTimeout> | undefined

const {
  query,
  projectTypeFilter,
  labelFilter,
  loading,
  error,
  projectTypes,
  labels,
  projects,
  clearFilters,
  loadProjects,
  loadDirectory,
} = useProjectDirectory()

function getQueryValue(value: unknown) {
  return typeof value === 'string' ? value : ''
}

query.value = getQueryValue(route.query.q)
projectTypeFilter.value = getQueryValue(route.query.projectType)
labelFilter.value = getQueryValue(route.query.label)

const activeFilterLabel = computed(
  () => projectTypeFilter.value || labelFilter.value,
)

const visibleProjects = computed(() =>
  projects.value.toSorted((a, b) => {
    if (sortBy.value === 'name') {
      return a.name.localeCompare(b.name)
    }

    const direction = sortBy.value === 'oldest' ? 1 : -1
    return (
      (new Date(a.created_at).getTime() - new Date(b.created_at).getTime()) *
      direction
    )
  }),
)

const resultLabel = computed(() => {
  const count = visibleProjects.value.length
  return `${count} ${count === 1 ? 'result' : 'results'}`
})

const resultsHeading = computed(() => {
  const normalizedQuery = query.value.trim()

  if (normalizedQuery && activeFilterLabel.value) {
    return `${activeFilterLabel.value} matching “${normalizedQuery}”`
  }

  if (normalizedQuery) {
    return `Results for “${normalizedQuery}”`
  }

  return activeFilterLabel.value || 'All projects'
})

watch([query, projectTypeFilter, labelFilter], () => {
  if (searchTimer !== undefined) clearTimeout(searchTimer)

  void router.replace({
    path: '/browse',
    query: {
      ...(query.value.trim() ? { q: query.value.trim() } : {}),
      ...(projectTypeFilter.value
        ? { projectType: projectTypeFilter.value }
        : {}),
      ...(labelFilter.value ? { label: labelFilter.value } : {}),
    },
  })

  searchTimer = setTimeout(() => {
    void loadProjects()
  }, 250)
})

onMounted(() => {
  void loadDirectory()
})

onBeforeUnmount(() => {
  if (searchTimer !== undefined) clearTimeout(searchTimer)
})
</script>

<template>
  <main class="mx-auto max-w-[1120px] px-5 py-10 pb-24 sm:px-8">
    <!-- SearchFilter -->
    <SearchFilter
      v-model:query="query"
      v-model:project-type-filter="projectTypeFilter"
      v-model:label-filter="labelFilter"
      placeholder="Search projects, maintainers, and keywords…"
      :project-types="projectTypes"
      :labels="labels"
    />

    <div
      v-if="error"
      class="mt-9 flex items-center gap-2 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]"
    >
      <ExclamationTriangleIcon class="size-4 shrink-0" />
      {{ error }}
    </div>

    <div
      v-else-if="loading"
      class="mt-12 space-y-3"
      aria-label="Loading projects"
    >
      <div
        v-for="item in 5"
        :key="item"
        class="h-[112px] animate-pulse rounded-xl border-b border-[var(--border)] bg-gradient-to-r from-[var(--surface)] to-transparent"
      />
    </div>

    <section
      v-else
      class="mt-9 min-w-0"
      aria-labelledby="results-heading"
    >
      <div
        class="flex flex-col items-start gap-2 border-b border-[var(--border)] pb-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4"
      >
        <h2
          id="results-heading"
          class="min-w-0 break-words font-display text-[18px] font-semibold tracking-[-0.015em] text-[var(--text)]"
        >
          {{ resultsHeading }}
          <span class="font-normal text-[var(--muted)]">· {{ resultLabel }}</span>
        </h2>

        <label class="flex shrink-0 items-center gap-2">
          <span class="hidden font-mono text-[10px] text-[var(--faint)] sm:inline">Sort</span>
          <select
            v-model="sortBy"
            class="rounded-lg border border-transparent bg-transparent py-1 pl-2 pr-1 text-xs text-[var(--muted)] outline-none transition hover:border-[var(--border)] focus:border-[var(--accent)]"
          >
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
            <option value="name">Name</option>
          </select>
        </label>
      </div>

      <div v-if="visibleProjects.length">
        <ProjectBrowseRow
          v-for="project in visibleProjects"
          :key="project.id"
          :project="project"
        />
      </div>

      <div
        v-else
        class="rounded-b-xl border-b border-[var(--border)] px-6 py-16 text-center"
      >
        <p class="font-display text-base font-semibold text-[var(--text)]">
          No projects found
        </p>
        <p class="mt-2 text-sm text-[var(--muted)]">
          Try another keyword or clear the active filters.
        </p>
        <button
          type="button"
          class="mt-5 inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-sm text-[var(--muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text)]"
          @click="clearFilters"
        >
          <XMarkIcon class="size-4" />
          Clear filters
        </button>
      </div>
    </section>
  </main>
</template>
