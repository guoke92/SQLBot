export type ExecutionStepStatus = 'running' | 'success' | 'degraded' | 'failed' | 'interrupted'

export function executionStepStatus(item: { status?: string } | undefined): ExecutionStepStatus {
  const status = item?.status
  if (status === 'completed') return 'success'
  return (status || 'success') as ExecutionStepStatus
}

/** Wait this long in queued status before showing the real dispatcher copy. */
export const QUEUED_WAIT_MS = 2000

export type ConversationPlaceholderRecord = {
  run_status?: string
  run_dispatch_attempts?: number
  create_time?: Date | string
  run_update_time?: Date | string
  run_started_at?: Date | string
}

function queuedElapsedMs(record?: ConversationPlaceholderRecord): number {
  const stamp = record?.run_update_time || record?.create_time
  if (!stamp) return 0
  const ms = Date.now() - new Date(stamp).getTime()
  return Number.isFinite(ms) ? ms : 0
}

function isRealQueue(record?: ConversationPlaceholderRecord): boolean {
  if ((record?.run_dispatch_attempts || 0) > 1) return true
  return queuedElapsedMs(record) >= QUEUED_WAIT_MS
}

export function conversationPlaceholderKey(record?: ConversationPlaceholderRecord): string {
  if (record?.run_status === 'queued' && isRealQueue(record)) {
    return (record.run_dispatch_attempts || 0) > 1
      ? 'qa.run_stage_redispatch'
      : 'qa.run_stage_queued'
  }
  return 'chat.timeline.processing'
}

/** @deprecated Prefer conversationPlaceholderKey; NLQ stage names are no longer shown. */
export function conversationStageKey(_node?: string): string {
  return 'chat.timeline.processing'
}
