import { createRouter, createWebHistory } from 'vue-router'
import BotDetailPage from '../pages/BotDetailPage.vue'
import HomePage from '../pages/HomePage.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomePage },
    { path: '/bots/:id', component: BotDetailPage },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
