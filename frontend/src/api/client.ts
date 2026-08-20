import type {
  Label,
  Project,
  ProjectCreate,
  ProjectListItem,
  ProjectType,
} from '../types/project'

interface Profile {
  matrix_id: string | null
  matrix_id_verified: boolean
  display_name: string | null
  bio: string | null
  avatar_url: string | null
  github_url: string | null
  website_url: string | null
}

export interface CurrentUser {
  id: string
  profile: Profile | null
}

export interface ProfileUpdate {
  matrix_id: string | null
  display_name: string | null
  bio: string | null
  avatar_url: string | null
  github_url: string | null
  website_url: string | null
}

export interface PublicProfile extends Profile {
  user_id: string | null
  projects: ProjectListItem[]
}

type ValidationIssue = {
  loc: Array<string | number>
  msg: string
  type: string
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly issues: ValidationIssue[] = [],
  ) {
    super(message)
  }
}

const API_URL = import.meta.env.VITE_API_URL ?? '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    credentials: 'include',
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const issues = Array.isArray(body?.detail) ? body.detail : []
    const message =
      typeof body?.detail === 'string'
        ? body.detail
        : `Request failed with ${response.status}`

    throw new ApiError(message, response.status, issues)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

type ProjectQuery = {
  query?: string
  projectType?: string
  label?: string
  limit?: number
  offset?: number
}

export function listProjects(filters: ProjectQuery = {}) {
  const params = new URLSearchParams()

  if (filters.query) params.set('q', filters.query)
  if (filters.projectType) params.set('project_type', filters.projectType)
  if (filters.label) params.set('label', filters.label)
  if (filters.limit !== undefined) params.set('limit', String(filters.limit))
  if (filters.offset !== undefined) params.set('offset', String(filters.offset))

  const queryString = params.toString()
  const path = queryString ? `/projects/?${queryString}` : '/projects/'

  return request<ProjectListItem[]>(path)
}

export function getProject(id: string) {
  return request<Project>(`/projects/${id}`)
}

export function getCurrentUser() {
  return request<CurrentUser>('/auth/me')
}

export function updateMyProfile(profile: ProfileUpdate) {
  return request<Profile>('/profile/me', {
    method: 'PUT',
    body: JSON.stringify(profile),
  })
}

export function getPublicProfile(userId: string) {
  return request<PublicProfile>(`/profiles/${userId}`)
}

export function logout() {
  return request<void>('/auth/logout', {
    method: 'POST',
  })
}

export function listMyProjects() {
  return request<ProjectListItem[]>('/projects/mine/')
}

export function deleteProject(id: string) {
  return request<void>(`/projects/${id}`, {
    method: 'DELETE',
  })
}

export function listRandomProjects(limit = 6) {
  const params = new URLSearchParams({
    limit: String(limit),
  })

  return request<ProjectListItem[]>(
    `/projects/random/?${params.toString()}`,
  )
}

export function countProjects() {
  return request<number>('/projects/count/')
}

export function listProjectTypes() {
  return request<ProjectType[]>('/project-types/')
}

export function listLabels() {
  return request<Label[]>('/labels/')
}

export function createProject(input: ProjectCreate) {
  return request<Project>('/projects/', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateProject(id: string, input: ProjectCreate) {
  return request<Project>(`/projects/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}
