<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="border-b border-zinc-200 bg-white">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
      <RouterLink
        to="/"
        class="text-sm font-semibold tracking-tight text-zinc-950"
      >
        Matrix Bot Directory
      </RouterLink>

      <nav class="flex items-center gap-4 text-sm text-zinc-600">
        <RouterLink
          to="/"
          class="rounded-md border border-zinc-300 bg-white px-3 py-1.5 font-medium text-zinc-800 hover:bg-zinc-50"
        >
          Browse
        </RouterLink>
      </nav>
    </div>
  </header>
</template>
