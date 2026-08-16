<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ChevronRightIcon, CheckBadgeIcon } from "@heroicons/vue/24/outline";

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
      err instanceof Error ? err.message : 'Could not load this bot.'
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, loadProject)
onMounted(loadProject)
</script>

<template>
  <main class="mx-auto w-full max-w-6xl px-6 py-10 sm:px-8 lg:py-12">
    <!-- Loading -->
    <div
      v-if="loading"
      class="py-20 text-sm text-zinc-500"
    >
      Loading bot…
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
    >
      {{ error }}
    </div>

    <!-- Project -->
    <template v-else-if="project">
      <!-- Breadcrumb -->
      <nav class="mb-8 flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.18em]">
        <RouterLink
          to="/"
          class="text-emerald-600 transition hover:text-emerald-700"
        >
          Open directory
        </RouterLink>

        <span class="text-zinc-400">
          <ChevronRightIcon class="size-3" />
        </span>

        <RouterLink
          to="/"
          class="text-emerald-600 transition hover:text-emerald-700"
        >
          Bots
        </RouterLink>

        <span class="text-zinc-400">
          <ChevronRightIcon class="size-3" />
        </span>

        <span class="text-zinc-500">
          {{ project.name }}
        </span>
      </nav>

      <!-- Hero -->
      <section class="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
        <div class="max-w-3xl">
          <!-- Name -->
          <div class="flex items-center gap-4">
            <h1 class="text-5xl font-semibold tracking-tight text-zinc-950 sm:text-6xl">
              {{ project.name }}
            </h1>

            <!-- Verified badge 
             TODO: connect some verified mechanism when available -->
            <span
              class="flex items-center justify-center rounded-full bg-emerald-600 text-white"
              title="Verified"
            >
              <CheckBadgeIcon class="size-7" />
            </span>
          </div>

          <!-- Description -->
          <p class="mt-4 text-lg leading-8 text-zinc-500">
            {{ project.short_description }}
          </p>

          <!-- Categories -->
          <div class="mt-5 flex flex-wrap gap-2">
            <span
              v-for="category in project.categories"
              :key="category.id"
              class="rounded-full border border-zinc-200 bg-white px-4 py-1.5 text-sm text-zinc-500 shadow-sm"
            >
              {{ category.name }}
            </span>
          </div>
        </div>

        <!-- Invite to room button -->
        <button
          target="_blank"
          rel="noreferrer"
          class="inline-flex shrink-0 items-center justify-center cursor-pointer rounded-lg bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
          disabled
          title="Coming soon"
        >
          Invite to my room
        </button>
      </section>

      <!-- Details -->
      <div class="mt-12 grid gap-4 lg:grid-cols-[minmax(0,1.5fr)_minmax(320px,1fr)]">
        <!-- Left card -->
        <section class="rounded-2xl border border-zinc-200 bg-white p-8 sm:p-9">
          <!-- About -->
          <div>
            <h2 class="text-xl font-semibold tracking-tight text-zinc-950">
              About
            </h2>

            <p class="mt-4 whitespace-pre-line text-base leading-8 text-zinc-600">
              {{ project.description }}
            </p>
          </div>

          <div class="my-8 border-t border-zinc-200" />

          <!-- Matrix server -->
          <div>
            <h2 class="text-lg font-semibold text-zinc-950">
              Matrix server
            </h2>

            <a
              v-if="project.matrix_server_url"
              :href="project.matrix_server_url"
              target="_blank"
              rel="noreferrer"
              class="mt-3 block break-all text-base text-blue-600 underline decoration-blue-300 underline-offset-2 transition hover:text-blue-700"
            >
              {{ project.matrix_server_url }}
            </a>

            <p
              v-else
              class="mt-3 text-base text-zinc-500"
            >
              Not listed
            </p>
          </div>
        </section>

        <!-- Right card -->
        <aside class="rounded-2xl border border-zinc-200 bg-white p-8 sm:p-9">
          <!-- Website -->
          <div>
            <p class="text-sm font-medium text-zinc-500">
              Website
            </p>

            <a
              v-if="project.website_url"
              :href="project.website_url"
              target="_blank"
              rel="noreferrer"
              class="mt-2 block break-all text-base text-zinc-900 underline decoration-zinc-400 underline-offset-2 transition hover:text-emerald-700"
            >
              {{ project.website_url }}
            </a>

            <p
              v-else
              class="mt-2 text-base text-zinc-900"
            >
              Not listed
            </p>
          </div>

          <div class="my-8 border-t border-zinc-200" />

          <!-- Bot Repository -->
          <div>
            <p class="text-sm font-medium text-zinc-500">
              Repository
            </p>

            <a
              v-if="project.repository_url"
              :href="project.repository_url"
              target="_blank"
              rel="noreferrer"
              class="mt-2 block break-all text-base text-zinc-900 underline decoration-zinc-400 underline-offset-2 transition hover:text-emerald-700"
            >
              {{ project.repository_url }}
            </a>

            <p
              v-else
              class="mt-2 text-base text-zinc-900"
            >
              Not listed
            </p>
          </div>

          <div class="my-8 border-t border-zinc-200" />

          <!-- Owner -->
          <div>
            <p class="text-sm font-medium text-zinc-500">
              Owner
            </p>

            <p class="mt-2 break-all text-base leading-6 text-zinc-900">
              {{ project.user_id }}
            </p>
          </div>

          <div class="my-8 border-t border-zinc-200" />

          <!-- E2EE -->
          <div>
            <p class="text-sm font-medium text-zinc-500">
              E2EE
            </p>

            <p class="mt-2 text-base text-zinc-900">
              {{ project.supports_e2ee ? 'Supported' : 'Not Supported' }}
            </p>
          </div>
        </aside>
      </div>
    </template>
  </main>
</template>
