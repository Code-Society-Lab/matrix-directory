<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import {
  EllipsisHorizontalIcon,
  EyeIcon,
  PencilSquareIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'

import type { ProjectListItem } from '../types/project'
import { projectPath } from '../utils/projectRoutes'

const props = defineProps<{
  project: ProjectListItem
}>()

const emit = defineEmits<{
  delete: []
}>()

const menuOpen = ref(false)
const menuPlacement = ref<'above' | 'below'>('below')

function toggleMenu(event: MouseEvent) {
  if (menuOpen.value) {
    menuOpen.value = false
    return
  }

  const button = event.currentTarget as HTMLElement
  const spaceBelow = window.innerHeight - button.getBoundingClientRect().bottom

  menuPlacement.value = spaceBelow < 128 ? 'above' : 'below'
  document.dispatchEvent(
    new CustomEvent('project-actions-open', {
      detail: props.project.id,
    }),
  )
  menuOpen.value = true
}

function closeWhenAnotherMenuOpens(event: Event) {
  if ((event as CustomEvent<string>).detail !== props.project.id) {
    menuOpen.value = false
  }
}

function closeMenuOnOutsideClick(event: PointerEvent) {
  if (
    menuOpen.value &&
    (!(event.target instanceof Element) ||
      !event.target.closest('[data-project-actions]'))
  ) {
    menuOpen.value = false
  }
}

function remove() {
  menuOpen.value = false
  emit('delete')
}

onMounted(() => {
  document.addEventListener('pointerdown', closeMenuOnOutsideClick)
  document.addEventListener('project-actions-open', closeWhenAnotherMenuOpens)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', closeMenuOnOutsideClick)
  document.removeEventListener('project-actions-open', closeWhenAnotherMenuOpens)
})
</script>

<template>
  <div
    data-project-actions
    class="absolute right-2 top-3 sm:static sm:shrink-0"
  >
    <div class="hidden items-center sm:flex">
      <RouterLink
        :to="`/projects/${props.project.id}/edit`"
        :aria-label="`Edit ${props.project.name}`"
        title="Edit project"
        class="grid size-9 place-items-center rounded-[8px] text-[var(--faint)] no-underline transition hover:bg-[var(--sunk)] hover:text-[var(--text)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
      >
        <PencilSquareIcon
          class="size-4"
          aria-hidden="true"
        />
      </RouterLink>

      <RouterLink
        :to="projectPath(props.project)"
        aria-label="View project"
        title="View project"
        class="grid size-9 place-items-center rounded-[8px] text-[var(--faint)] no-underline transition hover:bg-[var(--sunk)] hover:text-[var(--text)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
      >
        <EyeIcon
          class="size-4"
          aria-hidden="true"
        />
      </RouterLink>

      <button
        type="button"
        :aria-label="`Delete ${props.project.name}`"
        title="Delete project"
        class="grid size-9 cursor-pointer place-items-center rounded-[8px] text-[var(--faint)] transition hover:bg-[var(--danger-soft)] hover:text-[var(--danger)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--danger)]"
        @click="remove"
      >
        <TrashIcon
          class="size-4"
          aria-hidden="true"
        />
      </button>
    </div>

    <div class="relative sm:hidden">
      <button
        type="button"
        aria-label="Project actions"
        :aria-expanded="menuOpen"
        class="grid size-9 cursor-pointer place-items-center rounded-[8px] bg-[var(--bg)] text-[var(--faint)] transition hover:text-[var(--text)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
        @click="toggleMenu"
      >
        <EllipsisHorizontalIcon
          class="size-5"
          aria-hidden="true"
        />
      </button>

      <div
        v-if="menuOpen"
        class="absolute right-0 z-10 w-36 rounded-[10px] border border-[var(--border)] bg-[var(--surface)] p-1 shadow-lg"
        :class="menuPlacement === 'above' ? 'bottom-10' : 'top-10'"
      >
        <RouterLink
          :to="projectPath(props.project)"
          class="flex items-center gap-2 rounded-[7px] px-3 py-2 text-sm text-[var(--text)] no-underline hover:bg-[var(--sunk)]"
          @click="menuOpen = false"
        >
          <EyeIcon class="size-4" />
          View
        </RouterLink>
        <RouterLink
          :to="`/projects/${props.project.id}/edit`"
          class="flex items-center gap-2 rounded-[7px] px-3 py-2 text-sm text-[var(--text)] no-underline hover:bg-[var(--sunk)]"
          @click="menuOpen = false"
        >
          <PencilSquareIcon class="size-4" />
          Edit
        </RouterLink>
        <button
          type="button"
          class="flex w-full cursor-pointer items-center gap-2 rounded-[7px] px-3 py-2 text-sm text-[var(--danger)] hover:bg-[var(--danger-soft)]"
          @click="remove"
        >
          <TrashIcon class="size-4" />
          Delete
        </button>
      </div>
    </div>
  </div>
</template>
