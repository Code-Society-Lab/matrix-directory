<script setup lang="ts">
import { watch } from 'vue'
import {
  defaultValueCtx,
  Editor,
  editorViewOptionsCtx,
  rootCtx,
} from '@milkdown/kit/core'
import { commonmark } from '@milkdown/kit/preset/commonmark'
import { getMarkdown, replaceAll } from '@milkdown/kit/utils'
import { Milkdown, useEditor } from '@milkdown/vue'

import { markdownImagePolicy } from './markdownPolicy'
import '@milkdown/crepe/theme/common/prosemirror.css'
import '@milkdown/crepe/theme/common/reset.css'
import './markdown.css'

const props = withDefaults(
  defineProps<{
    source: string
    ariaLabel?: string
  }>(),
  {
    ariaLabel: 'Markdown content',
  },
)

const { get, loading } = useEditor((root) =>
  Editor.make()
    .config((ctx) => {
      ctx.set(rootCtx, root)
      ctx.set(defaultValueCtx, props.source)
      ctx.update(editorViewOptionsCtx, (options) => ({
        ...options,
        editable: () => false,
        attributes: (state) => {
          const currentAttributes =
            typeof options.attributes === 'function'
              ? options.attributes(state)
              : options.attributes

          return {
            ...currentAttributes,
            'aria-label': props.ariaLabel,
            role: 'document',
          }
        },
      }))
    })
    .use(commonmark)
    .use(markdownImagePolicy),
)

watch(
  [() => props.source, loading],
  ([source, isLoading]) => {
    if (isLoading) return

    const editor = get()
    if (!editor) return

    const currentMarkdown = editor.action(getMarkdown())
    if (currentMarkdown !== source) {
      editor.action(replaceAll(source))
    }
  },
)
</script>

<template>
  <div
    class="markdown-editor markdown-editor--readonly"
    :aria-busy="loading"
  >
    <Milkdown />
  </div>
</template>
