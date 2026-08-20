import { computed, reactive, ref, type Ref } from 'vue'
import type { Router } from 'vue-router'

import {
  ApiError,
  createProject,
  listLabels,
  listMyProjects,
  listProjectTypes,
  updateProject,
} from '../api/client'
import type { Label, ProjectCreate, ProjectType } from '../types/project'
import { projectPath } from '../utils/projectRoutes'

export function useProjectForm(
  router: Router,
  editingProjectId: Ref<string>,
) {
  const isEditing = computed(() => Boolean(editingProjectId.value))
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
  const loadingProject = ref(isEditing.value)
  const projectUnavailable = ref(false)
  const submitting = ref(false)
  const formError = ref('')
  const fieldErrors = ref<Record<string, string>>({})

  const selectedLabels = computed(() =>
    labels.value.filter((label) => form.label_ids.includes(label.id)),
  )
  const hasProjectLink = computed(() =>
    Boolean(form.repository_url?.trim() || form.website_url?.trim()),
  )
  const cannotSubmit = computed(() =>
    submitting.value ||
    loadingClassifications.value ||
    loadingProject.value ||
    projectUnavailable.value ||
    !form.name.trim() ||
    !form.short_description.trim() ||
    !form.description.trim() ||
    !form.project_type_id ||
    !hasProjectLink.value ||
    form.short_description.length > 160 ||
    form.description.length > 10000,
  )
  const checklist = computed(() => [
    { label: 'Name', complete: Boolean(form.name.trim()), required: true },
    {
      label: 'Short description',
      complete: Boolean(form.short_description.trim()),
      required: true,
    },
    { label: 'About', complete: Boolean(form.description.trim()), required: true },
    { label: 'Project link', complete: hasProjectLink.value, required: true },
    {
      label: 'Project type',
      complete: Boolean(form.project_type_id),
      required: true,
    },
    { label: 'Labels', complete: form.label_ids.length > 0, required: false },
    {
      label: 'Matrix room',
      complete: Boolean(form.matrix_server_url?.trim()),
      required: false,
    },
    { label: 'E2EE support', complete: form.supports_e2ee, required: false },
  ])
  const requiredChecklist = computed(() =>
    checklist.value.filter((item) => item.required),
  )
  const requiredCompleteCount = computed(() =>
    requiredChecklist.value.filter((item) => item.complete).length,
  )
  const projectReady = computed(() =>
    requiredChecklist.value.every((item) => item.complete),
  )

  function fieldError(field: string) {
    return fieldErrors.value[field]
  }

  function optionalValue(value: string | null) {
    return value?.trim() || null
  }

  async function load() {
    try {
      const [availableProjectTypes, availableLabels, ownedProjects] =
        await Promise.all([
          listProjectTypes(),
          listLabels(),
          isEditing.value ? listMyProjects() : Promise.resolve(null),
        ])
      projectTypes.value = availableProjectTypes
      labels.value = availableLabels

      if (isEditing.value) {
        const project = ownedProjects?.find(
          (item) => item.id === editingProjectId.value,
        )

        if (!project) {
          projectUnavailable.value = true
          formError.value =
            'This project was not found or you do not have permission to edit it.'
          return
        }

        Object.assign(form, {
          name: project.name,
          short_description: project.short_description,
          description: project.description,
          repository_url: project.repository_url,
          website_url: project.website_url,
          matrix_server_url: project.matrix_server_url,
          supports_e2ee: project.supports_e2ee,
          project_type_id: project.project_type.id,
          label_ids: project.labels.map((label) => label.id),
        })
      }
    } catch (error) {
      formError.value =
        error instanceof Error
          ? error.message
          : 'Could not load project classifications.'
    } finally {
      loadingClassifications.value = false
      loadingProject.value = false
    }
  }

  async function submit() {
    if (cannotSubmit.value) return

    submitting.value = true
    formError.value = ''
    fieldErrors.value = {}

    try {
      const input = {
        ...form,
        name: form.name.trim(),
        short_description: form.short_description.trim(),
        description: form.description.trim(),
        repository_url: optionalValue(form.repository_url),
        website_url: optionalValue(form.website_url),
        matrix_server_url: optionalValue(form.matrix_server_url),
      }
      const savedProject = isEditing.value
        ? await updateProject(editingProjectId.value, input)
        : await createProject(input)

      await router.push(projectPath(savedProject))
    } catch (error) {
      if (error instanceof ApiError && error.issues.length) {
        for (const issue of error.issues) {
          fieldErrors.value[String(issue.loc.at(-1))] = issue.msg.replace(
            /^Value error, /,
            '',
          )
        }
      } else {
        formError.value =
          error instanceof Error
            ? error.message
            : `Could not ${isEditing.value ? 'save' : 'publish'} the project.`
      }
    } finally {
      submitting.value = false
    }
  }

  return {
    cannotSubmit,
    checklist,
    fieldError,
    form,
    formError,
    isEditing,
    labels,
    load,
    loadingClassifications,
    loadingProject,
    projectReady,
    projectTypes,
    projectUnavailable,
    requiredChecklist,
    requiredCompleteCount,
    selectedLabels,
    submit,
    submitting,
  }
}
