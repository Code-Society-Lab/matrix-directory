import { ref } from 'vue'
import { getCurrentUser, logout as requestLogout, type CurrentUser } from './api/client'

export const currentUser = ref<CurrentUser | null>(null)
export const authLoaded = ref(false)

export async function loadCurrentUser() {
  try {
    currentUser.value = await getCurrentUser()
  } catch {
    currentUser.value = null
  } finally {
    authLoaded.value = true
  }
}

export async function logout() {
  await requestLogout()
  currentUser.value = null
}
