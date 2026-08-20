export interface MailtoOptions {
    to: string
    subject?: string
    body?: string
    cc?: string
    bcc?: string
}

export function createMailto({ to, subject, body, cc, bcc }: MailtoOptions): string {
    const params: string[] = []

    if (subject) {
        params.push(`subject=${encodeURIComponent(subject)}`)
    }

    if (body) {
        params.push(`body=${encodeURIComponent(body)}`)
    }

    if (cc) {
        params.push(`cc=${encodeURIComponent(cc)}`)
    }

    if (bcc) {
        params.push(`bcc=${encodeURIComponent(bcc)}`)
    }

    return `mailto:${to}${params.length ? `?${params.join('&')}` : ''}`
}