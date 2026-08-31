<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import type { ProjectListItem } from '../types/project'
import { projectPath } from '../utils/projectRoutes'
import AvatarImage from './AvatarImage.vue'

const props = defineProps<{
  project: ProjectListItem
}>()

const primaryLabel = computed(() => props.project.labels[0])

const extraLabelCount = computed(() =>
  Math.max(props.project.labels.length - 1, 0),
)

const ownerName = computed(
  () => props.project.owner?.display_name || props.project.owner?.matrix_id,
)
</script>

<template>
  <RouterLink
    :to="projectPath(project)"
    class="
      group flex min-h-[66px] items-center gap-4
      rounded-b-[10px]
      border-b border-[var(--border)]
      px-2 py-3
      transition
      hover:bg-[var(--hover)]
      sm:px-3
    "
  >
    <!-- Initial -->
    <div
      class="
        grid size-11 shrink-0 place-items-center
        rounded-[11px] bg-[var(--accent-soft)]
        font-display text-[16px] font-semibold
        text-[var(--accent-ink)]
      "
    >
      {{ project.name.charAt(0).toUpperCase() }}
    </div>

    <!-- Main content -->
    <div class="min-w-0 flex-1">
      <div
        class="
          flex min-w-0 flex-col gap-1
          sm:flex-row sm:items-center sm:gap-3
        "
      >
        <h2
          class="
            min-w-0 truncate font-display text-[15px] font-semibold
            tracking-[-0.01em] text-[var(--text)]
          "
        >
          {{ project.name }}
        </h2>

        <div
          v-if="project.owner"
          class="
            hidden min-w-0 items-center gap-1.5
            md:flex
          "
        >
          <div
            class="
              grid size-4 shrink-0 place-items-center
              overflow-hidden rounded-full
              bg-[var(--accent-soft)]
              text-[8px] font-semibold
              text-[var(--accent-ink)]
            "
          >
            <AvatarImage
              :src="project.owner.avatar_url"
              :name="ownerName"
            />
          </div>

          <span
            class="
              max-w-[150px] truncate
              font-mono text-[10px]
              text-[var(--faint)]
            "
          >
            {{
              project.owner.display_name ||
                project.owner.matrix_id
            }}
          </span>
        </div>
      </div>

      <p
        class="
          mt-1 max-w-2xl
          break-words
          text-[13.5px] leading-5
          text-[var(--muted)]
        "
      >
        {{ project.short_description }}
      </p>

      <div class="mt-2.5 flex flex-wrap items-center gap-1.5">
        <span
          class="
            rounded-[6px] bg-[var(--accent-soft)]
            px-2 py-[3px]
            text-[10.5px] font-medium
            text-[var(--accent-ink)]
          "
        >
          {{ project.project_type.name }}
        </span>

        <span
          v-if="primaryLabel"
          class="
            rounded-[6px] bg-[var(--sunk)]
            px-2 py-[3px]
            text-[10.5px] text-[var(--muted)]
          "
        >
          {{ primaryLabel.name }}
        </span>

        <span
          v-if="extraLabelCount"
          class="
            rounded-[6px] bg-[var(--sunk)]
            px-2 py-[3px]
            font-mono text-[9.5px]
            text-[var(--faint)]
          "
        >
          +{{ extraLabelCount }}
        </span>
      </div>
    </div>
  </RouterLink>
</template>
