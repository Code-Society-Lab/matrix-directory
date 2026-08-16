<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const loginUrl = `${import.meta.env.VITE_API_URL ?? '/api'}/auth/matrix/login`
</script>

<template>
  <main class="mx-auto max-w-xl px-5 py-12">
    <h1 class="text-3xl font-semibold tracking-tight text-zinc-950">
      Sign in with Matrix
    </h1>
    <p class="mt-3 leading-7 text-zinc-600">
      Continue securely with your matrix.org account. The directory never receives your password or a Matrix access token.
    </p>

    <p
      v-if="route.query.error"
      class="mt-6 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700"
    >
      {{ route.query.error }}
    </p>

    <a
      :href="loginUrl"
      class="mt-7 inline-block rounded-md bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-zinc-700"
    >
      Continue with Matrix
    </a>
  </main>
</template>
