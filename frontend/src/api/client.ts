import type { Project, ProjectListItem } from '../types/project'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `Request failed with ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function listProjects() {
  return request<ProjectListItem[]>('/projects/')
}

export function getProject(id: string) {
  return request<Project>(`/projects/${id}`)
}
