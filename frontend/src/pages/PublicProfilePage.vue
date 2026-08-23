<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  ArrowLeftIcon,
  CheckIcon,
  CodeBracketIcon,
  ExclamationTriangleIcon,
  GlobeAltIcon,
  FlagIcon,
  PencilSquareIcon,
} from '@heroicons/vue/24/outline'

import { currentUser } from '../auth'
import {
  getPublicProfile,
  type PublicProfile,
} from '../api/client'
import MarkdownContent from '../components/markdown/MarkdownContent.vue'
import { projectPath } from '../utils/projectRoutes'
import { createReportProfileEmail } from '../email/reportProfile'

const route = useRoute()

const profile = ref<PublicProfile | null>(null)
const loading = ref(true)
const error = ref('')

const displayName = computed(
  () =>
    profile.value?.display_name ||
    profile.value?.matrix_id ||
    'Directory member',
)

const initials = computed(() =>
  displayName.value
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase(),
)

const bio = computed(() => profile.value?.bio ?? '')

const isOwnProfile = computed(
  () => currentUser.value?.id === profile.value?.user_id,
)

async function loadProfile() {
  loading.value = true
  error.value = ''

  try {
    profile.value = await getPublicProfile(
      String(route.params.id),
    )
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Could not load this profile.'
  } finally {
    loading.value = false
  }
}

const reportMailto = computed(() => {
  if (!profile.value) {
    return '#'
  }

  return createReportProfileEmail({
    displayName: displayName.value,
    matrixId: profile.value.matrix_id,
    profileUrl: window.location.href,
  })
})

watch(() => route.params.id, loadProfile)
onMounted(loadProfile)
</script>

<template>
  <main
    class="mx-auto w-full max-w-[1120px] px-5 py-8 pb-20 sm:px-8 sm:py-10 sm:pb-24"
  >
    <p
      v-if="loading"
      class="py-20 font-mono text-xs text-[var(--faint)]"
    >
      Loading profile…
    </p>

    <div
      v-else-if="error"
      class="flex items-center gap-2 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]"
    >
      <ExclamationTriangleIcon class="size-4 shrink-0" />
      {{ error }}
    </div>

    <template v-else-if="profile">
      <div class="flex items-center justify-between gap-4">
        <RouterLink
          to="/browse"
          class="inline-flex items-center gap-2 font-mono text-[12px] text-[var(--muted)] no-underline transition hover:text-[var(--text)]"
        >
          <ArrowLeftIcon class="size-3.5" />
          Directory
        </RouterLink>

        <RouterLink
          v-if="isOwnProfile"
          to="/account/profile"
          class="inline-flex items-center gap-1.5 rounded-[9px] border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-[12px] font-medium text-[var(--muted)] no-underline transition hover:border-[var(--border-strong)] hover:bg-[var(--hover)] hover:text-[var(--text)]"
        >
          <PencilSquareIcon class="size-4" />
          Edit profile
        </RouterLink>
      </div>

      <div class="mt-7 grid gap-12 lg:grid-cols-[minmax(0,1fr)_360px] lg:gap-16">
        <!-- Profile -->
        <section class="min-w-0">
          <div class="flex items-center gap-4 sm:gap-5">
            <div
              class="grid size-16 shrink-0 place-items-center overflow-hidden rounded-[16px]
             bg-[var(--accent-soft)] font-display text-xl font-semibold
             text-[var(--accent-ink)] sm:size-24 sm:rounded-[20px]"
            >
              <img
                v-if="profile.avatar_url"
                :src="profile.avatar_url"
                alt=""
                class="size-full object-cover"
              >

              <span v-else>
                {{ initials }}
              </span>
            </div>

            <div class="flex min-w-0 flex-1 items-start gap-3">
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2.5">
                  <h1
                    class="font-display text-[30px] font-semibold tracking-[-0.025em] text-[var(--text)] sm:text-[38px]"
                  >
                    {{ displayName }}
                  </h1>

                  <span
                    v-if="profile.matrix_id_verified"
                    class="inline-flex items-center gap-1 rounded-full bg-[var(--accent-soft)] px-2.5 py-1 text-xs font-medium text-[var(--accent-ink)]"
                  >
                    <CheckIcon class="size-3.5" />
                    Verified
                  </span>
                </div>

                <div
                  v-if="profile.matrix_id"
                  class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1"
                >
                  <p
                    v-if="profile.matrix_id"
                    class="break-all font-mono text-sm text-[var(--muted)]"
                  >
                    {{ profile.matrix_id }}

                    <a
                      :href="reportMailto"
                      aria-label="Report profile"
                      title="Report profile"
                      class="inline-flex align-super text-[var(--danger)] no-underline transition hover:opacity-70"
                    >
                      <FlagIcon class="size-3" />
                    </a>
                  </p>
                </div>

                <div
                  v-if="profile.github_url || profile.website_url"
                  class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2"
                >
                  <a
                    v-if="profile.github_url"
                    :href="profile.github_url"
                    target="_blank"
                    rel="noreferrer"
                    title="Github Account"
                    class="inline-flex items-center gap-1.5 text-[13px] font-medium text-[var(--muted)] no-underline transition hover:text-[var(--text)]"
                  >
                    <CodeBracketIcon class="size-4" />
                    GitHub
                  </a>

                  <a
                    v-if="profile.website_url"
                    :href="profile.website_url"
                    target="_blank"
                    rel="noreferrer"
                    title="Website"
                    class="inline-flex items-center gap-1.5 text-[13px] font-medium text-[var(--muted)] no-underline transition hover:text-[var(--text)]"
                  >
                    <GlobeAltIcon class="size-4" />
                    Website
                  </a>
                </div>
              </div>
            </div>
          </div>

          <MarkdownContent
            v-if="bio"
            :source="bio"
            aria-label="Profile biography"
            class="mt-6 min-w-0 max-w-full break-words"
          />
        </section>

        <!-- Projects -->
        <aside class="min-w-0 lg:sticky lg:top-24">
          <div class="flex items-baseline justify-between gap-4 border-b border-[var(--border)] pb-3">
            <h2 class="font-display text-lg font-semibold text-[var(--text)]">
              Published projects
            </h2>

            <span class="shrink-0 font-mono text-xs text-[var(--faint)]">
              {{ profile.projects.length }}
            </span>
          </div>

          <div
            v-if="profile.projects.length"
            class="mt-2"
          >
            <RouterLink
              v-for="project in profile.projects"
              :key="project.id"
              :to="projectPath(project)"
              class="group flex min-w-0 items-start gap-3 rounded-[10px] px-2 py-3.5 no-underline transition hover:bg-[var(--hover)]"
            >
              <div
                class="grid size-10 shrink-0 place-items-center rounded-[10px] bg-[var(--accent-soft)] font-display text-sm font-semibold text-[var(--accent-ink)]"
              >
                {{ project.name.charAt(0).toUpperCase() }}
              </div>

              <div class="min-w-0 flex-1">
                <h3 class="truncate font-display text-[14px] font-semibold text-[var(--text)]">
                  {{ project.name }}
                </h3>

                <p
                  v-if="project.short_description"
                  class="mt-1 line-clamp-2 text-[13px] leading-5 text-[var(--muted)]"
                >
                  {{ project.short_description }}
                </p>
              </div>
            </RouterLink>
          </div>

          <p
            v-else
            class="mt-5 text-sm text-[var(--muted)]"
          >
            No projects published yet.
          </p>
        </aside>
      </div>
    </template>
  </main>
</template>
