<script setup lang="ts">
import { useRoute } from 'vue-router'
import {
  ArrowRightIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
} from '@heroicons/vue/24/outline'

import MatrixLogo from '../components/MatrixLogo.vue'
const route = useRoute()

const loginUrl =
  `${import.meta.env.VITE_API_URL ?? '/api'}/auth/matrix/login`
</script>

<template>
  <main
    class="mx-auto flex max-w-[1120px] items-start justify-center px-5 pb-24 pt-16 sm:px-8 sm:pt-24"
  >
    <div class="w-full max-w-[480px]">
      <!-- Heading -->
      <div>
        <p
          class="font-mono text-xs font-medium uppercase tracking-[0.08em] text-[var(--accent-ink)]"
        >
          Account
        </p>

        <h1
          class="mt-3 font-display text-[34px] font-semibold tracking-[-0.025em] text-[var(--text)]"
        >
          Sign in with Matrix
        </h1>

        <p
          class="mt-3 text-[15px] leading-6 text-[var(--muted)]"
        >
          Sign in securely using your Matrix account to manage your
          profile and directory listings.
        </p>
      </div>

      <!-- Error -->
      <div
        v-if="route.query.error"
        class="mt-7 flex items-start gap-2.5 rounded-[10px] border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]"
      >
        <ExclamationTriangleIcon
          class="mt-0.5 size-4 shrink-0"
        />

        <span>
          {{ route.query.error }}
        </span>
      </div>

      <!-- Login card -->
      <section
        class="mt-8 overflow-hidden rounded-[14px] border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow)]"
      >
        <div class="p-6 sm:p-7">
          <div class="flex items-start gap-4">
            <!-- Matrix Logo -->
            <MatrixLogo class="size-12 sm:size-16" />

            <div>
              <h2
                class="font-display text-base font-semibold text-[var(--text)]"
              >
                Continue with Matrix
              </h2>

              <p
                class="mt-1 text-[13.5px] leading-5 text-[var(--muted)]"
              >
                You’ll be redirected to the Matrix authentication
                service to complete sign-in.
              </p>
            </div>
          </div>

          <a
            :href="loginUrl"
            class="mt-6 flex w-full items-center justify-between rounded-[10px] bg-[var(--accent)] px-4 py-3 text-sm font-medium text-[#0e1012] no-underline transition hover:bg-[var(--accent-deep)]"
          >
            <span>Continue with Matrix</span>
            <ArrowRightIcon class="size-4" />
          </a>
        </div>

        <!-- Security note -->
        <div
          class="flex items-start gap-3 border-t border-[var(--border)] bg-[var(--sunk)] px-6 py-4 sm:px-7"
        >
          <ShieldCheckIcon
            class="mt-0.5 size-4 shrink-0 text-[var(--accent-ink)]"
          />

          <p
            class="text-[12.5px] leading-5 text-[var(--muted)]"
          >
            The directory never receives your Matrix password.
            Authentication is handled through OpenID Connect.
          </p>
        </div>
      </section>

      <!-- Small explanation -->
      <p
        class="mt-5 text-center font-mono text-[11px] leading-5 text-[var(--faint)]"
      >
        Your directory profile is separate from your Matrix account.
      </p>
    </div>
  </main>
</template>
