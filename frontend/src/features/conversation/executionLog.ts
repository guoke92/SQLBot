import type { ChatLogHistoryItem } from '@/api/chat'

type LogItem = ChatLogHistoryItem | Record<string, any>
export type ExecutionStepStatus = 'running' | 'success' | 'degraded' | 'failed' | 'interrupted'

export function executionStepStatus(item: LogItem | undefined): ExecutionStepStatus {
  return (item?.status || 'success') as ExecutionStepStatus
}

export function isSpanPayload(item: LogItem | undefined): boolean {
  return !!item?.graph_node || !!item?.title_key || Object.keys(item?.detail || {}).length > 0
}

export function stepDisplayName(item: LogItem | undefined): string {
  if (!item) return ''
  const base = item.operate || ''
  const brief = item.detail?.brief || ''
  return brief ? `${base} · ${brief}` : base
}

export function executionStepSummary(item: LogItem): string {
  return stepDisplayName(item)
}

const NODE_PHASE: Record<string, string> = {
  prepare: 'prepare',
  prepare_record: 'prepare',
  ensure_datasource: 'prepare',
  resolve_access_scope: 'prepare',
  retrieve_context: 'understand',
  turn_router: 'understand',
  ground_entities: 'understand',
  plan_query: 'plan',
  review_query: 'plan',
  semantic_review: 'plan',
  await_clarification: 'plan',
  agent: 'plan',
  generate_queries: 'plan',
  execute_tools: 'execute',
  execute_queries: 'execute',
  decide_next: 'execute',
  generate_charts: 'present',
  summarize_answer: 'respond',
  stream: 'respond',
  parse: 'review',
}

export function executionNodePhase(node?: string): string {
  return NODE_PHASE[node || ''] || 'plan'
}

export function conversationStageKey(node?: string): string {
  const phase = executionNodePhase(node)
  return {
    prepare: 'qa.run_stage_prepare',
    understand: 'qa.run_stage_understand',
    plan: 'qa.run_stage_generate',
    execute: 'qa.run_stage_execute',
    review: 'qa.run_stage_generate',
    present: 'qa.run_stage_chart',
    respond: 'qa.run_stage_summary',
  }[phase] as string
}
