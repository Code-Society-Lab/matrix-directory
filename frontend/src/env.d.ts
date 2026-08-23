/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_MATRIX_ACCOUNT_URL?: string
  readonly VITE_DOCS_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
