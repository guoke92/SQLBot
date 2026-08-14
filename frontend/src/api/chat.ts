import { request } from '@/utils/request'
import { getDate } from '@/utils/utils.ts'
import { i18n } from '@/i18n'

const { t } = i18n.global

export const runApi = {
  create: (data: CreateRunRequest) => request.post('/chat/runs', data),
  snapshot: (runId: string) =>
    request.get(`/chat/runs/${runId}`, { requestOptions: { silent: true } }),
  events: (runId: string, cursor = 0, controller?: AbortController) =>
    request.fetchStream(
      `/chat/runs/${runId}/events?cursor=${cursor}`,
      undefined,
      controller,
      'GET'
    ),
  resume: (runId: string, interruptId: string, data: ResumeRunRequest) =>
    request.post(`/chat/runs/${runId}/interrupts/${interruptId}/resume`, data),
  correct: (runId: string, interruptId: string, data: CorrectionRunRequest) =>
    request.post(`/chat/runs/${runId}/interrupts/${interruptId}/correct`, data),
  cancel: (runId: string) => request.post(`/chat/runs/${runId}/cancel`),
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  create_time?: Date | string
  content?: string | number
  record?: ChatRecord
  isTyping?: boolean
  first_chat?: boolean
  recommended_question?: string
  index: number
}

export interface CandidateResolution {
  option_id: string
  label: string
  description?: string
  impact?: string
  resolution?: Record<string, unknown>
  evidence_refs?: string[]
}

export interface Ambiguity {
  ambiguity_id: string
  business_axis?: string
  business_question: string
  reason?: string
  impact_level: 'low' | 'medium' | 'high'
  candidate_resolutions: CandidateResolution[]
  recommended_candidate_id?: string
  recommendation_reason?: string
  can_assume: boolean
}

export interface AmbiguitySet {
  ambiguities: Ambiguity[]
  summary?: string
  can_proceed_with_assumptions?: boolean
}

export interface ResumeAnswer {
  ambiguity_id: string
  mode: 'option' | 'custom'
  option_id?: string
  text?: string
  evidence_id?: string
}

export interface ConversationInterrupt {
  interrupt_id: string
  version: number
  status: 'open' | 'consumed' | 'cancelled'
  payload: AmbiguitySet
  answers?: ResumeAnswer[]
}

export type ConversationRunStatus =
  'queued' | 'running' | 'awaiting_input' | 'succeeded' | 'degraded' | 'failed' | 'cancelled'

export interface ConversationRunSnapshot {
  run_id: string
  chat_record_id: number
  graph_key: 'chat' | 'config'
  status: ConversationRunStatus
  current_node?: string
  event_cursor: number
  dispatch_attempts: number
  update_time?: string
  started_at?: string
  completed_at?: string
  active_interrupt?: ConversationInterrupt
  interrupts: ConversationInterrupt[]
  record?: Record<string, unknown>
  error_summary?: string
}

export interface CreateRunRequest {
  chat_id: number
  question: string
  datasource_id?: number
  regenerate_record_id?: number
  route_hint?: 'query' | 'analysis' | 'prediction' | 'unsupported'
  reference_record_ids?: number[]
  finish_step?: number
  return_img?: boolean
}

export interface ResumeRunRequest {
  version: number
  idempotency_key: string
  answers: ResumeAnswer[]
  proceed_with_assumptions?: boolean
}

export interface CorrectionRunRequest {
  version: number
  idempotency_key: string
  supersedes_evidence_id: string
  answer: ResumeAnswer
}

export type ResultQualityGrade = 'excellent' | 'acceptable' | 'reference_only' | 'unreliable'

export interface ResultQualityDetail {
  code: string
  params: Record<string, string | number>
  step_index?: number
}

export interface ResultQualityDimension {
  code: string
  weight: number
  score: number
  weighted_score: number
  assessor: 'program' | 'ai'
  details: ResultQualityDetail[]
}

export interface ResultDataObservation {
  code: string
  severity: 'info' | 'warning' | 'error'
  params: Record<string, string | number>
  step_index?: number
}

export interface ResultQuality {
  score: number
  grade: ResultQualityGrade
  dimensions: ResultQualityDimension[]
  observations: ResultDataObservation[]
  passed_checks: string[]
  coverage: {
    returned_rows: number
    truncated: boolean
    step_count: number
  }
}

export type RunStatus =
  'running' | 'awaiting_input' | 'blocked' | 'success' | 'degraded' | 'failed' | 'limit_reached'

export interface RunOutcome {
  status: RunStatus
  failures: Array<Record<string, any>>
  successful_steps: number
  total_steps: number
  quality?: ResultQuality
}

export interface AnswerDataset {
  fields?: string[]
  data?: any[]
  fields_info?: any
  limit?: number
  row_count?: number
  truncated?: boolean
  truncation_reason?: string
  datasource?: number
}

export interface AnswerPresentation {
  title: string
  columns: Array<{
    field: string
    label: string
    display: string
  }>
}

export interface AnswerStep {
  sql: string
  brief: string
  presentation?: AnswerPresentation
  chart?: unknown
  data?: AnswerDataset
  error?: string
  failure?: Record<string, any>
}

export interface AnswerPayload {
  steps: AnswerStep[]
  analysis: string
  outcome: RunOutcome
}

export interface TurnAnswerDataset {
  dataset_id: string
  status: 'succeeded' | 'degraded' | 'failed'
  required?: boolean
  title?: string
  sql?: string
  fields?: string[]
  rows?: Array<Record<string, any>>
  row_count?: number
  truncated?: boolean
  presentation?: AnswerPresentation
  chart?: unknown
  error?: { code: string; message: string; retryable?: boolean }
}

export interface TurnAnswerV1 {
  version: 1
  answer_revision: number
  source_run_id: string
  kind: 'query' | 'analysis' | 'prediction' | 'unsupported'
  status: 'succeeded' | 'degraded' | 'failed'
  content?: string
  datasets?: TurnAnswerDataset[]
  source_datasets?: TurnAnswerDataset[]
  forecast_rows?: Array<Record<string, any>>
  assumptions?: Array<Record<string, any>>
  source_record_ids?: number[]
  quality?: ResultQuality
  error?: { code: string; message: string; retryable?: boolean }
}

export const parseTurnAnswer = (value: unknown): TurnAnswerV1 | undefined => {
  if (!value || typeof value !== 'object') return undefined
  const candidate = value as Partial<TurnAnswerV1>
  if (candidate.version !== 1 || !candidate.kind || !candidate.status) return undefined
  return candidate as TurnAnswerV1
}

export const turnAnswerToPayload = (value: unknown): AnswerPayload | undefined => {
  const answer = parseTurnAnswer(value)
  if (!answer) return undefined
  const datasets = answer.datasets || answer.source_datasets || []
  const failedDatasets = datasets.filter((item) => item.status === 'failed')
  const steps: AnswerStep[] = datasets
    .filter((item) => item.status !== 'failed')
    .map((item) => ({
      sql: item.sql || '',
      brief: item.title || '',
      presentation: item.presentation,
      chart: item.chart,
      data: {
        fields: item.fields || [],
        data: item.rows || [],
        row_count: item.row_count,
        truncated: item.truncated,
      },
    }))
  if (answer.kind === 'prediction' && answer.forecast_rows?.length) {
    const fields = Object.keys(answer.forecast_rows[0] || {})
    steps.push({
      sql: '',
      brief: t('chat.data_predict'),
      chart: {
        type: 'table',
        columns: fields.map((field) => ({ field, label: field, display: field })),
      },
      data: { fields, data: answer.forecast_rows },
    })
  }
  const status: RunStatus = answer.status === 'succeeded' ? 'success' : answer.status
  return {
    steps,
    analysis: answer.content || '',
    outcome: {
      status,
      failures: [
        ...failedDatasets.map((item) => ({
          dataset_id: item.dataset_id,
          required: item.required !== false,
          message: item.error?.message || t('common.failed'),
        })),
        ...(answer.error ? [{ message: answer.error.message }] : []),
      ],
      successful_steps: steps.length,
      total_steps: datasets.length || steps.length,
      quality: answer.quality,
    },
  }
}

export const parseAnswerPayload = (value: unknown): AnswerPayload | undefined => {
  let parsed = value
  if (typeof parsed === 'string') {
    try {
      parsed = JSON.parse(parsed)
    } catch {
      return undefined
    }
  }
  if (!parsed || typeof parsed !== 'object') return undefined
  const candidate = parsed as Partial<AnswerPayload>
  if (!Array.isArray(candidate.steps) || !candidate.outcome) return undefined
  return candidate as AnswerPayload
}

export const selectAnswerStep = (value: unknown, stepIndex = 0): AnswerStep | undefined => {
  const payload = parseAnswerPayload(value)
  if (!payload?.steps.length) return undefined
  return payload.steps[stepIndex] ?? payload.steps[0]
}

export class ChatRecord {
  id?: number
  chat_id?: number
  create_time?: Date | string
  finish_time?: Date | string
  question?: string
  sql_answer?: string
  sql?: string
  datasource?: number
  engine_type?: string
  re_exec?: string | any
  answer?: AnswerPayload
  turn_answer?: TurnAnswerV1
  answer_revision: number = 0
  turn_kind?: 'query' | 'analysis' | 'prediction' | 'unsupported'
  relation?: 'independent' | 'continue' | 'revise'
  reference_record_ids: number[] = []
  data?: AnswerDataset
  chart_answer?: string
  chart?: string
  analysis?: string
  analysis_thinking?: string
  predict?: string
  predict_content?: string
  predict_data?: string | any
  finish?: boolean = false
  error?: string
  run_time: number = 0
  first_chat: boolean = false
  recommended_question?: string
  duration?: number
  total_tokens?: number
  run_id?: string
  run_attempt_index: number = 0
  run_status?: ConversationRunStatus
  run_event_cursor: number = 0
  run_current_node?: string
  run_dispatch_attempts: number = 0
  run_update_time?: Date | string
  run_started_at?: Date | string
  run_completed_at?: Date | string
  active_interrupt?: ConversationInterrupt
  interrupts: ConversationInterrupt[] = []
  intent_reasoning_content?: string
  feedback?: string | null

  constructor()
  constructor(
    id: number,
    chat_id: number,
    create_time: Date | string,
    finish_time: Date | string | undefined,
    question: string,
    sql_answer: string | undefined,
    sql: string | undefined,
    datasource: number | undefined,
    data: unknown,
    chart_answer: string | undefined,
    chart: string | undefined,
    analysis: string | undefined,
    analysis_thinking: string | undefined,
    predict: string | undefined,
    predict_content: string | undefined,
    predict_data: string | any | undefined,
    finish: boolean,
    error: string | undefined,
    run_time: number,
    first_chat: boolean,
    recommended_question: string | undefined,
    duration: number | undefined,
    total_tokens: number | undefined
  )
  constructor(
    id?: number,
    chat_id?: number,
    create_time?: Date | string,
    finish_time?: Date | string,
    question?: string,
    sql_answer?: string,
    sql?: string,
    datasource?: number | undefined,
    data?: unknown,
    chart_answer?: string,
    chart?: string,
    analysis?: string,
    analysis_thinking?: string,
    predict?: string,
    predict_content?: string,
    predict_data?: string | any,
    finish?: boolean,
    error?: string,
    run_time?: number,
    first_chat?: boolean,
    recommended_question?: string,
    duration?: number,
    total_tokens?: number
  ) {
    this.id = id
    this.chat_id = chat_id
    this.create_time = getDate(create_time)
    this.finish_time = getDate(finish_time)
    this.question = question
    this.sql_answer = sql_answer
    this.sql = sql
    this.datasource = datasource
    this.answer = parseAnswerPayload(data)
    this.chart_answer = chart_answer
    this.chart = chart
    this.analysis = analysis
    this.analysis_thinking = analysis_thinking
    this.predict = predict
    this.predict_content = predict_content
    this.predict_data = predict_data
    this.finish = !!finish
    this.error = error
    this.run_time = run_time ?? 0
    this.first_chat = !!first_chat
    this.recommended_question = recommended_question
    this.duration = duration
    this.total_tokens = total_tokens
  }
}

export class Chat {
  id?: number
  create_time?: Date | string
  create_by?: number
  brief?: string
  chat_type?: string
  datasource?: number
  engine_type?: string
  ds_type?: string
  recommended_question?: string | undefined
  recommended_generate?: boolean | undefined

  constructor()
  constructor(
    id: number,
    create_time: Date | string,
    create_by: number,
    brief: string,
    chat_type: string,
    datasource: number,
    engine_type: string
  )
  constructor(
    id?: number,
    create_time?: Date | string,
    create_by?: number,
    brief?: string,
    chat_type?: string,
    datasource?: number,
    engine_type?: string
  ) {
    this.id = id
    this.create_time = getDate(create_time)
    this.create_by = create_by
    this.brief = brief
    this.chat_type = chat_type
    this.datasource = datasource
    this.engine_type = engine_type
  }
}

export class ChatInfo extends Chat {
  datasource_name?: string
  datasource_exists: boolean = true
  records: Array<ChatRecord> = []

  constructor()
  constructor(chat: Chat)
  constructor(
    id: number,
    create_time: Date | string,
    create_by: number,
    brief: string,
    chat_type: string,
    datasource: number,
    engine_type: string,
    ds_type: string,
    datasource_name: string,
    datasource_exists: boolean,
    records: Array<ChatRecord>,
    recommended_question?: string | undefined,
    recommended_generate?: boolean | undefined
  )
  constructor(
    param1?: number | Chat,
    create_time?: Date | string,
    create_by?: number,
    brief?: string,
    chat_type?: string,
    datasource?: number,
    engine_type?: string,
    ds_type?: string,
    datasource_name?: string,
    datasource_exists: boolean = true,
    records: Array<ChatRecord> = [],
    recommended_question?: string | undefined,
    recommended_generate?: boolean | undefined
  ) {
    super()
    if (param1 !== undefined) {
      if (param1 instanceof Chat) {
        this.id = param1.id
        this.create_time = getDate(param1.create_time)
        this.create_by = param1.create_by
        this.brief = param1.brief
        this.chat_type = param1.chat_type
        this.datasource = param1.datasource
        this.engine_type = param1.engine_type
        this.ds_type = param1.ds_type
        this.recommended_question = recommended_question
        this.recommended_generate = recommended_generate
      } else {
        this.id = param1
        this.create_time = getDate(create_time)
        this.create_by = create_by
        this.brief = brief
        this.chat_type = chat_type
        this.datasource = datasource
        this.engine_type = engine_type
        this.ds_type = ds_type
        this.recommended_question = recommended_question
        this.recommended_generate = recommended_generate
      }
    }
    this.datasource_name = datasource_name
    this.datasource_exists = datasource_exists
    this.records = records
  }
}

const toChatRecord = (data?: any): ChatRecord | undefined => {
  if (!data) {
    return undefined
  }
  const record = new ChatRecord(
    data.id,
    data.chat_id,
    data.create_time,
    data.finish_time,
    data.question,
    data.sql_answer,
    data.sql,
    data.datasource,
    data.data,
    data.chart_answer,
    data.chart,
    data.analysis,
    data.analysis_thinking,
    data.predict,
    data.predict_content,
    data.predict_data,
    data.finish,
    data.error,
    data.run_time,
    data.first_chat,
    data.recommended_question,
    data.duration,
    data.total_tokens
  )
  record.run_id = data.run_id
  record.run_attempt_index = Number(data.run_attempt_index || 0)
  record.turn_answer = parseTurnAnswer(data.answer)
  record.answer = turnAnswerToPayload(data.answer) || record.answer
  record.answer_revision = Number(data.answer_revision || 0)
  record.turn_kind = data.turn_kind
  record.relation = data.relation
  record.reference_record_ids = data.reference_record_ids || []
  record.run_status = data.run_status
  record.run_event_cursor = Number(data.run_event_cursor || 0)
  record.active_interrupt = data.active_interrupt
  record.interrupts = data.interrupts || []
  record.intent_reasoning_content = data.intent_reasoning_content
  return record
}
const toChatRecordList = (list: any = []): ChatRecord[] => {
  const records: Array<ChatRecord> = []
  for (let i = 0; i < list.length; i++) {
    const record = toChatRecord(list[i])
    if (record) {
      records.push(record)
    }
  }
  return records
}

export class ChatLogHistoryItem {
  id?: number | string
  start_time?: Date | string
  finish_time?: Date | string
  duration?: number | undefined
  total_tokens?: number | undefined
  operate?: string | undefined
  operate_key?: string | undefined
  local_operation?: boolean | undefined
  error?: boolean | undefined
  message?: any
  status?: 'running' | 'success' | 'degraded' | 'failed' | 'interrupted'
  phase?: string
  graph_node?: string
  title_key?: string
  title_params?: Record<string, any>
  summary_key?: string
  summary_params?: Record<string, any>
  batch_index?: number
  attempt_index?: number
  unit_index?: number
  detail?: Record<string, any>
  input?: any
  output?: any
  reasoning_content?: string

  constructor()
  constructor(
    start_time: Date | string,
    finish_time: Date | string,
    duration: number | undefined,
    total_tokens: number | undefined,
    operate: string | undefined,
    local_operation: boolean | undefined,
    error: boolean | undefined,
    message: any | undefined
  )
  constructor(
    start_time?: Date | string,
    finish_time?: Date | string,
    duration?: number | undefined,
    total_tokens?: number | undefined,
    operate?: string | undefined,
    local_operation?: boolean | undefined,
    error?: boolean | undefined,
    message?: any | undefined
  ) {
    this.start_time = getDate(start_time)
    this.finish_time = getDate(finish_time)
    this.duration = duration
    this.total_tokens = total_tokens
    this.operate_key = operate
    // Enum member names (GENERATE_QUERY / EXECUTE_QUERY / …) are stored by value
    // ('0'/'12'/…); history resolves missing value→name via OperationEnum, so labels
    // always come from current i18n keys. No SQL-era name remap is needed.
    this.operate = t('chat.log.' + operate)
    this.local_operation = !!local_operation
    this.error = !!error
    this.message = message
  }
}

export class ChatLogHistory {
  start_time?: Date | string
  finish_time?: Date | string
  duration?: number | undefined
  elapsed_duration?: number | undefined
  waiting_duration?: number | undefined
  total_tokens?: number | undefined
  steps?: Array<ChatLogHistoryItem> | undefined
  run?: {
    run_id?: string
    status?: string
    current_node?: string
    dispatch_attempts?: number
    started_at?: Date | string
    completed_at?: Date | string
    update_time?: Date | string
  }
  attempts?: Array<{
    run_id: string
    status?: string
    current_node?: string
    dispatch_attempts?: number
    started_at?: Date | string
    completed_at?: Date | string
    update_time?: Date | string
  }>

  constructor()
  constructor(
    start_time: Date | string,
    finish_time: Date | string,
    duration: number | undefined,
    total_tokens: number | undefined,
    steps: Array<ChatLogHistoryItem> | undefined
  )
  constructor(
    start_time?: Date | string,
    finish_time?: Date | string,
    duration?: number | undefined,
    total_tokens?: number | undefined,
    steps?: Array<ChatLogHistoryItem> | undefined
  ) {
    this.start_time = getDate(start_time)
    this.finish_time = getDate(finish_time)
    this.duration = duration
    this.total_tokens = total_tokens
    this.steps = steps ? steps : []
  }
}

const toChatLogHistoryItem = (data?: any): any | undefined => {
  if (!data) {
    return undefined
  }
  const item = new ChatLogHistoryItem(
    data.start_time,
    data.finish_time,
    data.duration,
    data.total_tokens,
    data.operate,
    data.local_operation,
    data.error,
    data.message
  )
  ;(item as any).id = data.id
  Object.assign(item, {
    status: data.status,
    phase: data.phase,
    graph_node: data.graph_node,
    title_key: data.title_key,
    title_params: data.title_params || {},
    summary_key: data.summary_key,
    summary_params: data.summary_params || {},
    batch_index: data.batch_index,
    attempt_index: data.attempt_index,
    unit_index: data.unit_index,
    detail: data.detail || {},
    input: data.input,
    output: data.output,
    reasoning_content: data.reasoning_content,
  })
  return item
}

const toChatLogHistoryItemList = (list: any = []): ChatLogHistoryItem[] => {
  const records: Array<ChatLogHistoryItem> = []
  for (let i = 0; i < list.length; i++) {
    const record = toChatLogHistoryItem(list[i])
    if (record) {
      records.push(record)
    }
  }
  return records
}

const toChatLogHistory = (data?: any): ChatLogHistory | undefined => {
  if (!data) {
    return undefined
  }
  const history = new ChatLogHistory(
    data.start_time,
    data.finish_time,
    data.duration,
    data.total_tokens,
    toChatLogHistoryItemList(data.steps)
  )
  history.elapsed_duration = data.elapsed_duration
  history.waiting_duration = data.waiting_duration
  history.run = data.run || {}
  history.attempts = data.attempts || []
  return history
}

export const chatApi = {
  toChatInfo: (data?: any): ChatInfo | undefined => {
    if (!data) {
      return undefined
    }
    return new ChatInfo(
      data.id,
      data.create_time,
      data.create_by,
      data.brief,
      data.chat_type,
      data.datasource,
      data.engine_type,
      data.ds_type,
      data.datasource_name,
      data.datasource_exists,
      toChatRecordList(data.records),
      data.recommended_question,
      data.recommended_generate
    )
  },
  toChatInfoList: (list: any[] = []): ChatInfo[] => {
    const infos: Array<ChatInfo> = []
    for (let i = 0; i < list.length; i++) {
      const chatInfo = chatApi.toChatInfo(list[i])
      if (chatInfo) {
        infos.push(chatInfo)
      }
    }
    return infos
  },
  toChatLogHistory,
  list: (): Promise<Array<ChatInfo>> => {
    return request.get('/chat/list')
  },
  get: (id: number): Promise<ChatInfo> => {
    return request.get(`/chat/${id}`)
  },
  get_with_Data: (id: number): Promise<ChatInfo> => {
    return request.get(`/chat/${id}/with_data`)
  },
  get_chart_data: (record_id?: number): Promise<AnswerPayload> => {
    return request.get(`/chat/record/${record_id}/data`)
  },
  get_chart_predict_data: (record_id?: number): Promise<any> => {
    return request.get(`/chat/record/${record_id}/predict_data`)
  },
  get_chart_log_history: async (
    record_id?: number,
    options?: { silent?: boolean; runId?: string }
  ): Promise<ChatLogHistory | undefined> => {
    const runQuery = options?.runId ? `?run_id=${encodeURIComponent(options.runId)}` : ''
    const response = await request.get(
      `/chat/record/${record_id}/log${runQuery}`,
      options?.silent ? { requestOptions: { silent: true } } : undefined
    )
    return toChatLogHistory(response)
  },
  get_chart_usage: (record_id?: number): Promise<any> => {
    return request.get(`/chat/record/${record_id}/usage`)
  },
  submitFeedback: (record_id: number, feedback: string | null): Promise<any> => {
    return request.post(`/chat/record/${record_id}/feedback`, { feedback })
  },
  startChat: (data: any): Promise<ChatInfo> => {
    return request.post('/chat/start', data)
  },
  startAssistantChat: (data?: any): Promise<ChatInfo> => {
    return request.post('/chat/assistant/start', Object.assign({ origin: 2 }, data))
  },
  renameChat: (chat_id: number | undefined, brief: string): Promise<string> => {
    return request.post('/chat/rename', { id: chat_id, brief: brief })
  },
  deleteChat: (id: number | undefined, brief: any): Promise<string> => {
    return request.delete(`/chat/${id}`, { data: { id: id, brief: brief } })
  },
  analysis: (record_id: number | undefined, controller?: AbortController) => {
    return request.fetchStream(`/chat/record/${record_id}/analysis`, {}, controller)
  },
  predict: (record_id: number | undefined, controller?: AbortController) => {
    return request.fetchStream(`/chat/record/${record_id}/predict`, {}, controller)
  },
  recommendQuestions: (
    record_id: number | undefined,
    controller?: AbortController,
    params?: any
  ) => {
    return request.fetchStream(`/chat/recommend_questions/${record_id}${params}`, {}, controller)
  },
  recentQuestions: (datasource_id?: number): Promise<any> => {
    return request.get(`/chat/recent_questions/${datasource_id}`)
  },
  checkLLMModel: () => request.get('/system/aimodel/default', { requestOptions: { silent: true } }),
  export2Excel: (record_id: number | undefined, chat_id: any) =>
    request.get(`/chat/record/${record_id}/excel/export/${chat_id}`, {
      responseType: 'blob',
      requestOptions: { customError: true },
    }),
}
