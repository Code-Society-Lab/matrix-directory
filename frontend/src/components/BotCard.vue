<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { ProjectListItem } from '../types/project'

defineProps<{ project: ProjectListItem }>()
</script>

<template>
  <RouterLink
    :to="`/bots/${project.id}`"
    class="block rounded-lg border border-zinc-200 bg-white p-5 transition hover:border-zinc-300 hover:shadow-sm"
  >
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <h2 class="text-base font-semibold text-zinc-950">
            {{ project.name }}
          </h2>
        </div>
        <p class="mt-2 text-sm leading-6 text-zinc-600">
          {{ project.short_description }}
        </p>
      </div>
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-2">
      <span
        v-for="category in project.categories"
        :key="category.id"
        class="rounded-full bg-zinc-100 px-2 py-1 text-xs text-zinc-600"
      >
        {{ category.name }}
      </span>
      <span class="ml-auto text-xs text-zinc-500">ID {{ project.id }}</span>
    </div>
  </RouterLink>
</template>
