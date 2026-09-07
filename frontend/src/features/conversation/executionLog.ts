export type ExecutionStepStatus = 'running' | 'success' | 'degraded' | 'failed' | 'interrupted'

export function executionStepStatus(item: { status?: string } | undefined): ExecutionStepStatus {
  const status = item?.status
  if (status === 'completed') return 'success'
  return (status || 'success') as ExecutionStepStatus
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
