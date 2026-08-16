<script setup lang="ts">
import { RouterLink } from 'vue-router'

import type { ProjectListItem } from '../types/project'

defineProps<{
  project: ProjectListItem
}>()
</script>

<template>
  <RouterLink
    :to="`/bots/${project.id}`"
    class="group block rounded-2xl border border-zinc-200
      bg-white p-5 transition
      hover:border-zinc-300 hover:shadow-sm
    "
  >
    <div class="flex gap-5">
      <!-- Bot avatar -->
      <div
        class="flex size-14 shrink-0 items-center justify-center
          rounded-2xl bg-emerald-50
          text-xl font-semibold text-emerald-800
        "
      >
        {{ project.name.charAt(0).toUpperCase() }}
      </div>

      <!-- Bot information -->
      <div class="min-w-0 flex-1">
        <div class="flex items-start justify-between gap-4">
          <h2
            class="text-lg font-semibold tracking-tight text-zinc-950
              group-hover:text-zinc-700
            "
          >
            {{ project.name }}
          </h2>
        </div>

        <p class="mt-2 max-w-lg text-sm leading-6 text-zinc-600">
          {{ project.short_description }}
        </p>

        <div class="mt-5 flex items-end justify-between gap-4">
          <!-- Categories -->
          <div class="flex flex-wrap items-center gap-2">
            <span
              v-for="category in project.categories"
              :key="category.id"
              class="rounded-lg bg-zinc-100
                px-2.5 py-1
                text-xs font-medium text-zinc-600
              "
            >
              {{ category.name }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </RouterLink>
</template>
