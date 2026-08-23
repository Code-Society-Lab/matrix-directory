import { createRouter, createWebHistory } from 'vue-router'

import HomePage from '../pages/HomePage.vue'
import LoginPage from '../pages/LoginPage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import { authLoaded, currentUser, loadCurrentUser } from '../auth'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomePage },
    {
      path: '/browse',
      component: () => import('../pages/BrowsePage.vue'),
    },
    {
      path: '/projects/:id',
      alias: [
        '/bots/:id',
        '/bridges/:id',
        '/clients/:id',
        '/frameworks/:id',
        '/integrations/:id',
        '/sdks/:id',
        '/servers/:id',
      ],
      component: () => import('../pages/ProjectDetailPage.vue'),
    },
    {
      path: '/projects/:id/edit',
      component: () => import('../pages/SubmitPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profiles/:id',
      component: () => import('../pages/PublicProfilePage.vue'),
    },
    { path: '/login', component: LoginPage },
    {
      path: '/account/profile',
      component: () => import('../pages/ProfilePage.vue'),
      meta: { requiresAuth: true },
    },
    { path: '/dashboard', component: DashboardPage, meta: { requiresAuth: true } },
    {
      path: '/submit',
      component: () => import('../pages/SubmitPage.vue'),
      meta: { requiresAuth: true },
    },
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
