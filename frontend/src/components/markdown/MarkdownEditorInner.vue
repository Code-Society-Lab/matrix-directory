<script setup lang="ts">
import { computed, watch } from 'vue'
import { CrepeBuilder } from '@milkdown/crepe/builder'
import { blockEdit } from '@milkdown/crepe/feature/block-edit'
import { cursor } from '@milkdown/crepe/feature/cursor'
import { linkTooltip } from '@milkdown/crepe/feature/link-tooltip'
import { listItem } from '@milkdown/crepe/feature/list-item'
import { placeholder as placeholderFeature } from '@milkdown/crepe/feature/placeholder'
import { toolbar } from '@milkdown/crepe/feature/toolbar'
import { editorViewOptionsCtx } from '@milkdown/kit/core'
import { getMarkdown, replaceAll } from '@milkdown/kit/utils'
import { Milkdown, useEditor } from '@milkdown/vue'

import { markdownImagePolicy } from './markdownPolicy'
import '@milkdown/crepe/theme/common/prosemirror.css'
import '@milkdown/crepe/theme/common/reset.css'
import '@milkdown/crepe/theme/common/block-edit.css'
import '@milkdown/crepe/theme/common/cursor.css'
import '@milkdown/crepe/theme/common/link-tooltip.css'
import '@milkdown/crepe/theme/common/list-item.css'
import '@milkdown/crepe/theme/common/placeholder.css'
import '@milkdown/crepe/theme/common/toolbar.css'
import '@milkdown/crepe/theme/frame.css'

import './markdown.css'

const props = withDefaults(
  defineProps<{
    modelValue: string
    maxlength?: number
    placeholder?: string
    ariaLabel?: string
  }>(),
  {
    maxlength: undefined,
    placeholder: 'Write a description…',
    ariaLabel: 'Markdown editor',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const limitExceeded = computed(() =>
  Boolean(props.maxlength && props.modelValue.length > props.maxlength),
)

const { get, loading } = useEditor((root) => {
  const crepe = new CrepeBuilder({
    root,
    defaultValue: props.modelValue,
  })

  crepe
    .addFeature(blockEdit)
    .addFeature(cursor)
    .addFeature(linkTooltip)
    .addFeature(listItem)
    .addFeature(placeholderFeature, {
      text: props.placeholder,
      mode: 'doc',
    })
    .addFeature(toolbar)

  crepe.editor.config((ctx) => {
    ctx.update(editorViewOptionsCtx, (options) => ({
      ...options,
      attributes: (state) => {
        const currentAttributes =
          typeof options.attributes === 'function'
            ? options.attributes(state)
            : options.attributes

        return {
          ...currentAttributes,
          'aria-label': props.ariaLabel,
          'aria-invalid': limitExceeded.value ? 'true' : 'false',
          'aria-multiline': 'true',
          role: 'textbox',
        }
      },
    }))
  })
  crepe.editor.use(markdownImagePolicy)
  crepe.on((listener) => {
    listener.markdownUpdated((_ctx, markdown) => {
      if (markdown !== props.modelValue) {
        emit('update:modelValue', markdown)
      }
    })
  })

  return crepe
})

watch(
  [() => props.modelValue, loading],
  ([value, isLoading]) => {
    if (isLoading) return

    const editor = get()
    if (!editor) return

    const currentMarkdown = editor.action(getMarkdown())
    if (currentMarkdown !== value) {
      editor.action(replaceAll(value))
    }
  },
)
</script>

<template>
  <div
    class="markdown-editor"
    :class="{
      'markdown-editor--invalid': limitExceeded,
    }"
    :aria-busy="loading"
  >
    <Milkdown />

    <p
      v-if="limitExceeded"
      class="markdown-editor__limit"
      role="alert"
    >
      The description cannot exceed {{ maxlength }} characters.
    </p>
  </div>
</template>
