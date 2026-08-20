<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ExclamationTriangleIcon,
  PlusIcon,
} from '@heroicons/vue/24/outline'

import { deleteProject, listMyProjects } from '../api/client'
import type { ProjectListItem } from '../types/project'
import { projectPath } from '../utils/projectRoutes'
import ProjectActions from '../components/ProjectActions.vue'

const projects = ref<ProjectListItem[]>([])
const loading = ref(true)
const error = ref('')

const projectCount = computed(() => projects.value.length)

function formatUpdatedAt(date: string) {
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(date))
}

async function load() {
  loading.value = true
  error.value = ''

  try {
    projects.value = await listMyProjects()
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not load your projects.'
  } finally {
    loading.value = false
  }
}

async function remove(project: ProjectListItem) {
  if (!window.confirm(`Delete ${project.name} from the directory?`)) {
    return
  }

  try {
    await deleteProject(project.id)

    projects.value = projects.value.filter(
      (item) => item.id !== project.id,
    )
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not delete the project.'
  }
}

onMounted(() => {
  load()
})
</script>

<template>
  <main class="mx-auto max-w-[1120px] px-5 py-10 pb-24 sm:px-8">
    <!-- Header -->
    <div class="flex flex-wrap items-end justify-between gap-6">
      <div class="max-w-2xl">
        <p
          class="font-mono text-xs font-medium uppercase tracking-[0.08em] text-[var(--accent-ink)]"
        >
          Dashboard
        </p>

        <h1
          class="mt-3 font-display text-[34px] font-semibold tracking-[-0.02em] text-[var(--text)]"
        >
          My Projects
        </h1>

        <p class="mt-2 text-[15px] leading-6 text-[var(--muted)]">
          Manage the projects you've published to the directory.
        </p>
      </div>

      <RouterLink
        to="/submit"
        class="inline-flex items-center gap-2 rounded-[9px] bg-[var(--accent)] px-4 py-2.5 text-sm font-medium text-[#0e1012] no-underline transition hover:bg-[var(--accent-deep)]"
      >
        <PlusIcon class="size-4" />
        Add project
      </RouterLink>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="mt-8 flex items-center gap-2 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]"
    >
      <ExclamationTriangleIcon class="size-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Loading -->
    <p
      v-if="loading"
      class="mt-8 font-mono text-xs text-[var(--faint)]"
    >
      Loading projects...
    </p>

    <template v-else>
      <!-- Section header -->
      <div
        class="mt-10 flex items-baseline justify-between gap-4 border-b border-[var(--border)] pb-3"
      >
        <h2
          class="font-display text-xl font-semibold tracking-[-0.01em] text-[var(--text)]"
        >
          Published
        </h2>

        <span class="font-mono text-xs text-[var(--faint)]">
          {{ projectCount }}
          {{ projectCount === 1 ? 'project' : 'projects' }}
        </span>
      </div>

      <!-- Projects -->
      <div
        v-if="projects.length"
        class="mt-3"
      >
        <article
          v-for="project in projects"
          :key="project.id"
          class="group relative flex items-start gap-4 rounded-[10px] border-b border-[var(--border)] px-2 py-4 transition hover:bg-[var(--hover)] sm:items-center"
        >
          <!-- Initial -->
          <RouterLink
            :to="projectPath(project)"
            class="mt-1 grid size-11 shrink-0 place-items-center rounded-[11px] bg-[var(--accent-soft)] font-display text-base font-semibold text-[var(--accent-ink)] no-underline sm:mt-0"
          >
            {{ project.name.charAt(0).toUpperCase() }}
          </RouterLink>

          <!-- Information -->
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-3 pr-20 sm:pr-0">
              <RouterLink
                :to="projectPath(project)"
                class="block min-w-0 flex-1 truncate font-display text-[15px] font-semibold tracking-[-0.01em] text-[var(--text)] no-underline hover:text-[var(--accent-ink)]"
              >
                {{ project.name }}
              </RouterLink>
            </div>

            <p
              class="mt-1 line-clamp-2 max-w-2xl text-[13.5px] leading-5 text-[var(--muted)]"
            >
              {{ project.short_description }}
            </p>

            <div class="mt-2.5 flex flex-wrap items-center gap-1.5">
              <span
                class="rounded-[6px] bg-[var(--accent-soft)] px-2 py-[3px] text-[10.5px] font-medium text-[var(--accent-ink)]"
              >
                {{ project.project_type.name }}
              </span>

              <span
                v-for="label in project.labels.slice(0, 2)"
                :key="label.id"
                class="rounded-[6px] bg-[var(--sunk)] px-2 py-[3px] text-[10.5px] text-[var(--muted)]"
              >
                {{ label.name }}
              </span>

              <span
                v-if="project.labels.length > 2"
                class="rounded-[6px] bg-[var(--sunk)] px-2 py-[3px] font-mono text-[9.5px] text-[var(--faint)]"
              >
                +{{ project.labels.length - 2 }}
              </span>

              <span class="hidden text-[var(--faint)] sm:inline">·</span>

              <time
                :datetime="project.updated_at"
                class="basis-full font-mono text-[10.5px] text-[var(--faint)] sm:basis-auto"
              >
                Updated {{ formatUpdatedAt(project.updated_at) }}
              </time>
            </div>
          </div>

          <ProjectActions
            :project="project"
            @delete="remove(project)"
          />
        </article>
      </div>

      <!-- Empty state -->
      <div
        v-else
        class="mt-6 rounded-[14px] border border-dashed border-[var(--border-strong)] bg-[var(--surface)] px-6 py-14 text-center"
      >
        <div
          class="mx-auto grid size-12 place-items-center rounded-[12px] bg-[var(--accent-soft)] text-[var(--accent-ink)]"
        >
          <PlusIcon class="size-5" />
        </div>

        <h2
          class="mt-4 font-display text-base font-semibold text-[var(--text)]"
        >
          No projects yet
        </h2>

        <p
          class="mx-auto mt-2 max-w-sm text-sm leading-6 text-[var(--muted)]"
        >
          Projects you publish to the Matrix directory will appear here.
        </p>

        <RouterLink
          to="/submit"
          class="mt-5 inline-flex items-center gap-2 rounded-[9px] bg-[var(--accent)] px-4 py-2.5 text-sm font-medium text-[#0e1012] no-underline transition hover:bg-[var(--accent-deep)]"
        >
          <PlusIcon class="size-4" />
          Add your first project
        </RouterLink>
      </div>
    </template>
  </main>
</template>
