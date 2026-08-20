import { createMailto } from '../utils/mailto'

interface ReportProfileEmailOptions {
  displayName: string
  matrixId: string | null
  profileUrl: string
}

export function createReportProfileEmail({
  displayName,
  matrixId,
  profileUrl,
}: ReportProfileEmailOptions): string {
  return createMailto({
    to: 'report@codesociety.xyz',
    subject: `[Matrix Directory] Report profile: ${displayName}`,
    body: [
      `Profile: ${profileUrl}`,
      `Matrix ID: ${matrixId ?? 'N/A'}`,
      '',
      'Reason for report:',
      '',
    ].join('\n'),
  })
}