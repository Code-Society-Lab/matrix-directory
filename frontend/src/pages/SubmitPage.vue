<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeftIcon,
  ExclamationTriangleIcon,
  LockClosedIcon,
} from '@heroicons/vue/24/outline'

import {
  ApiError,
  createProject,
  listLabels,
  listProjectTypes,
} from '../api/client'
import MarkdownEditor from '../components/markdown/MarkdownEditor.vue'
import type { Label, ProjectCreate, ProjectType } from '../types/project'
import { projectPath } from '../utils/projectRoutes'

const router = useRouter()
const form = reactive<ProjectCreate>({
  name: '',
  short_description: '',
  description: '',
  repository_url: null,
  website_url: null,
  matrix_server_url: null,
  supports_e2ee: false,
  project_type_id: '',
  label_ids: [],
})

const projectTypes = ref<ProjectType[]>([])
const labels = ref<Label[]>([])
const loadingClassifications = ref(true)
const submitting = ref(false)
const formError = ref('')
const fieldErrors = ref<Record<string, string>>({})

const selectedLabels = computed(() =>
  labels.value.filter((label) =>
    form.label_ids.includes(label.id),
  ),
)

const previewInitial = computed(() =>
  form.name.trim().charAt(0).toUpperCase() || '?',
)

const hasProjectLink = computed(() =>
  Boolean(
    form.repository_url?.trim() ||
    form.website_url?.trim(),
  ),
)

const cannotSubmit = computed(() =>
  submitting.value ||
  loadingClassifications.value ||
  !form.name.trim() ||
  !form.short_description.trim() ||
  !form.description.trim() ||
  !form.project_type_id ||
  !hasProjectLink.value ||
  form.short_description.length > 160 ||
  form.description.length > 10000,
)

const checklist = computed(() => [
  {
    label: 'Name',
    complete: Boolean(form.name.trim()),
    required: true,
  },
  {
    label: 'Short description',
    complete: Boolean(form.short_description.trim()),
    required: true,
  },
  {
    label: 'About',
    complete: Boolean(form.description.trim()),
    required: true,
  },
  {
    label: 'Project link',
    complete: hasProjectLink.value,
    required: true,
  },
  {
    label: 'Project type',
    complete: Boolean(form.project_type_id),
    required: true,
  },
  {
    label: 'Labels',
    complete: form.label_ids.length > 0,
    required: false,
  },
  {
    label: 'Matrix room',
    complete: Boolean(form.matrix_server_url?.trim()),
    required: false,
  },
  {
    label: 'E2EE support',
    complete: form.supports_e2ee,
    required: false,
  },
])

const requiredChecklist = computed(() =>
  checklist.value.filter((item) => item.required),
)

const requiredCompleteCount = computed(() =>
  requiredChecklist.value.filter((item) => item.complete).length,
)

const listingReady = computed(() =>
  requiredChecklist.value.every((item) => item.complete),
)

function optionalValue(value: string | null) {
  const normalized = value?.trim()
  return normalized || null
}

function fieldError(field: string) {
  return fieldErrors.value[field]
}

async function submit() {
  if (cannotSubmit.value) return

  submitting.value = true
  formError.value = ''
  fieldErrors.value = {}

  try {
    const created = await createProject({
      ...form,
      name: form.name.trim(),
      short_description: form.short_description.trim(),
      description: form.description.trim(),
      repository_url: optionalValue(form.repository_url),
      website_url: optionalValue(form.website_url),
      matrix_server_url: optionalValue(form.matrix_server_url),
    })

    await router.push(projectPath(created))
  } catch (error) {
    if (error instanceof ApiError && error.issues.length) {
      for (const issue of error.issues) {
        const field = String(issue.loc.at(-1))

        fieldErrors.value[field] = issue.msg.replace(
          /^Value error, /,
          '',
        )
      }
    } else {
      formError.value =
        error instanceof Error
          ? error.message
          : 'Could not publish the listing.'
    }
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const [availableProjectTypes, availableLabels] = await Promise.all([
      listProjectTypes(),
      listLabels(),
    ])
    projectTypes.value = availableProjectTypes
    labels.value = availableLabels
  } catch (error) {
    formError.value =
      error instanceof Error
        ? error.message
        : 'Could not load project classifications.'
  } finally {
    loadingClassifications.value = false
  }
})
</script>

<template>
  <main class="mx-auto max-w-6xl px-5 pb-24 pt-8 sm:px-8">
    <RouterLink
      to="/dashboard"
      class="inline-flex items-center gap-2 font-mono text-[12px] text-[var(--muted)] no-underline transition hover:text-[var(--text)]"
    >
      <ArrowLeftIcon class="size-3.5" />
      back to dashboard
    </RouterLink>

    <!-- Page heading -->
    <header class="mt-7 max-w-2xl">
      <p
        class="font-mono text-xs font-medium uppercase tracking-[0.08em] text-[var(--accent-ink)]"
      >
        Directory listing
      </p>

      <h1
        class="mt-3 font-display text-[34px] font-semibold tracking-[-0.025em] text-[var(--text)]"
      >
        Submit a project
      </h1>

      <p class="mt-2 text-[15px] leading-6 text-[var(--muted)]">
        Add a Matrix bot or integration to the public directory.
        You can update these details later.
      </p>
    </header>

    <!-- Global error -->
    <div
      v-if="formError"
      class="mt-7 flex max-w-3xl items-start gap-2.5 rounded-[10px] border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]"
      role="alert"
    >
      <ExclamationTriangleIcon class="mt-0.5 size-4 shrink-0" />
      {{ formError }}
    </div>

    <form
      class="mt-10 grid items-start gap-12 lg:grid-cols-[minmax(0,1fr)_320px]"
      @submit.prevent="submit"
    >
      <!-- Main form -->
      <div class="min-w-0 space-y-10">
        <!-- Project -->
        <section>
          <div class="border-b border-[var(--border)] pb-3">
            <h2
              class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              Project
            </h2>
          </div>

          <div class="mt-6 space-y-6">
            <!-- Name -->
            <label class="block">
              <span class="text-[13px] font-medium text-[var(--text)]">
                Name
              </span>

              <input
                v-model="form.name"
                type="text"
                minlength="2"
                maxlength="100"
                required
                autocomplete="off"
                placeholder="Example Bot"
                class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition placeholder:text-[var(--faint)] focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
              >

              <span
                v-if="fieldError('name')"
                class="mt-1.5 block text-xs text-[var(--danger)]"
              >
                {{ fieldError('name') }}
              </span>
            </label>

            <!-- Short description -->
            <label class="block">
              <span class="flex items-end justify-between gap-4">
                <span>
                  <span
                    class="block text-[13px] font-medium text-[var(--text)]"
                  >
                    Short description
                  </span>

                  <span
                    class="mt-1 block text-[12.5px] text-[var(--muted)]"
                  >
                    Appears in directory cards and search results.
                  </span>
                </span>

                <span
                  class="shrink-0 font-mono text-[11px] text-[var(--faint)]"
                >
                  {{ form.short_description.length }}/160
                </span>
              </span>

              <input
                v-model="form.short_description"
                type="text"
                maxlength="160"
                required
                placeholder="General-purpose Matrix bot built with matrix.py."
                class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition placeholder:text-[var(--faint)] focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
              >

              <span
                v-if="fieldError('short_description')"
                class="mt-1.5 block text-xs text-[var(--danger)]"
              >
                {{ fieldError('short_description') }}
              </span>
            </label>

            <!-- About -->
            <div>
              <span class="flex items-end justify-between gap-4">
                <span>
                  <span
                    id="long-description-label"
                    class="block text-[13px] font-medium text-[var(--text)]"
                  >
                    About
                  </span>

                  <span
                    class="mt-1 mb-2 block text-[12.5px] text-[var(--muted)]"
                  >
                    Explain what the project does, who it is for, and
                    how people can use it. Markdown is supported.
                  </span>
                </span>

                <span
                  class="shrink-0 font-mono text-[11px] text-[var(--faint)]"
                >
                  {{ form.description.length }}/10000
                </span>
              </span>

              <MarkdownEditor
                v-model="form.description"
                :maxlength="10000"
                placeholder="Tell Matrix users about the project..."
                aria-label="About"
              />

              <span
                v-if="fieldError('description')"
                class="mt-1.5 block text-xs text-[var(--danger)]"
              >
                {{ fieldError('description') }}
              </span>
            </div>
          </div>
        </section>

        <!-- Links -->
        <section>
          <div class="border-b border-[var(--border)] pb-3">
            <h2
              class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              Links
            </h2>
          </div>

          <p class="mt-5 text-[12.5px] leading-5 text-[var(--muted)]">
            Provide at least a repository or website so people can
            learn more about the project.
          </p>

          <div class="mt-5 space-y-6">
            <!-- Repository -->
            <label class="block">
              <span class="flex items-center gap-2">
                <span class="text-[13px] font-medium text-[var(--text)]">
                  Repository
                </span>

                <span class="text-[12px] text-[var(--faint)]">
                  Recommended
                </span>
              </span>

              <span
                class="mt-1 block text-[12.5px] text-[var(--muted)]"
              >
                Source code or primary project repository.
              </span>

              <input
                v-model="form.repository_url"
                type="url"
                maxlength="255"
                placeholder="https://github.com/Code-Society-Lab/ada"
                class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition placeholder:text-[var(--faint)] focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
              >

              <span
                v-if="fieldError('repository_url')"
                class="mt-1.5 block text-xs text-[var(--danger)]"
              >
                {{ fieldError('repository_url') }}
              </span>
            </label>

            <!-- Website -->
            <label class="block">
              <span class="text-[13px] font-medium text-[var(--text)]">
                Website
              </span>

              <span
                class="mt-1 block text-[12.5px] text-[var(--muted)]"
              >
                Project website, documentation, or landing page.
              </span>

              <input
                v-model="form.website_url"
                type="url"
                maxlength="255"
                placeholder="https://example.com"
                class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition placeholder:text-[var(--faint)] focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
              >

              <span
                v-if="fieldError('website_url')"
                class="mt-1.5 block text-xs text-[var(--danger)]"
              >
                {{ fieldError('website_url') }}
              </span>
            </label>

            <!-- Matrix room -->
            <label class="block">
              <span class="flex items-center gap-2">
                <span class="text-[13px] font-medium text-[var(--text)]">
                  Matrix room
                </span>

                <span class="text-[12px] text-[var(--faint)]">
                  Optional
                </span>
              </span>

              <p class="mt-1 text-[12.5px] text-[var(--muted)]">
                Support room, project room, or community space.
              </p>

              <input
                v-model="form.matrix_server_url"
                type="url"
                maxlength="255"
                placeholder="https://matrix.to/#/#room:example.org"
                class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition placeholder:text-[var(--faint)] focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
              >

              <span
                v-if="fieldError('matrix_server_url')"
                class="mt-1.5 block text-xs text-[var(--danger)]"
              >
                {{ fieldError('matrix_server_url') }}
              </span>
            </label>
          </div>
        </section>

        <!-- Discovery -->
        <section>
          <div class="border-b border-[var(--border)] pb-3">
            <h2
              class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              Discovery
            </h2>
          </div>

          <fieldset class="mt-6">
            <legend class="text-[13px] font-medium text-[var(--text)]">
              Project type
              <span class="text-[var(--danger)]">*</span>
            </legend>

            <p class="mt-1 text-[12.5px] text-[var(--muted)]">
              Choose the single option that best describes what this project is.
            </p>

            <p
              v-if="loadingClassifications"
              class="mt-4 font-mono text-xs text-[var(--faint)]"
            >
              Loading project types…
            </p>

            <div
              v-else-if="projectTypes.length"
              class="mt-4 flex flex-wrap gap-2"
            >
              <label
                v-for="projectType in projectTypes"
                :key="projectType.id"
                class="group cursor-pointer"
              >
                <input
                  v-model="form.project_type_id"
                  type="radio"
                  name="project-type"
                  :value="projectType.id"
                  class="peer sr-only"
                >

                <span
                  class="inline-flex rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[13px] text-[var(--muted)] transition group-hover:border-[var(--border-strong)] group-hover:text-[var(--text)] peer-checked:border-[var(--accent-deep)] peer-checked:bg-[var(--accent-soft)] peer-checked:font-medium peer-checked:text-[var(--accent-ink)]"
                >
                  {{ projectType.name }}
                </span>
              </label>
            </div>

            <p
              v-else
              class="mt-4 text-sm text-[var(--muted)]"
            >
              No project types are available yet.
            </p>

            <span
              v-if="fieldError('project_type_id')"
              class="mt-2 block text-xs text-[var(--danger)]"
            >
              {{ fieldError('project_type_id') }}
            </span>
          </fieldset>

          <fieldset class="mt-7">
            <legend class="text-[13px] font-medium text-[var(--text)]">
              Labels
              <span class="text-[12px] font-normal text-[var(--faint)]">
                Optional
              </span>
            </legend>

            <p class="mt-1 text-[12.5px] text-[var(--muted)]">
              Select any labels that describe what the project does.
            </p>

            <p
              v-if="loadingClassifications"
              class="mt-4 font-mono text-xs text-[var(--faint)]"
            >
              Loading labels…
            </p>

            <div
              v-else-if="labels.length"
              class="mt-4 flex flex-wrap gap-2"
            >
              <label
                v-for="label in labels"
                :key="label.id"
                class="group cursor-pointer"
              >
                <input
                  v-model="form.label_ids"
                  type="checkbox"
                  :value="label.id"
                  class="peer sr-only"
                >

                <span
                  class="inline-flex rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[13px] text-[var(--muted)] transition group-hover:border-[var(--border-strong)] group-hover:text-[var(--text)] peer-checked:border-[var(--accent-deep)] peer-checked:bg-[var(--accent-soft)] peer-checked:font-medium peer-checked:text-[var(--accent-ink)]"
                >
                  {{ label.name }}
                </span>
              </label>
            </div>

            <p
              v-else
              class="mt-4 text-sm text-[var(--muted)]"
            >
              No labels are available yet.
            </p>

            <span
              v-if="fieldError('label_ids')"
              class="mt-2 block text-xs text-[var(--danger)]"
            >
              {{ fieldError('label_ids') }}
            </span>
          </fieldset>
        </section>

        <!-- Capabilities -->
        <section>
          <div class="border-b border-[var(--border)] pb-3">
            <h2
              class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              Capabilities
            </h2>
          </div>

          <label
            class="mt-6 flex cursor-pointer items-start gap-3"
          >
            <input
              v-model="form.supports_e2ee"
              type="checkbox"
              class="mt-0.5 size-4 accent-[var(--accent-deep)]"
            >

            <span>
              <span
                class="flex items-center gap-2 text-sm font-medium text-[var(--text)]"
              >
                <LockClosedIcon
                  class="size-4 text-[var(--muted)]"
                />
                Supports encrypted rooms
              </span>

              <span
                class="mt-1 block max-w-xl text-[12.5px] leading-5 text-[var(--muted)]"
              >
                This project can operate in Matrix rooms with
                end-to-end encryption enabled.
              </span>
            </span>
          </label>
        </section>

        <!-- Actions -->
        <footer
          class="flex items-center justify-end gap-3 border-t border-[var(--border)] pt-6"
        >
          <RouterLink
            to="/dashboard"
            class="rounded-[9px] px-4 py-2.5 text-sm text-[var(--muted)] no-underline transition hover:bg-[var(--hover)] hover:text-[var(--text)]"
          >
            Cancel
          </RouterLink>

          <button
            type="submit"
            :disabled="cannotSubmit"
            class="rounded-[9px] bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-[#0e1012] transition hover:bg-[var(--accent-deep)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {{ submitting ? 'Publishing…' : 'Publish listing' }}
          </button>
        </footer>
      </div>

      <!-- Preview -->
      <aside class="hidden lg:block">
        <div class="sticky top-24">
          <!-- Preview heading -->
          <div class="flex items-center justify-between">
            <p
              class="font-mono text-[11px] font-medium uppercase tracking-[0.08em] text-[var(--faint)]"
            >
              Listing preview
            </p>

            <span
              class="font-mono text-[10px] uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              Draft
            </span>
          </div>

          <!-- Preview card -->
          <div
            class="mt-3 rounded-[14px] border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[var(--shadow)]"
          >
            <div class="flex gap-4">
              <div
                class="flex size-12 shrink-0 items-center justify-center rounded-[11px] bg-[var(--accent-soft)] text-base font-semibold text-[var(--accent-ink)]"
              >
                {{ previewInitial }}
              </div>

              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <h3
                    class="truncate text-[15px] font-semibold text-[var(--text)]"
                  >
                    {{ form.name.trim() || 'Project name' }}
                  </h3>

                  <span
                    v-if="form.name.trim()"
                    class="size-1.5 shrink-0 rounded-full bg-[var(--accent)]"
                    aria-label="Project"
                  />
                </div>

                <p
                  class="mt-2 text-[13px] leading-5 text-[var(--muted)]"
                >
                  {{
                    form.short_description.trim()
                      || 'Your short description will appear here.'
                  }}
                </p>

                <div
                  v-if="
                    form.project_type_id ||
                      selectedLabels.length ||
                      form.supports_e2ee
                  "
                  class="mt-4 flex flex-wrap gap-1.5"
                >
                  <span
                    v-if="form.project_type_id"
                    class="rounded-md bg-[var(--accent-soft)] px-2 py-1 text-[10px] font-medium text-[var(--accent-ink)]"
                  >
                    {{ projectTypes.find((item) => item.id === form.project_type_id)?.name }}
                  </span>

                  <span
                    v-for="label in selectedLabels"
                    :key="label.id"
                    class="rounded-md bg-[var(--sunk)] px-2 py-1 text-[10px] text-[var(--muted)]"
                  >
                    {{ label.name }}
                  </span>

                  <span
                    v-if="form.supports_e2ee"
                    class="inline-flex items-center gap-1 rounded-md bg-[var(--sunk)] px-2 py-1 text-[10px] text-[var(--muted)]"
                  >
                    <LockClosedIcon class="size-3" />
                    E2EE
                  </span>
                </div>
              </div>
            </div>
          </div>

          <p
            class="mt-3 text-[12px] leading-5 text-[var(--faint)]"
          >
            Preview of how the project will appear while browsing
            the directory.
          </p>

          <!-- Listing readiness -->
          <div
            class="mt-8 border-t border-[var(--border)] pt-5"
          >
            <div class="flex items-center justify-between gap-4">
              <p
                class="font-mono text-[10px] font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
              >
                Listing status
              </p>

              <span
                v-if="listingReady"
                class="font-mono text-[10px] font-medium uppercase tracking-[0.04em] text-[var(--success)]"
              >
                Ready
              </span>

              <span
                v-else
                class="font-mono text-[10px] text-[var(--faint)]"
              >
                {{ requiredCompleteCount }}/{{ requiredChecklist.length }}
                required
              </span>
            </div>

            <ul class="mt-4 space-y-2.5">
              <li
                v-for="item in checklist"
                :key="item.label"
                class="flex items-center justify-between gap-3 text-[12px]"
              >
                <span
                  class="flex items-center gap-2"
                  :class="
                    item.complete
                      ? 'text-[var(--text)]'
                      : 'text-[var(--muted)]'
                  "
                >
                  <span
                    class="flex size-4 items-center justify-center rounded-full border text-[9px]"
                    :class="
                      item.complete
                        ? 'border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent-ink)]'
                        : 'border-[var(--border-strong)]'
                    "
                  >
                    {{ item.complete ? '✓' : '' }}
                  </span>

                  {{ item.label }}
                </span>

                <span
                  v-if="!item.required"
                  class="font-mono text-[9px] uppercase text-[var(--faint)]"
                >
                  optional
                </span>
              </li>
            </ul>
          </div>
        </div>
      </aside>
    </form>
  </main>
</template>
