<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ExclamationTriangleIcon,
  PlusIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'

import { deleteProject, listMyProjects } from '../api/client'
import type { ProjectListItem } from '../types/project'

const projects = ref<ProjectListItem[]>([])
const loading = ref(true)
const error = ref('')

const listingCount = computed(() => projects.value.length)

async function load() {
  loading.value = true
  error.value = ''

  try {
    projects.value = await listMyProjects()
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not load your listings.'
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
        : 'Could not delete the listing.'
  }
}

onMounted(load)
</script>

<template>
  <main class="mx-auto max-w-[1120px] px-5 py-10 sm:px-8">
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
          My listings
        </h1>

        <p class="mt-2 text-[15px] leading-6 text-[var(--muted)]">
          Manage the bots and projects you've published to the directory.
        </p>
      </div>

      <button
        type="button"
        disabled
        class="inline-flex cursor-not-allowed items-center gap-2 rounded-[9px] bg-[var(--accent)] px-4 py-2.5 text-sm font-medium text-[#0e1012] opacity-50"
        title="Coming soon"
      >
        <PlusIcon class="size-4" />
        Add listing
      </button>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="mt-8 flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      <ExclamationTriangleIcon class="size-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Loading -->
    <p
      v-if="loading"
      class="mt-8 font-mono text-xs text-[var(--faint)]"
    >
      Loading listings…
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
          {{ listingCount }}
          {{ listingCount === 1 ? 'listing' : 'listings' }}
        </span>
      </div>

      <!-- Listings -->
      <div
        v-if="projects.length"
        class="mt-3"
      >
        <article
          v-for="project in projects"
          :key="project.id"
          class="group flex items-center gap-4 rounded-[10px] border-b border-[var(--border)] px-2 py-4 transition hover:bg-[var(--hover)]"
        >
          <!-- Initial -->
          <RouterLink
            :to="`/bots/${project.id}`"
            class="grid size-11 shrink-0 place-items-center rounded-[11px] bg-[var(--accent-soft)] font-display text-base font-semibold text-[var(--accent-ink)] no-underline"
          >
            {{ project.name.charAt(0).toUpperCase() }}
          </RouterLink>

          <!-- Information -->
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-3">
              <RouterLink
                :to="`/bots/${project.id}`"
                class="truncate font-display text-[15px] font-semibold tracking-[-0.01em] text-[var(--text)] no-underline hover:text-[var(--accent-ink)]"
              >
                {{ project.name }}
              </RouterLink>
            </div>

            <p
              class="mt-1 line-clamp-2 max-w-2xl text-[13.5px] leading-5 text-[var(--muted)]"
            >
              {{ project.short_description }}
            </p>
          </div>

          <!-- Actions -->
          <div class="flex shrink-0 items-center gap-2">
            <RouterLink
              :to="`/bots/${project.id}`"
              class="hidden rounded-[8px] px-3 py-2 font-mono text-[11.5px] text-[var(--muted)] no-underline transition hover:bg-[var(--sunk)] hover:text-[var(--text)] sm:block"
            >
              View
            </RouterLink>

            <button
              type="button"
              :aria-label="`Delete ${project.name}`"
              class="grid size-9 place-items-center rounded-[8px] text-[var(--faint)] transition hover:bg-red-50 hover:text-red-700"
              @click="remove(project)"
            >
              <TrashIcon class="size-4" />
            </button>
          </div>
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
          No listings yet
        </h2>

        <p
          class="mx-auto mt-2 max-w-sm text-sm leading-6 text-[var(--muted)]"
        >
          Projects you publish to the Matrix directory will appear here.
        </p>

        <p class="mt-4 font-mono text-[11px] text-[var(--faint)]">
          Submission support coming soon
        </p>
      </div>
    </template>
  </main>
</template>
