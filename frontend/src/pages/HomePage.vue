<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'

import { listProjects } from '../api/client'
import BotCard from '../components/BotCard.vue'
import type { ProjectListItem } from '../types/project'

const projects = ref<ProjectListItem[]>([])
const query = ref('')
const projectTypeFilter = ref('')
const labelFilter = ref('')
const loading = ref(true)
const error = ref('')

const projectCount = computed(() => projects.value.length)

const projectTypes = computed(() =>
  [...new Set(projects.value.map((project) => project.project_type.name))].sort(),
)

const labels = computed(() =>
  [
    ...new Set(
      projects.value.flatMap((project) =>
        project.labels.map((item) => item.name),
      ),
    ),
  ].sort(),
)

const latestProjects = computed(() =>
  projects.value
    .toSorted(
      (a, b) =>
        new Date(b.created_at).getTime() -
        new Date(a.created_at).getTime(),
    )
    .slice(0, 10),
)

function formatProjectDate(date: string) {
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    year: 'numeric',
  }).format(new Date(date))
}

const visibleProjects = computed(() => {
  const normalizedQuery = query.value.trim().toLowerCase()

  return projects.value.filter((project) => {
    const matchesQuery =
      !normalizedQuery ||
      [
        project.name,
        project.short_description,
        project.description,
        project.project_type.name,
        ...project.labels.map((item) => item.name),
      ]
        .join(' ')
        .toLowerCase()
        .includes(normalizedQuery)

    const matchesProjectType =
      !projectTypeFilter.value ||
      project.project_type.name === projectTypeFilter.value

    const matchesLabel =
      !labelFilter.value ||
      project.labels.some((item) => item.name === labelFilter.value)

    return matchesQuery && matchesProjectType && matchesLabel
  })
})

const hasFilters = computed(
  () =>
    Boolean(query.value.trim()) ||
    Boolean(projectTypeFilter.value) ||
    Boolean(labelFilter.value),
)

function selectProjectType(value: string) {
  projectTypeFilter.value = projectTypeFilter.value === value ? '' : value
}

function selectLabel(value: string) {
  labelFilter.value = labelFilter.value === value ? '' : value
}

function clearFilters() {
  query.value = ''
  projectTypeFilter.value = ''
  labelFilter.value = ''
}

async function loadProjects() {
  loading.value = true
  error.value = ''

  try {
    projects.value = await listProjects()
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not load projects.'
  } finally {
    loading.value = false
  }
}

onMounted(loadProjects)
</script>

<template>
  <main class="mx-auto max-w-[1120px] px-5 pb-24 sm:px-8">
    <!-- Hero -->
    <section class="max-w-[860px] pb-8 pt-10 sm:pb-8 sm:pt-14">
      <p class="font-mono text-xs font-medium uppercase tracking-[0.08em] text-[var(--accent-ink)]">
        Open directory · {{ projectCount }}
        {{ projectCount === 1 ? 'project' : 'projects' }}
      </p>

      <h1
        class="
          mt-4 max-w-[850px]
          font-display text-[36px] font-semibold
          leading-[1.08] tracking-[-0.035em]
          text-[var(--text)]
          sm:text-[52px] sm:leading-[1.06]
        "
      >
        Find tools for Matrix.
      </h1>

      <p
        class="
          mt-4 max-w-[680px]
          text-[15px] leading-6 text-[var(--muted)]
          sm:mt-5 sm:text-[17px] sm:leading-7
        "
      >
        Discover bots, bridges, frameworks, and tools built by the Matrix community.
      </p>
    </section>

    <!-- Search and filters -->
    <section>
      <!-- Search -->
      <label class="relative block">
        <span class="sr-only">Search directory</span>

        <MagnifyingGlassIcon
          class="
            pointer-events-none absolute left-3.5 top-1/2 size-4
            -translate-y-1/2 text-[var(--faint)]
          "
        />

        <input
          v-model="query"
          type="search"
          placeholder="Search projects…"
          class="
            h-11 w-full rounded-[10px]
            border border-[var(--border-strong)]
            bg-[var(--surface)]
            pl-10 pr-4
            text-[14px] text-[var(--text)]
            outline-none transition
            placeholder:text-[var(--faint)]
            focus:border-[var(--accent)]
            focus:ring-3 focus:ring-[var(--accent-soft)]
            sm:h-12 sm:text-[15px]
          "
        >
      </label>

      <!-- Filters -->
      <div class="mt-4 space-y-4 sm:space-y-2.5">
        <!-- Project types -->
        <fieldset
          v-if="projectTypes.length"
          class="
            grid gap-2
            sm:grid-cols-[68px_minmax(0,1fr)]
            sm:items-center
          "
        >
          <legend class="sr-only">
            Project type
          </legend>

          <span
            class="
              font-mono text-[9px] font-medium uppercase
              tracking-[0.08em] text-[var(--faint)]
            "
          >
            Type
          </span>

          <div
            class="
              -mx-5 flex gap-2 overflow-x-auto
              px-5 pb-1
              [scrollbar-width:none]
              [&::-webkit-scrollbar]:hidden
              sm:mx-0 sm:flex-wrap sm:overflow-visible sm:px-0 sm:pb-0
            "
          >
            <button
              type="button"
              class="
                shrink-0 rounded-full border
                px-3 py-1.5
                text-[12.5px] transition
              "
              :class="!projectTypeFilter
                ? 'border-[var(--accent-deep)] bg-[var(--accent-soft)] font-medium text-[var(--accent-ink)]'
                : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted)] hover:border-[var(--border-strong)] hover:text-[var(--text)]'
              "
              @click="projectTypeFilter = ''"
            >
              All
            </button>

            <button
              v-for="item in projectTypes"
              :key="item"
              type="button"
              class="
                shrink-0 rounded-full border
                px-3 py-1.5
                text-[12.5px] transition
              "
              :class="projectTypeFilter === item
                ? 'border-[var(--accent)] bg-[var(--surface)] font-medium text-[var(--accent-ink)]'
                : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted)] hover:border-[var(--border-strong)] hover:text-[var(--text)]'
              "
              @click="selectProjectType(item)"
            >
              {{ item }}
            </button>
          </div>
        </fieldset>

        <!-- Categories -->
        <fieldset
          v-if="labels.length"
          class="
            grid gap-2
            sm:grid-cols-[68px_minmax(0,1fr)]
            sm:items-center
          "
        >
          <legend class="sr-only">
            Category
          </legend>

          <span
            class="
              font-mono text-[9px] font-medium uppercase
              tracking-[0.08em] text-[var(--faint)]
            "
          >
            Category
          </span>

          <div
            class="
              -mx-5 flex gap-2 overflow-x-auto
              px-5 pb-1
              [scrollbar-width:none]
              [&::-webkit-scrollbar]:hidden
              sm:mx-0 sm:flex-wrap sm:overflow-visible sm:px-0 sm:pb-0
            "
          >
            <button
              type="button"
              class="
                shrink-0 rounded-full border
                px-3 py-1.5
                text-[12.5px] transition
              "
              :class="!labelFilter
                ? 'border-[var(--accent-deep)] bg-[var(--accent-soft)] font-medium text-[var(--accent-ink)]'
                : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted)] hover:border-[var(--border-strong)] hover:text-[var(--text)]'
              "
              @click="labelFilter = ''"
            >
              All
            </button>

            <button
              v-for="item in labels"
              :key="item"
              type="button"
              class="
                shrink-0 rounded-full border
                px-3 py-1.5
                text-[12.5px] transition
              "
              :class="labelFilter === item
                ? 'border-[var(--accent)] bg-[var(--surface)] font-medium text-[var(--accent-ink)]'
                : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted)] hover:border-[var(--border-strong)] hover:text-[var(--text)]'
              "
              @click="selectLabel(item)"
            >
              {{ item }}
            </button>
          </div>
        </fieldset>
      </div>

      <!-- Active filters -->
      <div
        v-if="hasFilters"
        class="mt-4 flex items-center gap-3"
      >
        <span class="font-mono text-[10px] text-[var(--faint)]">
          {{ visibleProjects.length }}
          {{ visibleProjects.length === 1 ? 'result' : 'results' }}
        </span>

        <button
          type="button"
          class="
            inline-flex items-center gap-1
            text-[12px] text-[var(--muted)]
            transition hover:text-[var(--text)]
          "
          @click="clearFilters"
        >
          <XMarkIcon class="size-3.5" />
          Clear filters
        </button>
      </div>
    </section>

    <!-- Error -->
    <div
      v-if="error"
      class="mt-8 flex items-center gap-2 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]"
    >
      <ExclamationTriangleIcon class="size-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Loading -->
    <div
      v-else-if="loading"
      class="mt-12 font-mono text-xs text-[var(--faint)]"
    >
      Loading projects…
    </div>

    <!-- Results -->
    <template v-else-if="visibleProjects.length">
      <section class="mt-8 sm:mt-12">
        <!-- Section heading -->
        <div class="flex items-end justify-between gap-4 border-b border-[var(--border)] pb-3">
          <div>
            <h2
              class="
                font-display text-[20px] font-semibold
                tracking-[-0.01em] text-[var(--text)]
                sm:text-[22px]
              "
            >
              {{ hasFilters ? 'Search results' : 'Explore projects' }}
            </h2>
          </div>

          <span class="font-mono text-[11.5px] text-[var(--faint)]">
            {{ visibleProjects.length }}
            {{
              visibleProjects.length === 1
                ? 'listing'
                : 'listings'
            }}
          </span>
        </div>

        <!-- Cards -->
        <div class="mt-5 grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          <BotCard
            v-for="project in visibleProjects"
            :key="project.id"
            :project="project"
          />
        </div>
      </section>

      <!-- Recently added -->
      <section
        v-if="!hasFilters && latestProjects.length"
        class="mt-12 sm:mt-16"
      >
        <div class="flex items-end justify-between gap-4 border-b border-[var(--border)] pb-3">
          <h2 class="font-display text-[22px] font-semibold tracking-[-0.01em] text-[var(--text)]">
            Recently added
          </h2>

          <span class="font-mono text-[11.5px] text-[var(--faint)]">
            newest listings first
          </span>
        </div>

        <div class="mt-5">
          <RouterLink
            v-for="project in latestProjects"
            :key="project.id"
            :to="`/bots/${project.id}`"
            class="
              group flex min-h-[66px] items-center gap-4
              rounded-b-[10px]
              border-b border-[var(--border)]
              px-2 py-3
              transition
              hover:bg-[var(--surface)]
              sm:px-3
            "
          >
            <!-- Initial -->
            <div
              class="grid size-11 shrink-0 place-items-center rounded-xl bg-[var(--sunk)] font-display text-[15px] font-semibold text-[var(--muted)]"
            >
              {{ project.name.charAt(0).toUpperCase() }}
            </div>

            <!-- Name / description -->
            <div class="min-w-0 flex-1 sm:flex sm:items-baseline sm:gap-3">
              <h3 class="shrink-0 font-display text-[15px] font-semibold text-[var(--text)]">
                {{ project.name }}
              </h3>

              <p class="mt-1 truncate text-[13.5px] text-[var(--muted)] sm:mt-0">
                {{ project.short_description }}
              </p>
            </div>

            <!-- Project type -->
            <span
              class="hidden shrink-0 rounded-lg bg-[var(--sunk)] px-2.5 py-1 text-[12px] text-[var(--muted)] md:inline-block"
            >
              {{ project.project_type.name }}
            </span>

            <!-- Date -->
            <time
              :datetime="project.created_at"
              class="hidden w-[72px] shrink-0 text-right font-mono text-[11.5px] text-[var(--faint)] sm:block"
            >
              {{ formatProjectDate(project.created_at) }}
            </time>
          </RouterLink>
        </div>
      </section>
    </template>

    <!-- Empty -->
    <div
      v-else
      class="mt-12 rounded-[14px] border border-dashed border-[var(--border-strong)] bg-[var(--surface)] px-6 py-14 text-center"
    >
      <p class="font-display text-[15px] font-semibold text-[var(--text)]">
        Nothing matched that
      </p>

      <p class="mt-2 text-sm text-[var(--muted)]">
        Try a shorter keyword or different filters.
      </p>

      <button
        v-if="hasFilters"
        type="button"
        class="mt-5 rounded-[9px] border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm text-[var(--muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text)]"
        @click="clearFilters"
      >
        Clear filters
      </button>
    </div>
  </main>
</template>
