<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowLeftIcon,
  CheckIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'

import { getProject } from '../api/client'
import type { Project } from '../types/project'

const route = useRoute()

const project = ref<Project | null>(null)
const loading = ref(true)
const error = ref('')

async function loadProject() {
  loading.value = true
  error.value = ''

  try {
    project.value = await getProject(String(route.params.id))
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not load this bot.'
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, loadProject)
onMounted(loadProject)
</script>

<template>
  <main
    class="mx-auto w-full max-w-[1120px] px-5 pb-24 pt-8 sm:px-8"
  >
    <!-- Loading -->
    <div
      v-if="loading"
      class="py-20 font-mono text-xs text-[var(--faint)]"
    >
      Loading bot…
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      <ExclamationTriangleIcon class="size-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Project -->
    <template v-else-if="project">
      <!-- Back -->
      <RouterLink
        to="/"
        class="inline-flex items-center gap-2 font-mono text-[12px] text-[var(--muted)] no-underline transition hover:text-[var(--text)]"
      >
        <ArrowLeftIcon class="size-3.5" />
        back to directory
      </RouterLink>

      <!-- Hero -->
      <section
        class="mt-7 flex flex-col gap-7 lg:flex-row lg:items-start lg:justify-between"
      >
        <div class="flex min-w-0 gap-5">
          <!-- Bot avatar -->
          <div
            class="grid size-[76px] shrink-0 place-items-center rounded-[18px] bg-[var(--accent-soft)] font-display text-[30px] font-semibold text-[var(--accent-ink)]"
          >
            {{ project.name.charAt(0).toUpperCase() }}
          </div>

          <div class="min-w-0">
            <!-- Name -->
            <div class="flex flex-wrap items-center gap-3">
              <h1
                class="font-display text-[34px] font-semibold tracking-[-0.025em] text-[var(--text)] sm:text-[40px]"
              >
                {{ project.name }}
              </h1>

              <!-- TODO: connect to actual verification -->
              <span
                class="inline-flex items-center gap-1.5 rounded-full bg-[var(--accent-soft)] px-2.5 py-1 text-xs font-medium text-[var(--accent-ink)]"
                title="Verified maintainer"
              >
                <CheckIcon class="size-3.5" />
                Verified
              </span>
            </div>

            <!-- Description -->
            <p
              class="mt-2 max-w-[650px] text-[15.5px] leading-6 text-[var(--muted)]"
            >
              {{ project.short_description }}
            </p>

            <!-- Categories -->
            <div class="mt-4 flex flex-wrap gap-2">
              <span
                v-for="category in project.categories"
                :key="category.id"
                class="rounded-[6px] bg-[var(--sunk)] px-2.5 py-1 text-[12px] text-[var(--muted)]"
              >
                {{ category.name }}
              </span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div
          class="flex shrink-0 flex-row gap-2 lg:w-[200px] lg:flex-col"
        >
          <button
            type="button"
            disabled
            title="Coming soon"
            class="cursor-not-allowed rounded-[10px] bg-[var(--accent)] px-4 py-3 text-center text-sm font-medium text-[#0e1012] opacity-50"
          >
            Invite to a room
          </button>

          <a
            v-if="project.repository_url"
            :href="project.repository_url"
            target="_blank"
            rel="noreferrer"
            class="rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-center text-sm text-[var(--text)] no-underline transition hover:border-[var(--border-strong)]"
          >
            Repository
          </a>
        </div>
      </section>

      <!-- Main content -->
      <div
        class="mt-12 grid gap-10 lg:grid-cols-[minmax(0,1fr)_300px]"
      >
        <!-- Left -->
        <div>
          <!-- About -->
          <section>
            <h2
              class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              About
            </h2>

            <p
              class="mt-4 whitespace-pre-line text-[15.5px] leading-7 text-[var(--text)]"
            >
              {{ project.description }}
            </p>
          </section>

          <!-- Matrix server -->
          <section class="mt-10">
            <h2
              class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              Commands
            </h2>

            <div
              class="mt-4 overflow-hidden rounded-[12px] border border-[var(--border)] bg-[var(--surface)]"
            >
              <div
                class="mt-5 rounded-[14px] bg-[var(--surface)] px-6 py-10 text-center"
              >
                <p
                  class="font-display text-sm font-semibold text-[var(--text)]"
                >
                  Bot commands are coming soon
                </p>

                <p
                  class="mx-auto mt-2 max-w-sm text-[13.5px] leading-5 text-[var(--muted)]"
                >
                  Once available, you will be able to see the commands that this bot supports, along with their descriptions and usage examples.
                </p>
              </div>
            </div>
          </section>
        </div>

        <!-- Facts -->
        <aside
          class="self-start rounded-[14px] border border-[var(--border)] bg-[var(--surface)] px-4"
        >
          <!-- Room / Server -->
          <div
            class="flex items-start justify-between gap-5 border-b border-[var(--border)] py-4"
          >
            <span
              class="text-[11.5px] uppercase tracking-[0.04em] text-[var(--faint)]"
            >
              Room / server
            </span>

            <a
              v-if="project.matrix_server_url"
              :href="project.matrix_server_url"
              target="_blank"
              rel="noreferrer"
              class="max-w-[170px] break-all text-right font-mono text-[12px] text-[var(--accent-ink)] no-underline hover:underline"
            >
              Join
            </a>

            <span
              v-else
              class="font-mono text-[12px] text-[var(--faint)]"
            >
              Not listed
            </span>
          </div>

          <!-- Website -->
          <div
            class="flex items-start justify-between gap-5 border-b border-[var(--border)] py-4"
          >
            <span
              class="text-[11.5px] uppercase tracking-[0.04em] text-[var(--faint)]"
            >
              Website
            </span>

            <a
              v-if="project.website_url"
              :href="project.website_url"
              target="_blank"
              rel="noreferrer"
              class="max-w-[170px] break-all text-right font-mono text-[12px] text-[var(--accent-ink)] no-underline hover:underline"
            >
              Visit
            </a>

            <span
              v-else
              class="font-mono text-[12px] text-[var(--faint)]"
            >
              Not listed
            </span>
          </div>

          <!-- Owner -->
          <div
            class="flex items-start justify-between gap-5 border-b border-[var(--border)] py-4"
          >
            <span
              class="text-[11.5px] uppercase tracking-[0.04em] text-[var(--faint)]"
            >
              Owner
            </span>

            <span
              class="max-w-[170px] break-all text-right font-mono text-[12px] text-[var(--text)]"
            >
              {{ project.owner.display_name ?? project.owner.matrix_id ?? 'Not listed' }}
            </span>
          </div>

          <!-- Categories -->
          <div
            class="flex items-start justify-between gap-5 border-b border-[var(--border)] py-4"
          >
            <span
              class="text-[11.5px] uppercase tracking-[0.04em] text-[var(--faint)]"
            >
              Categories
            </span>

            <span
              class="max-w-[170px] text-right font-mono text-[12px] leading-5 text-[var(--text)]"
            >
              {{
                project.categories
                  .map((category) => category.name)
                  .join(', ')
              }}
            </span>
          </div>

          <!-- E2EE -->
          <div
            class="flex items-start justify-between gap-5 py-4"
          >
            <span
              class="text-[11.5px] uppercase tracking-[0.04em] text-[var(--faint)]"
            >
              E2EE
            </span>

            <span
              class="font-mono text-[12px]"
              :class="
                project.supports_e2ee
                  ? 'text-[var(--accent-ink)]'
                  : 'text-[var(--muted)]'
              "
            >
              {{
                project.supports_e2ee
                  ? 'Supported'
                  : 'Not supported'
              }}
            </span>
          </div>
        </aside>
      </div>
    </template>
  </main>
</template>
