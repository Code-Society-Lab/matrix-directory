<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ExclamationTriangleIcon, TrashIcon } from "@heroicons/vue/24/outline";

import { deleteProject, listMyProjects } from '../api/client'
import type { ProjectListItem } from '../types/project'

const projects = ref<ProjectListItem[]>([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  try {
    projects.value = await listMyProjects()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load your listings.'
  } finally {
    loading.value = false
  }
}

async function remove(project: ProjectListItem) {
  if (!window.confirm(`Delete ${project.name} from the directory?`)) return
  try {
    await deleteProject(project.id)
    projects.value = projects.value.filter((item) => item.id !== project.id)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not delete the listing.'
  }
}

onMounted(load)
</script>

<template>
  <main class="mx-auto max-w-4xl px-5 py-10">
    <h1 class="text-3xl font-semibold tracking-tight text-zinc-950">
      My listings
    </h1>
    <p class="mt-2 text-zinc-600">
      Listings associated with your authenticated Matrix account.
    </p>

    <p class="mt-6 text-red-600">
      <ExclamationTriangleIcon class="mr-2 inline-block size-5" />
      Add a new listing coming soon.
    </p>

    <p
      v-if="error"
      class="mt-6 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700"
    >
      {{ error }}
    </p>
    <p
      v-if="loading"
      class="mt-6 text-sm text-zinc-500"
    >
      Loading…
    </p>
    <div
      v-else
      class="mt-6 divide-y divide-zinc-200 rounded-lg border border-zinc-200 bg-white"
    >
      <div
        v-for="project in projects"
        :key="project.id"
        class="flex items-center justify-between gap-4 p-4"
      >
        <div>
          <RouterLink
            :to="`/bots/${project.id}`"
            class="font-medium text-zinc-900 hover:underline"
          >
            {{ project.name }}
          </RouterLink>
          <p class="mt-1 text-sm text-zinc-500">
            {{ project.short_description }}
          </p>
        </div>
        <button
          class="text-sm font-medium text-red-700 hover:underline"
          @click="remove(project)"
        >
          <TrashIcon class="size-4" />
        </button>
      </div>
      <p
        v-if="!projects.length"
        class="p-6 text-sm text-zinc-500"
      >
        You do not have any listings yet.
      </p>
    </div>
  </main>
</template>
