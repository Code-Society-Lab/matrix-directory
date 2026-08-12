export type Category = {
  id: string
  name: string
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
}

export type Project = ProjectListItem
