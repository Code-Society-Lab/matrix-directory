<script setup lang="ts">
import { RouterView } from 'vue-router'
import SiteHeader from './components/SiteHeader.vue'
</script>

<template>
  <div class="min-h-screen bg-zinc-50">
    <SiteHeader />
    <RouterView />
  </div>
</template>
