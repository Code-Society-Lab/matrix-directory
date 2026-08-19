import type { ProjectListItem } from '../types/project'

const projectTypePaths: Record<string, string> = {
  Bot: 'bots',
  Bridges: 'bridges',
  Clients: 'clients',
  Framework: 'frameworks',
  Integrations: 'integrations',
  SDK: 'sdks',
  Server: 'servers',
}

export function projectPath(
  project: Pick<ProjectListItem, 'id' | 'project_type'>,
) {
  const segment = projectTypePaths[project.project_type.name] ?? 'projects'
  return `/${segment}/${project.id}`
}
