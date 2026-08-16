import { createRouter, createWebHistory } from 'vue-router'

import BotDetailPage from '../pages/BotDetailPage.vue'
import HomePage from '../pages/HomePage.vue'
import LoginPage from '../pages/LoginPage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import { authLoaded, currentUser, loadCurrentUser } from '../auth'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomePage },
    { path: '/bots/:id', component: BotDetailPage },
    { path: '/login', component: LoginPage },
    { path: '/dashboard', component: DashboardPage, meta: { requiresAuth: true } },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  if (!authLoaded.value) await loadCurrentUser()
  if (to.meta.requiresAuth && !currentUser.value) {
    return { path: '/login' }
  }
  if (to.path === '/login' && currentUser.value) {
    return { path: '/dashboard' }
  }
})
