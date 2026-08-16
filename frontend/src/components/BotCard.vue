<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { CheckIcon } from '@heroicons/vue/24/outline'

import type { ProjectListItem } from '../types/project'

defineProps<{
  project: ProjectListItem
}>()
</script>

<template>
  <RouterLink
    :to="`/bots/${project.id}`"
    class="group block rounded-[14px] border border-[var(--border)]
      bg-[var(--surface)] p-[18px] no-underline transition
      hover:border-[var(--border-strong)] hover:shadow-[var(--shadow)]"
  >
    <div class="flex gap-3.5">
      <!-- Bot avatar -->
      <div
        class="grid size-11 shrink-0 place-items-center
          rounded-[11px] bg-[var(--accent-soft)]
          font-display text-lg font-semibold
          text-[var(--accent-ink)]"
      >
        {{ project.name.charAt(0).toUpperCase() }}
      </div>

      <!-- Bot information -->
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <h2
            class="truncate font-display
              text-base font-semibold tracking-[-0.01em]
              text-[var(--text)]"
          >
            {{ project.name }}
          </h2>

          <!-- Placeholder until project verification exists -->
          <span
            v-if="false"
            class="grid size-[15px] shrink-0 place-items-center
              rounded-full bg-[var(--accent)]
              text-[#0e1012]"
            title="Verified"
          >
            <CheckIcon class="size-2.5" />
          </span>
        </div>

        <p
          class="mt-1.5 line-clamp-2 text-[13.5px]
            leading-[1.5] text-[var(--muted)]"
        >
          {{ project.short_description }}
        </p>

        <div class="mt-3 flex items-end justify-between gap-3">
          <!-- Categories -->
          <div class="flex min-w-0 flex-wrap gap-1.5">
            <span
              v-for="category in project.categories"
              :key="category.id"
              class="rounded-[6px] bg-[var(--sunk)]
                px-2 py-[3px] text-[11.5px]
                text-[var(--muted)]"
            >
              {{ category.name }}
            </span>
          </div>

          <!-- Owner -->
          <div
            v-if="project.owner"
            class="hidden shrink-0 items-center gap-1.5 lg:flex"
          >
            <div
              class="grid size-5 place-items-center overflow-hidden
                rounded-full bg-[var(--accent-soft)]
                text-[9px] font-semibold text-[var(--accent-ink)]"
            >
              <img
                v-if="project.owner.avatar_url"
                :src="project.owner.avatar_url"
                alt=""
                class="size-full object-cover"
              >

              <span v-else>
                {{
                  (
                    project.owner.display_name ||
                    project.owner.matrix_id ||
                    '?'
                  )
                    .replace(/^@/, '')
                    .charAt(0)
                    .toUpperCase()
                }}
              </span>
            </div>

            <span
              class="max-w-[100px] truncate font-mono
                text-[10.5px] text-[var(--faint)]"
            >
              {{
                project.owner.display_name ||
                  project.owner.matrix_id ||
                  'unknown'
              }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </RouterLink>
</template>
