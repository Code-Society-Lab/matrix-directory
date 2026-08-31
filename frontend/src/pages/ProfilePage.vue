<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  watch,
} from 'vue'
import {
  ArrowTopRightOnSquareIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'

import {
  disconnectMatrixAvatar,
  getCurrentUser,
  updateMyProfile,
  type CurrentUser,
  type ProfileUpdate,
} from '../api/client'
import { currentUser } from '../auth'
import AvatarImage from '../components/AvatarImage.vue'
import MarkdownEditor from '../components/markdown/MarkdownEditor.vue'

const ABOUT_YOU_MAX_LENGTH = 1024

const matrixAccountUrl =
  import.meta.env.VITE_MATRIX_ACCOUNT_URL ??
  'https://account.matrix.org/account/'

const user = ref<CurrentUser | null>(null)
const matrixId = ref<string | null>(null)
const matrixAvatarUrl = ref<string | null>(null)
const disconnecting = ref(false)

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const saved = ref(false)

type FormFooterPosition = 'below' | 'visible' | 'above'

const formFooter = ref<HTMLElement | null>(null)
const formFooterPosition = ref<FormFooterPosition>('below')

const form = reactive<ProfileUpdate>({
  display_name: null,
  bio: null,
  avatar_url: null,
  github_url: null,
  website_url: null,
})

const initialForm = ref<ProfileUpdate | null>(null)

const aboutYou = computed({
  get: () => form.bio ?? '',
  set: (value: string) => {
    form.bio = value
  },
})

// The backend decides whether a Matrix avatar exists; the client never
// infers it from the shape of an avatar URL.
const usingMatrixAvatar = computed(
  () => !form.avatar_url && matrixAvatarUrl.value !== null,
)

const previewAvatarUrl = computed(
  () => form.avatar_url || matrixAvatarUrl.value,
)

function normalize(value: string | null): string | null {
  const result = value?.trim()

  return result || null
}

function snapshotForm(): ProfileUpdate {
  return {
    display_name: normalize(form.display_name),
    bio: normalize(form.bio),
    avatar_url: normalize(form.avatar_url),
    github_url: normalize(form.github_url),
    website_url: normalize(form.website_url),
  }
}

const isDirty = computed(() => {
  if (!initialForm.value) {
    return false
  }

  return (
    JSON.stringify(snapshotForm()) !==
    JSON.stringify(initialForm.value)
  )
})

const showFloatingSaveBar = computed(
  () =>
    user.value !== null &&
    formFooterPosition.value === 'below',
)

function applyProfile(profile: CurrentUser['profile']) {
  matrixId.value = profile?.matrix_id ?? null
  matrixAvatarUrl.value = profile?.matrix_avatar_url ?? null

  form.display_name = profile?.display_name ?? null
  form.bio = profile?.bio ?? null
  form.avatar_url = profile?.custom_avatar_url ?? null
  form.github_url = profile?.github_url ?? null
  form.website_url = profile?.website_url ?? null
}

function useMatrixAvatar() {
  form.avatar_url = null
}

async function disconnectMatrix() {
  if (disconnecting.value) {
    return
  }

  disconnecting.value = true
  error.value = ''

  try {
    const profile = await disconnectMatrixAvatar()

    applyProfile(profile)
    initialForm.value = snapshotForm()

    if (user.value) {
      user.value.profile = profile
    }

    if (currentUser.value) {
      currentUser.value.profile = profile
    }
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not disconnect your Matrix avatar.'
  } finally {
    disconnecting.value = false
  }
}

async function load() {
  loading.value = true
  error.value = ''

  try {
    user.value = await getCurrentUser()

    applyProfile(user.value.profile)

    initialForm.value = snapshotForm()
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not load your profile.'
  } finally {
    loading.value = false
  }
}

let savedTimer: ReturnType<typeof setTimeout> | undefined
let footerObserver: IntersectionObserver | undefined

watch(isDirty, (dirty) => {
  if (!dirty) {
    return
  }

  saved.value = false
  clearTimeout(savedTimer)
})

watch(
  formFooter,
  (element) => {
    footerObserver?.disconnect()
    footerObserver = undefined

    if (!element) {
      formFooterPosition.value = 'below'
      return
    }

    footerObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          formFooterPosition.value = 'visible'
          return
        }

        const viewportBottom =
          entry.rootBounds?.bottom ??
          window.innerHeight

        if (entry.boundingClientRect.top >= viewportBottom) {
          formFooterPosition.value = 'below'
          return
        }

        formFooterPosition.value = 'above'
      },
      {
        threshold: 0,
      },
    )

    footerObserver.observe(element)
  },
  {
    flush: 'post',
  },
)

async function save() {
  if (saving.value || !isDirty.value) {
    return
  }

  saving.value = true
  saved.value = false
  error.value = ''

  try {
    const profile = await updateMyProfile(snapshotForm())

    applyProfile(profile)

    initialForm.value = snapshotForm()

    if (user.value) {
      user.value.profile = profile
    }

    if (currentUser.value) {
      currentUser.value.profile = profile
    }

    saved.value = true

    clearTimeout(savedTimer)

    savedTimer = setTimeout(() => {
      saved.value = false
    }, 3000)
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not save your profile.'
  } finally {
    saving.value = false
  }
}

onMounted(load)

onBeforeUnmount(() => {
  clearTimeout(savedTimer)
  footerObserver?.disconnect()
})
</script>

<template>
  <main
    class="mx-auto max-w-[1120px] px-5 py-10 pb-28 sm:px-8 sm:pb-24"
  >
    <div class="max-w-2xl">
      <p
        class="font-mono text-xs font-medium uppercase tracking-[0.08em] text-[var(--accent-ink)]"
      >
        Account
      </p>

      <h1
        class="mt-3 font-display text-[34px] font-semibold tracking-[-0.02em] text-[var(--text)]"
      >
        My profile
      </h1>

      <p class="mt-2 text-[15px] leading-6 text-[var(--muted)]">
        Manage how you appear alongside the projects you publish.
      </p>
    </div>

    <div
      v-if="loading"
      class="mt-8 font-mono text-xs text-[var(--faint)]"
    >
      Loading profile…
    </div>

    <template v-else>
      <div
        v-if="error"
        class="mt-8 flex items-center gap-2 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]"
      >
        <ExclamationTriangleIcon class="size-4 shrink-0" />
        {{ error }}
      </div>

      <form
        v-if="user"
        class="mt-8 overflow-hidden rounded-[14px] border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow)]"
        @submit.prevent="save"
      >
        <!-- Identity -->
        <section
          class="p-6 sm:flex sm:items-center sm:gap-6 sm:p-7"
        >
          <div class="flex min-w-0 items-center gap-4">
            <div
              class="grid size-[64px] shrink-0 place-items-center overflow-hidden rounded-[16px] bg-[var(--accent-soft)] font-display text-xl font-semibold text-[var(--accent-ink)]"
            >
              <AvatarImage
                :src="previewAvatarUrl"
                :name="form.display_name"
              />
            </div>

            <div class="min-w-0 flex-1">
              <h2
                class="truncate font-display text-lg font-semibold tracking-[-0.01em] text-[var(--text)]"
              >
                {{ form.display_name || 'Your profile' }}
              </h2>

              <p
                v-if="matrixId"
                class="mt-1 truncate font-mono text-xs text-[var(--muted)]"
              >
                {{ matrixId }}
              </p>

              <div
                v-if="matrixId"
                class="mt-2 flex flex-wrap items-center gap-2"
              >
                <span
                  class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium"
                  :class="
                    user.profile?.matrix_id_verified
                      ? 'bg-[var(--accent-soft)] text-[var(--accent-ink)]'
                      : 'bg-[var(--sunk)] text-[var(--muted)]'
                  "
                >
                  {{
                    user.profile?.matrix_id_verified
                      ? '✓ Verified'
                      : 'Unverified'
                  }}
                </span>

                <span
                  aria-hidden="true"
                  class="text-[var(--faint)]"
                >
                  ·
                </span>

                <a
                  :href="matrixAccountUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-1 text-[12px] text-[var(--muted)] no-underline transition hover:text-[var(--text)]"
                >
                  Manage account
                  <ArrowTopRightOnSquareIcon class="size-3.5" />
                </a>
              </div>
            </div>
          </div>

          <RouterLink
            :to="`/profiles/${user.id}`"
            class="mt-5 inline-flex w-full shrink-0 items-center justify-center gap-2 rounded-[9px] border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-[13px] font-medium text-[var(--muted)] no-underline transition hover:border-[var(--border-strong)] hover:bg-[var(--hover)] hover:text-[var(--text)] sm:ml-auto sm:mt-0 sm:w-auto"
          >
            View public profile
          </RouterLink>
        </section>

        <!-- Profile -->
        <section
          class="border-t border-[var(--border)] p-6"
        >
          <div
            class="border-b border-[var(--border)] pb-3"
          >
            <h2
              class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              Profile
            </h2>
          </div>

          <div class="mt-6 max-w-lg">
            <label class="block">
              <span
                class="text-[13px] font-medium text-[var(--text)]"
              >
                Display name
              </span>

              <input
                v-model="form.display_name"
                type="text"
                maxlength="100"
                placeholder="PenguinBoi"
                class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
              >
            </label>
          </div>

          <label class="mt-5 block">
            <div
              class="mb-2 flex items-center justify-between gap-4"
            >
              <span
                class="text-[13px] font-medium text-[var(--text)]"
              >
                About you
              </span>

              <span
                class="font-mono text-[11px] text-[var(--faint)]"
              >
                {{ form.bio?.length ?? 0 }}/{{ ABOUT_YOU_MAX_LENGTH }}
              </span>
            </div>

            <MarkdownEditor
              v-model="aboutYou"
              :maxlength="ABOUT_YOU_MAX_LENGTH"
              placeholder="Tell people what you build and what you're interested in."
              aria-label="About you"
            />
          </label>
        </section>

        <!-- Avatar -->
        <section
          class="border-t border-[var(--border)] p-6"
        >
          <div
            class="border-b border-[var(--border)] pb-3"
          >
            <h2
              class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              Avatar
            </h2>
          </div>

          <div class="mt-6 flex items-center gap-4">
            <div
              class="grid size-12 shrink-0 place-items-center overflow-hidden rounded-[12px] bg-[var(--accent-soft)] font-display text-sm font-semibold text-[var(--accent-ink)]"
            >
              <AvatarImage
                :src="previewAvatarUrl"
                :name="form.display_name"
              />
            </div>

            <p class="min-w-0 flex-1 text-[12px] text-[var(--muted)]">
              <template v-if="usingMatrixAvatar">
                Using your Matrix profile avatar.
              </template>

              <template v-else-if="form.avatar_url">
                Using a custom image.
              </template>

              <template v-else>
                No avatar set.
              </template>
            </p>

            <button
              v-if="!usingMatrixAvatar && matrixAvatarUrl"
              type="button"
              class="shrink-0 cursor-pointer rounded-[8px] border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[12px] font-medium text-[var(--muted)] transition hover:border-[var(--border-strong)] hover:bg-[var(--hover)] hover:text-[var(--text)]"
              @click="useMatrixAvatar"
            >
              Use Matrix avatar
            </button>
          </div>

          <label class="mt-5 block max-w-lg">
            <span
              class="text-[13px] font-medium text-[var(--text)]"
            >
              Custom image URL
            </span>

            <input
              v-model="form.avatar_url"
              type="url"
              maxlength="500"
              placeholder="https://example.com/avatar.png"
              class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
            >

            <p
              class="mt-1.5 text-[11px] text-[var(--faint)]"
            >
              Use a publicly accessible image URL. Leaving this empty falls back
              to your Matrix avatar when one is connected.
            </p>
          </label>

          <div
            v-if="matrixAvatarUrl"
            class="mt-5 border-t border-[var(--border)] pt-5"
          >
            <p class="text-[12px] text-[var(--muted)]">
              Matrix Directory stores an encrypted Matrix token so it can load
              your avatar. Disconnecting deletes that token.
            </p>

            <button
              type="button"
              :disabled="disconnecting"
              class="mt-3 cursor-pointer rounded-[8px] border border-[var(--danger-border)] bg-[var(--surface)] px-3 py-1.5 text-[12px] font-medium text-[var(--danger)] transition hover:bg-[var(--danger-soft)] disabled:cursor-not-allowed disabled:opacity-60"
              @click="disconnectMatrix"
            >
              {{ disconnecting ? 'Disconnecting…' : 'Disconnect Matrix avatar' }}
            </button>
          </div>
        </section>

        <!-- Links -->
        <section
          class="border-t border-[var(--border)] p-6"
        >
          <div
            class="border-b border-[var(--border)] pb-3"
          >
            <h2
              class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]"
            >
              Links
            </h2>
          </div>

          <div class="mt-6">
            <div class="grid gap-5 sm:grid-cols-2">
              <label>
                <span
                  class="text-[13px] font-medium text-[var(--text)]"
                >
                  GitHub
                </span>

                <input
                  v-model="form.github_url"
                  type="url"
                  maxlength="150"
                  placeholder="https://github.com/username"
                  class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
                >
              </label>

              <label>
                <span
                  class="text-[13px] font-medium text-[var(--text)]"
                >
                  Website
                </span>

                <input
                  v-model="form.website_url"
                  type="url"
                  maxlength="150"
                  placeholder="https://example.com"
                  class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
                >
              </label>
            </div>
          </div>
        </section>

        <!-- Real form footer -->
        <footer
          ref="formFooter"
          class="flex min-h-16 items-center justify-between gap-4 border-t border-[var(--border)] bg-[var(--sunk)] px-6 py-4 sm:px-7"
        >
          <div
            class="min-h-5"
            aria-live="polite"
          >
            <p
              v-if="saved"
              class="flex items-center gap-2 text-sm text-[var(--accent-ink)]"
            >
              <CheckCircleIcon class="size-4" />
              Changes saved
            </p>
          </div>

          <button
            type="submit"
            :disabled="saving || !isDirty"
            class="cursor-pointer rounded-[9px] bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-[#0e1012] transition hover:bg-[var(--accent-deep)] disabled:cursor-not-allowed disabled:opacity-65"
          >
            {{ saving ? 'Saving…' : 'Save changes' }}
          </button>
        </footer>
      </form>

      <!-- Mobile floating save bar -->
      <Transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="translate-y-full opacity-0"
        enter-to-class="translate-y-0 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="translate-y-0 opacity-100"
        leave-to-class="translate-y-full opacity-0"
      >
        <div
          v-if="showFloatingSaveBar"
          class="fixed inset-x-0 bottom-0 z-30 border-t border-[var(--border)] bg-[var(--sunk)]/95 px-5 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] shadow-[0_-4px_16px_rgba(0,0,0,0.04)] backdrop-blur sm:hidden"
        >
          <div
            class="mx-auto flex max-w-[1120px] items-center justify-between gap-4"
          >
            <div
              class="min-h-5"
              aria-live="polite"
            >
              <p
                v-if="saved"
                class="flex items-center gap-2 text-sm text-[var(--accent-ink)]"
              >
                <CheckCircleIcon class="size-4" />
                Changes saved
              </p>
            </div>

            <button
              type="button"
              :disabled="saving || !isDirty"
              class="ml-auto cursor-pointer rounded-[9px] bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-[#0e1012] transition hover:bg-[var(--accent-deep)] disabled:cursor-not-allowed disabled:opacity-65"
              @click="save"
            >
              {{ saving ? 'Saving…' : 'Save changes' }}
            </button>
          </div>
        </div>
      </Transition>
    </template>
  </main>
</template>