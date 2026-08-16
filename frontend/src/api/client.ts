import type { Project, ProjectListItem } from '../types/project'

export interface CurrentUser {
  id: string
  matrix_id: string | null
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
    throw new Error(body?.detail ?? `Request failed with ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export function listProjects() {
  return request<ProjectListItem[]>('/projects/')
}

export function getProject(id: string) {
  return request<Project>(`/projects/${id}`)
}

export function getCurrentUser() {
  return request<CurrentUser>('/auth/me')
}

export function logout() {
  return request<void>('/auth/logout', { method: 'POST' })
}

export function listMyProjects() {
  return request<ProjectListItem[]>('/projects/mine/')
}

export function deleteProject(id: string) {
  return request<void>(`/projects/${id}`, { method: 'DELETE' })
}
