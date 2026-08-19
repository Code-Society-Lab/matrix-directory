<script setup lang="ts">
import { RouterLink } from 'vue-router'

import MatrixLogo from './MatrixLogo.vue'
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="border-t border-[var(--border)] bg-[var(--surface)]">
    <div
      class="mx-auto w-full max-w-[1120px] px-5 py-6 sm:px-8"
    >
      <div
        class="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between"
      >
        <div class="max-w-sm">
          <RouterLink
            to="/"
            class="
              inline-flex items-center gap-2
              font-display text-sm font-semibold tracking-tight
              text-[var(--text)]
              transition-colors
              hover:text-[var(--accent-deep)]
            "
          >
            Matrix Directory
          </RouterLink>

          <p
            class="
              mt-2 text-sm leading-6
              text-[var(--muted)]
            "
          >
            Discover projects across the Matrix ecosystem.
          </p>
        </div>

        <nav
          aria-label="Footer navigation"
          class="
            flex flex-wrap gap-x-6 gap-y-3
            text-sm text-[var(--muted)]
          "
        >
          <RouterLink
            to="/browse"
            class="
              transition-colors
              hover:text-[var(--text)]
            "
          >
            Browse
          </RouterLink>

          <RouterLink
            to="/submit"
            class="
              transition-colors
              hover:text-[var(--text)]
            "
          >
            Submit
          </RouterLink>

          <a
            href="/docs"
            class="
              transition-colors
              hover:text-[var(--text)]
            "
          >
            Docs
          </a>

          <a
            href="https://github.com/Code-Society-Lab/matrix-directory"
            target="_blank"
            rel="noopener noreferrer"
            class="
              transition-colors
              hover:text-[var(--text)]
            "
          >
            GitHub
          </a>
        </nav>
      </div>

      <div
        class="
          mt-7 flex flex-col gap-2
          border-t border-[var(--border)]
          pt-5
          text-xs text-[var(--faint)]
          sm:flex-row sm:items-center sm:justify-between
        "
      >
        <p>
          © {{ currentYear }} Code Society Lab
        </p>

        <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
          <a
            href="https://matrix.org/"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Matrix.org"
            class="text-[var(--faint)] transition-colors hover:text-[var(--text)]"
          >
            <MatrixLogo class="size-5" />
          </a>
          <p>
            Open source · Not affiliated with The Matrix.org Foundation
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>
