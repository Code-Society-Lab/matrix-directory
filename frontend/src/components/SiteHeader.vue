<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import {
  ArrowRightStartOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'

import { currentUser, logout } from '../auth'

import logoUrl from '../assets/matrix-directory-mark.svg'

const docsUrl =
  import.meta.env.VITE_DOCS_URL ??
  (import.meta.env.DEV ? 'http://127.0.0.1:8001' : '/docs/')

const router = useRouter()
const route = useRoute()

const menuOpen = ref(false)
const mobileMenu = ref<HTMLElement | null>(null)

function handleClickOutside(event: PointerEvent) {
  if (!menuOpen.value) {
    return
  }

  const target = event.target as Node

  if (
    mobileMenu.value &&
    !mobileMenu.value.contains(target)
  ) {
    menuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('pointerdown', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', handleClickOutside)
})

const profileInitial = computed(() => {
  const name =
    currentUser.value?.profile?.display_name ||
    currentUser.value?.profile?.matrix_id

  if (!name) {
    return 'P'
  }

  return name
    .replace(/^@/, '')
    .charAt(0)
    .toUpperCase()
})

const profileLabel = computed(() =>
  currentUser.value?.profile?.display_name ||
  currentUser.value?.profile?.matrix_id ||
  'Profile',
)

function isActive(path: string) {
  return route.path.startsWith(path)
}

async function signOut() {
  menuOpen.value = false

  await logout()
  await router.push('/')
}

// Close the mobile menu after navigation.
watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
  },
)
</script>

<template>
  <header
    class="sticky top-0 z-20 border-b border-[var(--border)] bg-[color:var(--bg)/88] backdrop-blur-[10px]"
  >
    <div
      class="relative mx-auto flex h-[68px] max-w-[1120px] items-center justify-between gap-6 px-5 sm:px-8"
    >
      <!-- Brand -->
      <RouterLink
        to="/"
        class="flex min-w-0 items-center gap-2.5 no-underline"
      >
        <img
          :src="logoUrl"
          alt="Matrix Directory Logo"
          class="size-[30px] text-[var(--accent-ink)]"
        >

        <div class="flex min-w-0 items-baseline gap-2">
          <span
            class="font-display text-[17px] font-semibold tracking-[-0.01em] text-[var(--text)]"
          >
            Matrix Directory
          </span>
        </div>
      </RouterLink>

      <!-- Desktop navigation -->
      <nav class="hidden items-center gap-1 sm:flex">
        <RouterLink
          to="/browse"
          class="rounded-lg px-3 py-2 text-sm no-underline transition"
          :class="
            isActive('/browse')
              ? 'bg-[var(--sunk)] font-medium text-[var(--text)]'
              : 'text-[var(--muted)] hover:bg-[var(--sunk)] hover:text-[var(--text)]'
          "
        >
          Browse
        </RouterLink>

        <a
          :href="docsUrl"
          class="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[var(--muted)] no-underline transition hover:bg-[var(--sunk)] hover:text-[var(--text)]"
        >
          Docs
        </a>

        <RouterLink
          v-if="currentUser"
          to="/dashboard"
          class="rounded-lg px-3 py-2 text-sm no-underline transition"
          :class="
            isActive('/dashboard')
              ? 'bg-[var(--sunk)] font-medium text-[var(--text)]'
              : 'text-[var(--muted)] hover:bg-[var(--sunk)] hover:text-[var(--text)]'
          "
        >
          Dashboard
        </RouterLink>

        <div
          class="mx-2 h-[22px] w-px bg-[var(--border)]"
        />

        <!-- Signed in -->
        <template v-if="currentUser">
          <RouterLink
            to="/profile"
            class="flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)] p-1 pr-3 no-underline transition hover:border-[var(--border-strong)]"
          >
            <div
              class="grid size-[28px] shrink-0 place-items-center overflow-hidden rounded-full bg-[var(--accent-soft)] text-xs font-semibold text-[var(--accent-ink)]"
            >
              <img
                v-if="currentUser.profile?.avatar_url"
                :src="currentUser.profile.avatar_url"
                alt=""
                class="size-full object-cover"
              >

              <span v-else>
                {{ profileInitial }}
              </span>
            </div>

            <span
              class="hidden max-w-[160px] truncate font-mono text-[11.5px] text-[var(--muted)] lg:block"
            >
              {{ profileLabel }}
            </span>
          </RouterLink>

          <button
            type="button"
            aria-label="Sign out"
            title="Sign out"
            class="ml-1 grid size-[34px] cursor-pointer place-items-center rounded-full text-[var(--muted)] transition hover:bg-[var(--sunk)] hover:text-[var(--text)]"
            @click="signOut"
          >
            <ArrowRightStartOnRectangleIcon class="size-[17px]" />
          </button>
        </template>

        <!-- Signed out -->
        <RouterLink
          v-else
          to="/login"
          class="ml-1 rounded-[9px] bg-[var(--accent)] px-4 py-2.5 text-sm font-medium text-[#0e1012] no-underline transition hover:bg-[var(--accent-deep)]"
        >
          Sign in
        </RouterLink>
      </nav>

      <!-- Mobile navigation -->
      <div
        ref="mobileMenu"
        class="sm:hidden"
      >
        <!-- Mobile menu button -->
        <button
          type="button"
          class="grid size-9 cursor-pointer place-items-center rounded-[9px] border border-[var(--border)] bg-[var(--surface)] text-[var(--muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text)] sm:hidden"
          aria-label="Toggle navigation"
          :aria-expanded="menuOpen"
          @click="menuOpen = !menuOpen"
        >
          <XMarkIcon
            v-if="menuOpen"
            class="size-5"
          />

          <Bars3Icon
            v-else
            class="size-5"
          />
        </button>

        <!-- Mobile dropdown -->
        <div
          v-if="menuOpen"
          class="absolute left-5 right-5 top-[58px] overflow-hidden rounded-[14px] border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow)] sm:hidden"
        >
          <!-- User -->
          <RouterLink
            v-if="currentUser"
            to="/profile"
            class="flex items-center gap-3 border-b border-[var(--border)] px-4 py-4 no-underline"
          >
            <div
              class="grid size-9 shrink-0 place-items-center overflow-hidden rounded-full bg-[var(--accent-soft)] text-sm font-semibold text-[var(--accent-ink)]"
            >
              <img
                v-if="currentUser.profile?.avatar_url"
                :src="currentUser.profile.avatar_url"
                alt=""
                class="size-full object-cover"
              >

              <span v-else>
                {{ profileInitial }}
              </span>
            </div>

            <div class="min-w-0">
              <p
                class="truncate text-sm font-medium text-[var(--text)]"
              >
                {{
                  currentUser.profile?.display_name ??
                    'Your profile'
                }}
              </p>

              <p
                v-if="currentUser.profile?.matrix_id"
                class="mt-0.5 truncate font-mono text-[11px] text-[var(--faint)]"
              >
                {{ currentUser.profile.matrix_id }}
              </p>
            </div>
          </RouterLink>

          <!-- Links -->
          <nav class="p-2">
            <RouterLink
              to="/browse"
              class="flex rounded-[8px] px-3 py-2.5 text-sm no-underline transition"
              :class="
                isActive('/browse')
                  ? 'bg-[var(--sunk)] font-medium text-[var(--text)]'
                  : 'text-[var(--muted)] hover:bg-[var(--sunk)] hover:text-[var(--text)]'
              "
            >
              Browse
            </RouterLink>

            <RouterLink
              v-if="currentUser"
              to="/dashboard"
              class="flex rounded-[8px] px-3 py-2.5 text-sm no-underline transition"
              :class="
                isActive('/dashboard')
                  ? 'bg-[var(--sunk)] font-medium text-[var(--text)]'
                  : 'text-[var(--muted)] hover:bg-[var(--sunk)] hover:text-[var(--text)]'
              "
            >
              Dashboard
            </RouterLink>

            <RouterLink
              v-if="currentUser"
              to="/profile"
              class="flex rounded-[8px] px-3 py-2.5 text-sm no-underline transition"
              :class="
                isActive('/profile')
                  ? 'bg-[var(--sunk)] font-medium text-[var(--text)]'
                  : 'text-[var(--muted)] hover:bg-[var(--sunk)] hover:text-[var(--text)]'
              "
            >
              Profile
            </RouterLink>

            <a
              :href="docsUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="flex rounded-[8px] px-3 py-2.5 text-sm text-[var(--muted)] no-underline transition hover:bg-[var(--sunk)] hover:text-[var(--text)]"
              @click="menuOpen = false"
            >
              Docs
            </a>
          </nav>

          <!-- Mobile auth action -->
          <div
            class="border-t border-[var(--border)] bg-[var(--sunk)] p-2"
          >
            <button
              v-if="currentUser"
              type="button"
              class="flex w-full cursor-pointer items-center gap-2 rounded-[8px] px-3 py-2.5 text-left text-sm text-[var(--muted)] transition hover:bg-[var(--surface)] hover:text-[var(--text)]"
              @click="signOut"
            >
              <ArrowRightStartOnRectangleIcon class="size-4" />
              Sign out
            </button>

            <RouterLink
              v-else
              to="/login"
              class="flex w-full items-center justify-center rounded-[8px] bg-[var(--accent)] px-4 py-2.5 text-sm font-medium text-[#0e1012] no-underline"
            >
              Sign in
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>
