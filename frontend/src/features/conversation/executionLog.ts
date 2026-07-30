import type { ChatLogHistoryItem } from '@/api/chat'

type LogItem = ChatLogHistoryItem | Record<string, any>
export type ExecutionStepStatus = 'running' | 'success' | 'failed'

export function executionStepStatus(item: LogItem | undefined): ExecutionStepStatus {
  if (!item?.finish_time) return 'running'
  return item.error ? 'failed' : 'success'
}

export function parseLogMessage(item: LogItem | undefined): any {
  if (!item) return null
  const raw = item.message
  if (raw && typeof raw === 'object') return raw
  if (typeof raw !== 'string') return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function spanMetaFromMessage(message: any): Record<string, any> | null {
  if (!message) return null
  if (message.sqlbot_span) return message
  if (!Array.isArray(message)) return null

  const head = message.find((item: any) => item?.sqlbot_span_meta || item?.sqlbot_span)
  if (head?.sqlbot_span) return head
  if (!head?.content) return null

  try {
    const parsed = typeof head.content === 'string' ? JSON.parse(head.content) : head.content
    return parsed?.sqlbot_span ? parsed : null
  } catch {
    return null
  }
}

export function isSpanPayload(item: LogItem | undefined): boolean {
  return !!spanMetaFromMessage(parseLogMessage(item))
}

export function stepDisplayName(item: LogItem | undefined): string {
  if (!item) return ''

  const base = item.operate || ''
  const message = parseLogMessage(item)
  if (item.operate_key === 'TOOL_CALL') {
    const tool = message?.name || message?.tool || message?.payload?.name
    if (tool) return `${base} · ${tool}`
  }

  const span = spanMetaFromMessage(message)
  if (!span) return base

  const parts: string[] = []
  if (span.brief) parts.push(String(span.brief))
  if (span.step_index !== undefined && span.step_index !== null) {
    parts.push(`b${span.step_index}`)
  }
  if (
    span.gen_attempts !== undefined &&
    span.gen_attempts !== null &&
    Number(span.gen_attempts) > 0
  ) {
    parts.push(`a${span.gen_attempts}`)
  }
  if (span.unit_index !== undefined && span.unit_index !== null) {
    parts.push(`#${span.unit_index}`)
  }
  return parts.length ? `${base} · ${parts.join(' · ')}` : base
}

export function executionStepSummary(item: LogItem): string {
  const message = parseLogMessage(item)
  const payload = message?.sqlbot_span ? message.payload : message?.payload || message
  const status = {
    running: '…',
    success: '✓',
    failed: '✕',
  }[executionStepStatus(item)]
  const title = stepDisplayName(item)

  if (item.operate_key === 'AGENT_STEP') {
    const tools = Array.isArray(payload?.tool_calls)
      ? payload.tool_calls.map((call: any) => call?.name).filter(Boolean)
      : []
    return tools.length ? `${status} ${title} → \`${tools.join('`, `')}\`` : `${status} ${title}`
  }

  if (item.operate_key === 'TOOL_CALL') {
    const summary = payload?.result?.summary
    return summary ? `${status} ${title}：${summary}` : `${status} ${title}`
  }

  return `${status} ${title}`
}
