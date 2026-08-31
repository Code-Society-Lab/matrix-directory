/** Build the placeholder shown when a profile has no usable avatar image. */
export function initialsFrom(name: string | null | undefined): string {
  const words = (name ?? '').replace(/^@/, '').trim().split(/\s+/).filter(Boolean)

  const initials = words
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase()

  return initials || '?'
}
