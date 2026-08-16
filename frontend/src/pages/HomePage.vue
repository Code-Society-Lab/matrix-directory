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
const category = ref('')
const loading = ref(true)
const error = ref('')

const botCount = computed(() => projects.value.length)

const categories = computed(() =>
  [
    ...new Set(
      projects.value.flatMap((project) =>
        project.categories.map((item) => item.name),
      ),
    ),
  ].sort(),
)

const visibleProjects = computed(() => {
  const normalizedQuery = query.value.trim().toLowerCase()

  return projects.value.filter((project) => {
    const matchesQuery =
      !normalizedQuery ||
      [
        project.name,
        project.short_description,
        project.description,
      ]
        .join(' ')
        .toLowerCase()
        .includes(normalizedQuery)

    const matchesCategory =
      !category.value ||
      project.categories.some(
        (item) => item.name === category.value,
      )

    return matchesQuery && matchesCategory
  })
})

const hasFilters = computed(
  () => Boolean(query.value.trim()) || Boolean(category.value),
)

function selectCategory(value: string) {
  category.value = category.value === value ? '' : value
}

function clearFilters() {
  query.value = ''
  category.value = ''
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
        : 'Could not load bots.'
  } finally {
    loading.value = false
  }
}

onMounted(loadProjects)
</script>

<template>
  <main
    class="mx-auto max-w-[1120px] px-5 pb-24 sm:px-8"
  >
    <!-- Hero -->
    <section class="max-w-[760px] pb-10 pt-16 sm:pt-18">
      <p
        class="font-mono text-xs font-medium uppercase tracking-[0.08em] text-[var(--accent-ink)]"
      >
        Open directory · {{ botCount }}
        {{ botCount === 1 ? 'bot' : 'bots' }}
      </p>

      <h1
        class="mt-4 max-w-[750px] font-display text-[42px] font-semibold leading-[1.06] tracking-[-0.035em] text-[var(--text)] sm:text-[52px]"
      >
        Find a bot for your Matrix room.
      </h1>

      <p
        class="mt-5 max-w-[580px] text-[16px] leading-7 text-[var(--muted)] sm:text-[17px]"
      >
        Discover bridges, moderation tools, games, and assistants
        listed by the people who build them.
      </p>
    </section>

    <!-- Search -->
    <section>
      <div
        class="flex items-center gap-3 rounded-[14px] border border-[var(--border-strong)] bg-[var(--surface)] p-1.5 pl-4 shadow-[var(--shadow)]"
      >
        <MagnifyingGlassIcon
          class="size-5 shrink-0 text-[var(--faint)]"
        />

        <label class="min-w-0 flex-1">
          <span class="sr-only">
            Search bots
          </span>

          <input
            v-model="query"
            type="search"
            placeholder="Search bots, bridges, keywords…"
            class="w-full border-0 bg-transparent py-3 text-[16px] text-[var(--text)] outline-none placeholder:text-[var(--faint)]"
          >
        </label>

        <button
          v-if="query"
          type="button"
          aria-label="Clear search"
          class="grid size-9 shrink-0 place-items-center rounded-lg text-[var(--faint)] transition hover:bg-[var(--sunk)] hover:text-[var(--text)]"
          @click="query = ''"
        >
          <XMarkIcon class="size-4" />
        </button>
      </div>

      <!-- Categories -->
      <div
        v-if="categories.length"
        class="mt-4 flex flex-wrap gap-2"
      >
        <button
          type="button"
          class="rounded-full border px-3.5 py-1.5 text-[13px] transition"
          :class="
            !category
              ? 'border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent-ink)]'
              : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted)] hover:border-[var(--accent)] hover:text-[var(--accent-ink)]'
          "
          @click="category = ''"
        >
          All
        </button>

        <button
          v-for="item in categories"
          :key="item"
          type="button"
          class="rounded-full border px-3.5 py-1.5 text-[13px] transition"
          :class="
            category === item
              ? 'border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent-ink)]'
              : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted)] hover:border-[var(--accent)] hover:text-[var(--accent-ink)]'
          "
          @click="selectCategory(item)"
        >
          {{ item }}
        </button>
      </div>
    </section>

    <!-- Error -->
    <div
      v-if="error"
      class="mt-8 flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      <ExclamationTriangleIcon class="size-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Loading -->
    <div
      v-else-if="loading"
      class="mt-12 font-mono text-xs text-[var(--faint)]"
    >
      Loading bots…
    </div>

    <!-- Results -->
    <template v-else-if="visibleProjects.length">
      <section class="mt-16">
        <!-- Section heading -->
        <div
          class="flex items-end justify-between gap-4 border-b border-[var(--border)] pb-3"
        >
          <div>
            <h2
              class="font-display text-[22px] font-semibold tracking-[-0.01em] text-[var(--text)]"
            >
              {{ hasFilters ? 'Search results' : 'Explore bots' }}
            </h2>
          </div>

          <span
            class="font-mono text-[11.5px] text-[var(--faint)]"
          >
            {{ visibleProjects.length }}
            {{
              visibleProjects.length === 1
                ? 'listing'
                : 'listings'
            }}
          </span>
        </div>

        <!-- Cards -->
        <div
          class="mt-5 grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3"
        >
          <BotCard
            v-for="project in visibleProjects"
            :key="project.id"
            :project="project"
          />
        </div>
      </section>

      <!-- Recently added -->
      <section
        v-if="!hasFilters"
        class="mt-16"
      >
        <div
          class="flex items-end justify-between gap-4 border-b border-[var(--border)] pb-3"
        >
          <h2
            class="font-display text-[22px] font-semibold tracking-[-0.01em] text-[var(--text)]"
          >
            Recently added
          </h2>

          <span
            class="font-mono text-[11.5px] text-[var(--faint)]"
          >
            newest listings first
          </span>
        </div>

        <div
          class="mt-5 rounded-[14px] border border-dashed border-[var(--border-strong)] bg-[var(--surface)] px-6 py-10 text-center"
        >
          <p
            class="font-display text-sm font-semibold text-[var(--text)]"
          >
            Recent listings are coming soon
          </p>

          <p
            class="mx-auto mt-2 max-w-sm text-[13.5px] leading-5 text-[var(--muted)]"
          >
            Once listing dates are exposed by the API, the newest
            additions to the directory will appear here.
          </p>
        </div>
      </section>
    </template>

    <!-- Empty -->
    <div
      v-else
      class="mt-12 rounded-[14px] border border-dashed border-[var(--border-strong)] bg-[var(--surface)] px-6 py-14 text-center"
    >
      <p
        class="font-display text-[15px] font-semibold text-[var(--text)]"
      >
        Nothing matched that
      </p>

      <p class="mt-2 text-sm text-[var(--muted)]">
        Try a shorter keyword or another category.
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
