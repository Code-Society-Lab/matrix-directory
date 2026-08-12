<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { listProjects } from '../api/client'
import BotCard from '../components/BotCard.vue'
import type { ProjectListItem } from '../types/project'

const projects = ref<ProjectListItem[]>([])
const query = ref('')
const category = ref('')
const loading = ref(true)
const error = ref('')
const categories = computed(() => [
  ...new Set(projects.value.flatMap((project) => project.categories.map((item) => item.name))),
].sort())

const visibleProjects = computed(() => {
  const normalizedQuery = query.value.trim().toLowerCase()
  return projects.value.filter((project) => {
    const matchesQuery = !normalizedQuery || [project.name, project.short_description, project.description]
      .join(' ')
      .toLowerCase()
      .includes(normalizedQuery)
    const matchesCategory = !category.value || project.categories.some((item) => item.name === category.value)
    return matchesQuery && matchesCategory
  })
})

async function loadProjects() {
  loading.value = true
  error.value = ''
  try {
    projects.value = await listProjects()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load bots.'
  } finally {
    loading.value = false
  }
}

onMounted(loadProjects)
</script>

<template>
  <main class="mx-auto max-w-6xl px-5 py-10">
    <section class="max-w-2xl">
      <p class="text-sm font-medium text-zinc-500 tracking-wide uppercase">
        Matrix ecosystem
      </p>
      <h1 class="mt-2 text-3xl font-semibold tracking-tight text-zinc-950">
        Find bots built for Matrix.
      </h1>
      <p class="mt-3 text-base leading-7 text-zinc-600">
        A small, community-oriented registry for discovering Matrix bots.
      </p>
    </section>

    <section class="mt-8 border-t border-zinc-200 pt-6">
      <div class="flex flex-col gap-3 sm:flex-row">
        <label class="flex-1">
          <span class="sr-only">Search bots</span>
          <input
            v-model="query"
            type="search"
            placeholder="Search bots"
            class="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm outline-none placeholder:text-zinc-400 focus:border-zinc-500"
          >
        </label>

        <label>
          <span class="sr-only">Category</span>
          <select
            v-model="category"
            class="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-700 outline-none focus:border-zinc-500 sm:w-48"
          >
            <option value="">All categories</option>
            <option
              v-for="item in categories"
              :key="item"
              :value="item"
            >{{ item }}</option>
          </select>
        </label>
      </div>

      <p
        v-if="error"
        class="mt-6 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700"
      >
        {{ error }}
      </p>

      <div
        v-else-if="loading"
        class="mt-6 text-sm text-zinc-500"
      >
        Loading bots…
      </div>

      <div
        v-else-if="visibleProjects.length"
        class="mt-6 grid gap-4 md:grid-cols-2"
      >
        <BotCard
          v-for="project in visibleProjects"
          :key="project.id"
          :project="project"
        />
      </div>

      <div
        v-else
        class="mt-6 rounded-lg border border-dashed border-zinc-300 bg-white p-8 text-center"
      >
        <p class="text-sm font-medium text-zinc-800">
          No bots found
        </p>
        <p class="mt-1 text-sm text-zinc-500">
          Try a different search or category.
        </p>
      </div>
    </section>
  </main>
</template>
