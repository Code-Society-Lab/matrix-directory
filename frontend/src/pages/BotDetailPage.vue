<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
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
    error.value = err instanceof Error ? err.message : 'Could not load this bot.'
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, loadProject)
onMounted(loadProject)
</script>

<template>
  <main class="mx-auto max-w-5xl px-5 py-10">
    <div
      v-if="loading"
      class="text-sm text-zinc-500"
    >
      Loading bot…
    </div>
    <div
      v-else-if="error"
      class="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700"
    >
      {{ error }}
    </div>

    <template v-else-if="project">
      <div class="border-b border-zinc-200 pb-8">
        <div class="flex flex-wrap items-start justify-between gap-6">
          <div class="max-w-2xl">
            <h1 class="text-3xl font-semibold tracking-tight text-zinc-950">
              {{ project.name }}
            </h1>
            <p class="mt-3 text-base leading-7 text-zinc-600">
              {{ project.short_description }}
            </p>
            <div class="mt-4 flex flex-wrap gap-2">
              <span
                v-for="category in project.categories"
                :key="category.id"
                class="rounded-full bg-zinc-100 px-2.5 py-1 text-xs text-zinc-600"
              >
                {{ category.name }}
              </span>
            </div>
          </div>

          <a
            v-if="project.repository_url"
            :href="project.repository_url"
            target="_blank"
            rel="noreferrer"
            class="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-50"
          >
            View repository
          </a>
        </div>
      </div>

      <div class="grid gap-10 py-8 md:grid-cols-[minmax(0,1fr)_260px]">
        <section>
          <h2 class="text-sm font-semibold uppercase tracking-wide text-zinc-500">
            About
          </h2>
          <p class="mt-3 whitespace-pre-line text-sm leading-7 text-zinc-700">
            {{ project.description }}
          </p>

          <h2 class="mt-8 text-sm font-semibold uppercase tracking-wide text-zinc-500">
            Matrix server
          </h2>
          <a
            v-if="project.matrix_server_url"
            :href="project.matrix_server_url"
            target="_blank"
            rel="noreferrer"
            class="mt-3 block break-all text-sm text-blue-600 underline"
          >
            {{ project.matrix_server_url }}
          </a>
          <p
            v-else
            class="mt-3 text-sm text-zinc-700"
          >
            Not listed
          </p>
        </section>

        <aside class="space-y-5 text-sm">
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-zinc-500">
              Website
            </p>
            <a
              v-if="project.website_url"
              :href="project.website_url"
              target="_blank"
              rel="noreferrer"
              class="mt-1 block break-all text-zinc-800 underline"
            >{{ project.website_url }}</a>
            <p
              v-else
              class="mt-1 text-zinc-800"
            >
              Not listed
            </p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-zinc-500">
              Owner
            </p>
            <p class="mt-1 break-all text-zinc-800">
              {{ project.user_id }}
            </p>
          </div>
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-zinc-500">
              E2EE
            </p>
            <p class="mt-1 text-zinc-800">
              {{ project.supports_e2ee ? 'Supported' : 'Not Supported' }}
            </p>
          </div>
        </aside>
      </div>
    </template>
  </main>
</template>
