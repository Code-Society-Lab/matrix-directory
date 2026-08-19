<script setup lang="ts">
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { countProjects, listProjects, listRandomProjects } from '../api/client'
import ProjectCard from '../components/ProjectCard.vue'
import SearchBar from '../components/SearchBar.vue'
import type { ProjectListItem } from '../types/project'
import { projectPath } from '../utils/projectRoutes'

const router = useRouter()
const projects = ref<ProjectListItem[]>([])
const recentProjects = ref<ProjectListItem[]>([])
const projectCount = ref(0)
const query = ref('')
const loading = ref(true)
const error = ref('')

function formatProjectDate(date: string) {
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    year: 'numeric',
  }).format(new Date(date))
}

async function loadHomepage() {
  loading.value = true
  error.value = ''

  try {
    const [randomProjects, newestProjects, total] = await Promise.all([
      listRandomProjects(6),
      listProjects({ limit: 10 }),
      countProjects(),
    ])

    projects.value = randomProjects
    recentProjects.value = newestProjects
    projectCount.value = total
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : 'Could not load projects.'
  } finally {
    loading.value = false
  }
}

function searchDirectory() {
  const normalizedQuery = query.value.trim()

  void router.push({
    path: '/browse',
    query: normalizedQuery ? { q: normalizedQuery } : {},
  })
}

onMounted(() => void loadHomepage())
</script>

<template>
  <main class="mx-auto max-w-[1120px] px-5 pb-24 sm:px-8">
    <!-- Hero -->
    <section class="max-w-[860px] pb-8 pt-10 sm:pb-8 sm:pt-14">
      <p class="font-mono text-xs font-medium uppercase tracking-[0.08em] text-[var(--accent-ink)]">
        Open directory · {{ projectCount }}
        {{ projectCount === 1 ? 'project' : 'projects' }}
      </p>

      <h1 class="mt-4 max-w-[850px] font-display text-[36px] font-semibold leading-[1.08] tracking-[-0.035em] text-[var(--text)] sm:text-[52px] sm:leading-[1.06]">
        Find tools for Matrix.
      </h1>

      <p class="mt-4 max-w-[680px] text-[15px] leading-6 text-[var(--muted)] sm:mt-5 sm:text-[17px] sm:leading-7">
        Discover bots, bridges, frameworks, and tools built by the Matrix community.
      </p>
    </section>

    <!-- Search -->
    <form
      class="flex items-stretch gap-2"
      role="search"
      @submit.prevent="searchDirectory"
    >
      <SearchBar
        v-model="query"
        class="min-w-0 flex-1"
        label="Search the project directory"
        placeholder="Search projects, maintainers, and keywords…"
      />

      <button
        type="submit"
        class="shrink-0 cursor-pointer rounded-[13px] bg-[var(--accent)] px-5 text-sm font-medium text-[#0e1012] transition hover:bg-[var(--accent-deep)]"
      >
        Search
      </button>
    </form>

    <div
      v-if="error"
      class="mt-8 flex items-center gap-2 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]"
    >
      <ExclamationTriangleIcon class="size-4 shrink-0" />
      {{ error }}
    </div>

    <div
      v-else-if="loading"
      class="mt-12 font-mono text-xs text-[var(--faint)]"
    >
      Loading projects…
    </div>

    <section
      v-else-if="projects.length"
      class="mt-8 sm:mt-12"
      aria-labelledby="discover-heading"
    >
      <!-- Discovery -->
      <div class="flex items-end justify-between gap-4 border-b border-[var(--border)] pb-3">
        <h2
          id="discover-heading"
          class="font-display text-[20px] font-semibold tracking-[-0.01em] text-[var(--text)] sm:text-[22px]"
        >
          Discover projects
        </h2>

        <RouterLink
          to="/browse"
          class="text-sm text-[var(--muted)] no-underline transition hover:text-[var(--text)]"
        >
          Browse all projects
        </RouterLink>
      </div>

      <div class="mt-5 grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
        <ProjectCard
          v-for="project in projects"
          :key="project.id"
          :project="project"
        />
      </div>
    </section>

    <!-- Recently added -->
    <section
      v-if="recentProjects.length"
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
          v-for="project in recentProjects"
          :key="project.id"
          :to="projectPath(project)"
          class="
              group flex min-h-[66px] items-center gap-4
              rounded-b-[10px]
              border-b border-[var(--border)]
              px-2 py-3
              transition
              hover:bg-[var(--hover)]
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

    <!-- Empty -->
    <div
      v-if="!loading && !error && !projects.length && !recentProjects.length"
      class="mt-12 rounded-[14px] border border-dashed border-[var(--border-strong)] bg-[var(--surface)] px-6 py-14 text-center"
    >
      <p class="font-display text-[15px] font-semibold text-[var(--text)]">
        No projects are available yet
      </p>

      <p class="mt-2 text-sm text-[var(--muted)]">
        Check back after projects have been added to the directory.
      </p>
    </div>
  </main>
</template>
