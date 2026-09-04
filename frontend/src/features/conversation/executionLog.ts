import type { ChatLogHistoryItem } from '@/api/chat'

type LogItem = ChatLogHistoryItem | Record<string, any>
export type ExecutionStepStatus = 'running' | 'success' | 'degraded' | 'failed' | 'interrupted'

export function executionStepStatus(item: LogItem | undefined): ExecutionStepStatus {
  return (item?.status || 'success') as ExecutionStepStatus
}

export function isSpanPayload(item: LogItem | undefined): boolean {
  return !!item?.graph_node || !!item?.title_key || Object.keys(item?.detail || {}).length > 0
}

export const TOOL_DISPLAY_NAMES: Record<string, string> = {
  execute_sql_sandbox: '执行查询 (execute_sql_sandbox)',
  patch_and_compile_sql: '增量补丁 (patch_and_compile_sql)',
  compare_results: '数据对比 (compare_results)',
  search_schema: '结构检索 (search_schema)',
  search_wiki: '查阅知识 (search_wiki)',
  request_clarification: '请求澄清 (request_clarification)',
}

export function getToolDisplayName(toolName: string): string {
  return TOOL_DISPLAY_NAMES[toolName] || `工具调用 (${toolName})`
}

export function stepDisplayName(item: LogItem | undefined): string {
  if (!item) return ''
  const base = item.operate || ''
  
  // If this is a tool call, prioritize specific tool name and description
  const toolName = item.title_params?.tool || item.detail?.input?.tool || item.detail?.name || (item as any)?.input?.tool
  if (toolName) {
    return getToolDisplayName(toolName)
  }

  const brief = item.detail?.brief || (item as any)?.brief || ''
  if (brief) {
    if (TOOL_DISPLAY_NAMES[brief]) {
      return TOOL_DISPLAY_NAMES[brief]
    }
    return `${base} · ${brief}`
  }
  return base
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
  agent_loop: 'plan',
  generate_queries: 'plan',
  execute_tools: 'execute',
  execute_queries: 'execute',
  decide_next: 'execute',
  generate_charts: 'present',
  finalize_turn: 'present',
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
