import { ref } from 'vue'

import { listLabels, listProjects, listProjectTypes } from '../api/client'
import type { ProjectListItem } from '../types/project'

export function useProjectDirectory() {
  const projects = ref<ProjectListItem[]>([])
  const query = ref('')
  const projectTypeFilter = ref('')
  const labelFilter = ref('')
  const loading = ref(true)
  const error = ref('')
  const projectTypes = ref<string[]>([])
  const labels = ref<string[]>([])
  let projectsRequestId = 0

  function clearFilters() {
    query.value = ''
    projectTypeFilter.value = ''
    labelFilter.value = ''
  }

  async function loadProjects() {
    projectsRequestId += 1
    const requestId = projectsRequestId
    loading.value = true
    error.value = ''

    try {
      const result = await listProjects({
        query: query.value.trim() || undefined,
        projectType: projectTypeFilter.value || undefined,
        label: labelFilter.value || undefined,
        limit: 50,
      })

      if (requestId === projectsRequestId) projects.value = result
    } catch (err) {
      if (requestId === projectsRequestId) {
        error.value =
          err instanceof Error ? err.message : 'Could not load projects.'
      }
    } finally {
      if (requestId === projectsRequestId) loading.value = false
    }
  }

  async function loadFilterOptions() {
    const [types, availableLabels] = await Promise.all([
      listProjectTypes(),
      listLabels(),
    ])

    projectTypes.value = types.map((type) => type.name)
    labels.value = availableLabels.map((label) => label.name)
  }

  async function loadDirectory() {
    try {
      await Promise.all([loadProjects(), loadFilterOptions()])
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Could not load filters.'
      loading.value = false
    }
  }

  return {
    projects,
    query,
    projectTypeFilter,
    labelFilter,
    loading,
    error,
    projectTypes,
    labels,
    clearFilters,
    loadProjects,
    loadDirectory,
  }
}
