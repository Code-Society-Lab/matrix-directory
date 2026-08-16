export type Category = {
  id: string
  name: string
}

export type ProjectOwner = {
  id: string
  display_name: string | null
  matrix_id: string | null
  avatar_url: string | null
}

export type ProjectListItem = {
  id: string
  name: string
  description: string
  short_description: string
  repository_url: string | null
  website_url: string | null
  matrix_server_url: string | null
  supports_e2ee: boolean
  user_id: string
  categories: Category[]
  owner: ProjectOwner
}

export type Project = ProjectListItem