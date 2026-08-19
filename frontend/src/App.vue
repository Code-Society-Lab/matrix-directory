<script setup lang="ts">
import { RouterView } from 'vue-router'
import SiteHeader from './components/SiteHeader.vue'
import SiteFooter from './components/SiteFooter.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-zinc-50">
    <SiteHeader />
    <div class="flex-1">
      <RouterView />
    </div>
    <SiteFooter />
  </div>
</template>
