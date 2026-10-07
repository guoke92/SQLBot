import { request } from '@/utils/request'

/** Per-tool override; `null` fields mean "inherit the code default". */
export interface AgentToolOverride {
  enabled: boolean
  description: string | null
  parallel_safe: boolean | null
  round_budget: number | null
}

export interface SqlRuleOverride {
  enabled: boolean
}

export interface AgentConfigSnapshot {
  prompt_body: string
  tools: Record<string, AgentToolOverride>
  loop_params: Record<string, number>
  sql_rules: Record<string, SqlRuleOverride>
  change_note: string | null
}

export interface AgentConfigVersion {
  id: number
  version_no: number
  status: string
  change_note: string | null
  create_by: number | null
  create_time: string
  published_by: number | null
  published_time: string | null
}

export interface AgentConfigDetail {
  /** "draft" | "published" | "code" */
  source: string
  active_version_no: number | null
  draft_version_no: number | null
  snapshot: AgentConfigSnapshot
  versions: AgentConfigVersion[]
}

export interface LoopParamMeta {
  key: string
  default: number
  minimum: number
  maximum: number
  /** Already-namespaced i18n key, e.g. `agent_config.params.execution_round_limit`. */
  label_key: string
}

export interface SqlRuleMeta {
  key: string
  default_enabled: boolean
  label_key: string
}

export interface AgentConfigMeta {
  prompt: {
    min_chars: number
    max_chars: number
    placeholder: string
    required_markers: string[]
  }
  tool_description_max_chars: number
  tool_round_budget: { min: number; max: number }
  change_note_max_chars: number
  params: LoopParamMeta[]
  tool_names: string[]
  required_tool_names: string[]
  sql_rules: SqlRuleMeta[]
}

export const agentConfigApi = {
  get: () => request.get('/system/agent_config'),
  getMeta: () => request.get('/system/agent_config/meta'),
  saveDraft: (data: AgentConfigSnapshot) => request.put('/system/agent_config', data),
  publish: () => request.post('/system/agent_config/publish'),
  rollback: (versionId: number) => request.post(`/system/agent_config/rollback/${versionId}`),
}
