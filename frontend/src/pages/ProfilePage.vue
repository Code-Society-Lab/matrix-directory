<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import {
  ArrowTopRightOnSquareIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'

import {
  getCurrentUser,
  updateMyProfile,
  type CurrentUser,
  type ProfileUpdate,
} from '../api/client'
import { currentUser } from '../auth'
import MarkdownEditor from '../components/markdown/MarkdownEditor.vue'

const user = ref<CurrentUser | null>(null)
const matrixId = ref<string | null>(null)

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const saved = ref(false)

const form = reactive<ProfileUpdate>({
  display_name: null,
  bio: null,
  avatar_url: null,
  github_url: null,
  website_url: null,
})

const aboutYou = computed({
  get: () => form.bio ?? '',
  set: (value: string) => {
    form.bio = value
  },
})

const initials = computed(() => {
  const name = form.display_name?.trim()

  if (!name) {
    return '?'
  }

  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
})

function normalize(value: string | null): string | null {
  const result = value?.trim()
  return result || null
}

async function load() {
  loading.value = true
  error.value = ''

  try {
    user.value = await getCurrentUser()

    const profile = user.value.profile

    matrixId.value = profile?.matrix_id ?? null
    form.display_name = profile?.display_name ?? null
    form.bio = profile?.bio ?? null
    form.avatar_url = profile?.avatar_url ?? null
    form.github_url = profile?.github_url ?? null
    form.website_url = profile?.website_url ?? null
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not load your profile.'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  saved.value = false
  error.value = ''

  try {
    const profile = await updateMyProfile({
      display_name: normalize(form.display_name),
      bio: normalize(form.bio),
      avatar_url: normalize(form.avatar_url),
      github_url: normalize(form.github_url),
      website_url: normalize(form.website_url),
    })

    if (user.value) {
      user.value.profile = profile
    }
    if (currentUser.value) {
      currentUser.value.profile = profile
    }

    saved.value = true
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
</script>

<template>
  <main class="mx-auto max-w-[1120px] px-5 py-10 pb-24 sm:px-8">
    <div class="max-w-2xl">
      <p class="font-mono text-xs font-medium uppercase tracking-[0.08em] text-[var(--accent-ink)]">
        Account
      </p>

      <h1 class="mt-3 font-display text-[34px] font-semibold tracking-[-0.02em] text-[var(--text)]">
        My profile
      </h1>

      <p class="mt-2 text-[15px] leading-6 text-[var(--muted)]">
        Manage how you appear alongside the bots you publish.
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
        class="mt-8 overflow-hidden rounded-[14px] border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow)]"
        @submit.prevent="save"
      >
        <!-- Identity -->
        <section class="p-6 sm:flex sm:items-center sm:gap-6 sm:p-7">
          <div class="flex min-w-0 items-center gap-4">
            <div
              class="grid size-[64px] shrink-0 place-items-center overflow-hidden rounded-[16px] bg-[var(--accent-soft)] font-display text-xl font-semibold text-[var(--accent-ink)]"
            >
              <img
                v-if="form.avatar_url"
                :src="form.avatar_url"
                alt=""
                class="size-full object-cover"
              >

              <span v-else>
                {{ initials }}
              </span>
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

              <span
                v-if="matrixId"
                class="mt-2 inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium"
                :class="
                  user?.profile?.matrix_id_verified
                    ? 'bg-[var(--accent-soft)] text-[var(--accent-ink)]'
                    : 'bg-[var(--sunk)] text-[var(--muted)]'
                "
              >
                {{
                  user?.profile?.matrix_id_verified
                    ? '✓ Verified'
                    : 'Unverified'
                }}
              </span>
            </div>
          </div>

          <RouterLink
            v-if="user?.id"
            :to="`/profiles/${user.id}`"
            class="mt-5 inline-flex w-full shrink-0 items-center justify-center gap-2 rounded-[9px] border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-[13px] font-medium text-[var(--muted)] no-underline transition hover:border-[var(--border-strong)] hover:bg-[var(--hover)] hover:text-[var(--text)] sm:ml-auto sm:mt-0 sm:w-auto"
          >
            View public profile
            <ArrowTopRightOnSquareIcon class="size-4" />
          </RouterLink>
        </section>

        <!-- Profile -->
        <section class="border-t border-[var(--border)] p-6 sm:p-7">
          <div class="border-b border-[var(--border)] pb-3">
            <h2 class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]">
              Profile
            </h2>
          </div>

          <div class="mt-6 grid gap-5 sm:grid-cols-2">
            <label>
              <span class="text-[13px] font-medium text-[var(--text)]">
                Display name
              </span>

              <input
                v-model="form.display_name"
                type="text"
                maxlength="255"
                placeholder="PenguinBoi"
                class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
              >
            </label>

            <label>
              <span class="text-[13px] font-medium text-[var(--text)]">
                Matrix ID
              </span>

              <input
                :value="matrixId ?? ''"
                type="text"
                maxlength="255"
                placeholder="@username:matrix.org"
                spellcheck="false"
                readonly
                class="mt-2 w-full cursor-default rounded-[10px] border border-[var(--border)] bg-[var(--sunk)] px-3.5 py-2.5 font-mono text-[13px] text-[var(--muted)] outline-none"
              >
              <p class="mt-1.5 text-[11px] text-[var(--faint)]">
                Verified from your Matrix account and cannot be changed here.
              </p>
            </label>
          </div>

          <label class="mt-5 block">
            <div class="flex items-center justify-between gap-4">
              <span class="text-[13px] font-medium text-[var(--text)]">
                About you
              </span>

              <span class="font-mono text-[11px] text-[var(--faint)]">
                {{ form.bio?.length ?? 0 }}/1024
              </span>
            </div>

            <MarkdownEditor
              v-model="aboutYou"
              :maxlength="1024"
              placeholder="Tell people what you build and what you're interested in."
              aria-label="About you"
              class="mt-2"
            />
          </label>
        </section>

        <!-- Links -->
        <section class="border-t border-[var(--border)] p-6 sm:p-7">
          <div class="border-b border-[var(--border)] pb-3">
            <h2 class="font-mono text-xs font-medium uppercase tracking-[0.06em] text-[var(--faint)]">
              Links
            </h2>
          </div>

          <div class="mt-6 space-y-5">
            <label class="block">
              <span class="text-[13px] font-medium text-[var(--text)]">
                Avatar URL
              </span>

              <input
                v-model="form.avatar_url"
                type="url"
                maxlength="500"
                placeholder="https://example.com/avatar.png"
                class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
              >
            </label>

            <div class="grid gap-5 sm:grid-cols-2">
              <label>
                <span class="text-[13px] font-medium text-[var(--text)]">
                  GitHub
                </span>

                <input
                  v-model="form.github_url"
                  type="url"
                  maxlength="500"
                  placeholder="https://github.com/username"
                  class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
                >
              </label>

              <label>
                <span class="text-[13px] font-medium text-[var(--text)]">
                  Website
                </span>

                <input
                  v-model="form.website_url"
                  type="url"
                  maxlength="500"
                  placeholder="https://example.com"
                  class="mt-2 w-full rounded-[10px] border border-[var(--border-strong)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text)] outline-none transition focus:border-[var(--accent)] focus:ring-3 focus:ring-[var(--accent-soft)]"
                >
              </label>
            </div>
          </div>
        </section>

        <!-- Footer -->
        <footer
          class="flex min-h-16 items-center justify-between gap-4 border-t border-[var(--border)] bg-[var(--sunk)] px-6 py-4 sm:px-7"
        >
          <div>
            <p
              v-if="saved"
              class="flex items-center gap-2 text-sm text-[var(--accent-ink)]"
            >
              <CheckCircleIcon class="size-4" />
              Profile saved
            </p>

            <p
              v-else
              class="font-mono text-[11px] text-[var(--faint)]"
            >
              Public profile information
            </p>
          </div>

          <button
            type="submit"
            :disabled="saving"
            class="rounded-[9px] bg-[var(--accent)] px-5 py-2.5 text-sm cursor-pointer font-medium text-[#0e1012] transition hover:bg-[var(--accent-deep)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {{ saving ? 'Saving…' : 'Save changes' }}
          </button>
        </footer>
      </form>
    </template>
  </main>
</template>
