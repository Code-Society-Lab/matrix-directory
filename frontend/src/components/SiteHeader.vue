<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'

import { currentUser, logout } from '../auth'

const router = useRouter()

async function signOut() {
  await logout()
  await router.push('/')
}
</script>

<template>
  <header class="border-b border-zinc-200 bg-white">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
      <RouterLink
        to="/"
        class="text-sm font-semibold tracking-tight text-zinc-950"
      >
        Matrix Directory
      </RouterLink>

      <nav class="flex items-center gap-4 text-sm text-zinc-600">
        <RouterLink
          to="/"
          class="font-medium text-zinc-800 hover:text-zinc-950"
        >
          Browse
        </RouterLink>
        <RouterLink
          to="#"
          class="font-medium text-zinc-800 hover:text-zinc-950"
          disabled
          title="Coming soon"
        >
          Docs
        </RouterLink>
        <RouterLink
          v-if="currentUser"
          to="/dashboard"
          class="font-medium text-zinc-800 hover:text-zinc-950"
        >
          {{ currentUser.matrix_id ?? 'Dashboard' }}
        </RouterLink>

        <div class="h-5 w-px bg-zinc-300" />

        <button
          v-if="currentUser"
          class="auth-button"
          @click="signOut"
        >
          Sign out
        </button>
        <RouterLink
          v-else
          to="/login"
          class="auth-button"
        >
          Sign in
        </RouterLink>
      </nav>
    </div>
  </header>
</template>
