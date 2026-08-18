import { $remark } from '@milkdown/kit/utils'
import type { Nodes, Parent, Root, Text } from 'mdast'

function removeImages(node: Root | Nodes): void {
  if (!('children' in node)) return

  const parent = node as Parent
  parent.children = parent.children.flatMap((child) => {
    if (child.type === 'image') {
      return child.alt
        ? [{ type: 'text', value: child.alt } satisfies Text]
        : []
    }

    removeImages(child)
    return [child]
  })
}

/** Prevent persisted Markdown from initiating third-party image requests. */
export const markdownImagePolicy = $remark(
  'markdownImagePolicy',
  () => () => (tree) => {
    removeImages(tree)
  },
)
