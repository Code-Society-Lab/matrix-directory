<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { CheckIcon } from '@heroicons/vue/24/outline'

import type { ProjectListItem } from '../types/project'

const props = defineProps<{
  project: ProjectListItem
}>()

const MAX_VISIBLE_LABELS = 2

const visibleLabels = computed(() =>
  props.project.labels.slice(0, MAX_VISIBLE_LABELS),
)

const hiddenLabelCount = computed(() =>
  Math.max(
    props.project.labels.length - MAX_VISIBLE_LABELS,
    0,
  ),
)

const ownerInitial = computed(() =>
  (
    props.project.owner?.display_name ||
    props.project.owner?.matrix_id ||
    '?'
  )
    .replace(/^@/, '')
    .charAt(0)
    .toUpperCase(),
)
</script>

<template>
  <RouterLink
    :to="`/bots/${project.id}`"
    class="
      group block rounded-[14px]
      border border-[var(--border)]
      bg-[var(--surface)]
      p-4 no-underline
      transition
      hover:border-[var(--border-strong)]
      hover:shadow-[var(--shadow)]
      sm:p-[18px]
    "
  >
    <div class="flex gap-3 sm:gap-3.5">
      <!-- Project avatar -->
      <div
        class="
          grid size-10 shrink-0 place-items-center
          rounded-[10px]
          bg-[var(--accent-soft)]
          font-display text-base font-semibold
          text-[var(--accent-ink)]
          sm:size-11 sm:rounded-[11px] sm:text-lg
        "
      >
        {{ project.name.charAt(0).toUpperCase() }}
      </div>

      <!-- Project information -->
      <div class="min-w-0 flex-1">
        <!-- Header -->
        <div class="flex min-w-0 items-center justify-between gap-3">
          <!-- Title -->
          <div class="flex min-w-0 items-center gap-2">
            <h2
              class="
                min-w-0 truncate
                font-display text-[15px] font-semibold
                tracking-[-0.01em]
                text-[var(--text)]
                sm:text-base
              "
            >
              {{ project.name }}
            </h2>

            <!-- Placeholder until project verification exists -->
            <span
              v-if="false"
              class="
                grid size-[15px] shrink-0 place-items-center
                rounded-full bg-[var(--accent)]
                text-[#0e1012]
              "
              title="Verified"
            >
              <CheckIcon class="size-2.5" />
            </span>
          </div>

          <!-- Owner -->
          <div
            v-if="project.owner"
            class="
              hidden min-w-0 shrink items-center gap-1.5
              lg:flex
            "
          >
            <div
              class="
                grid size-5 shrink-0 place-items-center
                overflow-hidden rounded-full
                bg-[var(--accent-soft)]
                text-[9px] font-semibold
                text-[var(--accent-ink)]
              "
            >
              <img
                v-if="project.owner.avatar_url"
                :src="project.owner.avatar_url"
                alt=""
                class="size-full object-cover"
              >

              <span v-else>
                {{ ownerInitial }}
              </span>
            </div>

            <span
              class="
                max-w-[90px] truncate
                font-mono text-[10px]
                text-[var(--faint)]
                xl:max-w-[120px]
              "
            >
              {{
                project.owner.display_name ||
                  project.owner.matrix_id ||
                  'unknown'
              }}
            </span>
          </div>
        </div>

        <!-- Description -->
        <p
          class="
            mt-1.5 line-clamp-2
            text-[13px] leading-[1.5]
            text-[var(--muted)]
            sm:text-[13.5px]
          "
        >
          {{ project.short_description }}
        </p>

        <!-- Metadata -->
        <div class="mt-3 flex min-w-0 flex-wrap items-center gap-1.5">
          <!-- Project type -->
          <span
            class="
              shrink-0 rounded-[6px]
              bg-[var(--accent-soft)]
              px-2 py-[3px]
              text-[11px] font-medium
              text-[var(--accent-ink)]
              sm:text-[11.5px]
            "
          >
            {{ project.project_type.name }}
          </span>

          <!-- Primary label -->
          <span
            v-for="label in visibleLabels"
            :key="label.id"
            class="
              shrink-0 rounded-[6px]
              bg-[var(--sunk)]
              px-2 py-[3px]
              text-[11px] text-[var(--muted)]
              sm:text-[11.5px]
            "
          >
            {{ label.name }}
          </span>

          <!-- Remaining labels -->
          <span
            v-if="hiddenLabelCount"
            class="
              shrink-0 rounded-[6px]
              bg-[var(--sunk)]
              px-2 py-[3px]
              font-mono text-[10px]
              text-[var(--faint)]
            "
            :title="project.labels
              .slice(MAX_VISIBLE_LABELS)
              .map((label) => label.name)
              .join(', ')
            "
          >
            +{{ hiddenLabelCount }}
          </span>
        </div>
      </div>
    </div>
  </RouterLink>
</template>