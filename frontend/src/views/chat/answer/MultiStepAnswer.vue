<script setup lang="ts">
import BaseAnswer from './BaseAnswer.vue'
import {
  Chat,
  ChatInfo,
  type AnswerPayload,
  type AnswerPresentation,
  type ChatMessage,
  ChatRecord,
  type ConversationInterrupt,
  type ResumeAnswer,
  type ResultQuality,
} from '@/api/chat.ts'
import { computed, nextTick, onBeforeUnmount, ref, watch, type Ref } from 'vue'
import ChartBlock from '@/views/chat/chat-block/ChartBlock.vue'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import SQLComponent from '@/views/chat/component/SQLComponent.vue'
import type { ChatStreamEvent } from '@/hooks/useChatStream'
import { useConversationTurn } from '@/features/conversation/useConversationTurn'
import { useI18n } from 'vue-i18n'
import icon_sql_outlined from '@/assets/svg/icon_sql_outlined.svg'
import ClarificationCard from '@/features/conversation/ClarificationCard.vue'
import QualityStamp from '@/features/conversation/QualityStamp.vue'
import AgentStagesView, { type AgentStageItem } from './AgentStagesView.vue'
import { conversationStageKey } from '@/features/conversation/executionLog'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface StepState {
  index: number
  title: string
  presentation: AnswerPresentation | undefined
  sql: string
  /** Chart config JSON string (same contract as ChatRecord.chart). */
  chart: string
  /** Chart data object {fields, data, ...} — never the multi-step envelope. */
  data:
    | {
        fields?: string[]
        data?: any[]
        fields_info?: any
        limit?: number
        row_count?: number
        truncated?: boolean
        truncation_reason?: string
      }
    | undefined
  recordId: number | undefined
  datasource: number | undefined
  engineType: string | undefined
  error: string
  loading: boolean
  showSql: boolean
}

// ---------------------------------------------------------------------------
// Props & emits
// ---------------------------------------------------------------------------

const props = withDefaults(
  defineProps<{
    recordId?: number
    chatList?: Array<ChatInfo>
    currentChatId?: number
    currentChat?: ChatInfo
    message?: ChatMessage
    loading?: boolean
  }>(),
  {
    recordId: undefined,
    chatList: () => [],
    currentChatId: undefined,
    currentChat: () => new ChatInfo(),
    message: undefined,
    loading: false,
  }
)

const emits = defineEmits([
  'finish',
  'error',
  'stop',
  'scrollBottom',
  'update:loading',
  'update:chatList',
  'update:currentChat',
  'update:currentChatId',
])

const { t } = useI18n()

const index = computed(() => {
  if (props.message?.index) return props.message.index
  if (props.message?.index === 0) return 0
  return -1
})

const _currentChatId = computed({
  get() {
    return props.currentChatId
  },
  set(v) {
    emits('update:currentChatId', v)
  },
})

const _currentChat = computed({
  get() {
    return props.currentChat
  },
  set(v) {
    emits('update:currentChat', v)
  },
})

const _chatList = computed({
  get() {
    return props.chatList
  },
  set(v) {
    emits('update:chatList', v)
  },
})

const _loading = computed({
  get() {
    return props.loading
  },
  set(v) {
    emits('update:loading', v)
  },
})

// ---------------------------------------------------------------------------
// Step state
// ---------------------------------------------------------------------------

const steps: Ref<Array<StepState>> = ref([])
const agentStages: Ref<Array<AgentStageItem>> = ref([])
const analysisText = ref('')
const analysisThinking = ref('')
const overallQuality = ref<ResultQuality>()
let hydratedTerminalRecordId: number | undefined
let activeChartReasoningIndex: number | undefined

const isMultiStep = computed(
  () => steps.value.filter((s) => s.sql || s.chart || s.error).length > 1
)

const recordReasoningNames = computed(
  () => ['intent_reasoning_content', 'sql_answer', 'chart_answer', 'analysis_thinking'] as const
)

const visibleInterrupts = computed<ConversationInterrupt[]>(() => {
  const record = props.message?.record
  const interrupts = (record?.interrupts || []).filter((item) => item.status !== 'cancelled')
  if (
    record?.active_interrupt &&
    !interrupts.some((item) => item.interrupt_id === record.active_interrupt?.interrupt_id)
  ) {
    interrupts.push(record.active_interrupt)
  }
  return interrupts
})

const isAwaitingInput = computed(() => props.message?.record?.run_status === 'awaiting_input')

const runStageText = computed(() => {
  const record = props.message?.record
  if (record?.run_status === 'queued') {
    return record.run_dispatch_attempts > 1
      ? t('qa.run_stage_redispatch')
      : t('qa.run_stage_queued')
  }
  return t(conversationStageKey(record?.run_current_node))
})

function toChartJson(chart: unknown): string {
  if (chart == null || chart === '') return ''
  if (typeof chart === 'string') return chart
  try {
    return JSON.stringify(chart)
  } catch {
    return ''
  }
}

/**
 * Build a virtual ChatMessage for ChartBlock.
 * ChartBlock mounts charts by DOM id derived from record.id — pass instanceId=step.index.
 */
function buildStepMessage(step: StepState): ChatMessage {
  const record = new ChatRecord()
  // Keep a stable numeric-ish id for toolkit actions; DOM uniqueness is instanceId.
  record.id = step.recordId
  record.chat_id = _currentChatId.value
  record.sql = step.sql
  record.chart = step.chart
  record.data = step.data
  record.datasource = step.datasource
  record.engine_type = step.engineType
  record.finish = true
  return {
    role: 'assistant',
    record,
    index: step.index,
  } as ChatMessage
}

function ensureStep(stepIndex: number): StepState {
  while (steps.value.length <= stepIndex) {
    steps.value.push({
      index: steps.value.length,
      title: '',
      presentation: undefined,
      sql: '',
      chart: '',
      data: undefined,
      recordId: undefined,
      datasource: undefined,
      engineType: undefined,
      error: '',
      loading: false,
      showSql: false,
    })
  }
  return steps.value[stepIndex]
}

function appendReasoningToRecord(
  kind: 'sql_answer' | 'chart_answer' | 'analysis_thinking',
  text: string
) {
  if (!text || index.value < 0) return
  const rec = _currentChat.value.records[index.value] as any
  rec[kind] = (rec[kind] || '') + text
}

/**
 * Apply the canonical terminal answer payload to all steps.
 */
function applyFullPayload(payload: AnswerPayload, recordId?: number, authoritative = false) {
  if (!payload) return

  // Quality evaluates an actual published result. A planning failure with no
  // result steps must not be rendered as a misleading zero-score stamp.
  const publishedQuality = payload.steps.length > 0 ? payload.outcome.quality : undefined
  if (authoritative) {
    steps.value = []
    analysisText.value = payload.analysis || ''
    overallQuality.value = publishedQuality
    if (Array.isArray((payload as any).stages)) {
      agentStages.value = (payload as any).stages
    }
  } else {
    if (Array.isArray((payload as any).stages)) {
      agentStages.value = (payload as any).stages
    }
    if (payload.analysis) analysisText.value = payload.analysis
    overallQuality.value = publishedQuality
  }
  payload.steps.forEach((stepPayload, i) => {
    const step = ensureStep(i)
    if (recordId !== undefined) step.recordId = recordId
    if (stepPayload.sql) step.sql = stepPayload.sql
    if (stepPayload.presentation) {
      step.presentation = stepPayload.presentation
      step.title = stepPayload.presentation.title || stepPayload.brief
    } else if (stepPayload.brief) {
      step.title = stepPayload.brief
    }
    if (stepPayload.chart != null && stepPayload.chart !== '') {
      step.chart = toChartJson(stepPayload.chart)
    }
    if (stepPayload.error) {
      step.error = String(stepPayload.error)
    }
    if (stepPayload.data !== undefined) {
      step.data = stepPayload.data
    } else if (!step.error) {
      step.data = { fields: [], data: [] }
    }
    step.loading = false
  })
  if (steps.value.length > payload.steps.length) {
    if (authoritative) {
      steps.value.splice(payload.steps.length)
    } else {
      // Progressive snapshots must not erase SQL tokens that arrived over
      // SSE but have not reached persistence yet.
      while (
        steps.value.length > payload.steps.length &&
        !steps.value[steps.value.length - 1].sql &&
        !steps.value[steps.value.length - 1].chart
      ) {
        steps.value.pop()
      }
    }
  }
}

function hydrateRecordData(record: ChatRecord, authoritative = false): boolean {
  if (!record.id || !record.answer) return false
  applyFullPayload(record.answer, record.id, authoritative)
  if (steps.value[0]) {
    if (steps.value[0].sql) record.sql = steps.value[0].sql
    if (steps.value[0].chart) record.chart = steps.value[0].chart as any
    if (steps.value[0].engineType) record.engine_type = steps.value[0].engineType
    if (authoritative) record.analysis = analysisText.value
  }
  emits('scrollBottom')
  return true
}

function hydrateHistory(record: ChatRecord) {
  analysisText.value = ''
  analysisThinking.value = ''
  overallQuality.value = undefined
  steps.value = []
  agentStages.value = []

  if (record.run_status === 'awaiting_input') {
    return
  }

  if (record.answer) {
    applyFullPayload(record.answer, record.id, true)
    if (agentStages.value.length === 0 && Array.isArray((record as any).agent_stages) && (record as any).agent_stages.length > 0) {
      agentStages.value = (record as any).agent_stages
    }
    hydratedTerminalRecordId = record.id
    return
  }

  if ((record as any).analysis) {
    const raw = String((record as any).analysis)
    try {
      if (raw.trim().startsWith('{')) {
        const obj = JSON.parse(raw)
        analysisText.value = obj.content || raw
      } else {
        analysisText.value = raw
      }
    } catch {
      analysisText.value = raw
    }
  }
  if ((record as any).analysis_thinking) {
    analysisThinking.value = String((record as any).analysis_thinking)
  }

  // Seed single-record columns while multi payload loads
  if (record.sql || record.chart) {
    const step = ensureStep(0)
    step.sql = record.sql || ''
    step.chart = toChartJson(record.chart)
    step.recordId = record.id
    step.datasource = record.datasource
    step.engineType = record.engine_type
    step.loading = true
  }

  if (hydrateRecordData(record, true)) hydratedTerminalRecordId = record.id
}

// ---------------------------------------------------------------------------
// SSE stream
// ---------------------------------------------------------------------------

const turn = useConversationTurn({ bigInt: true })

function turnHandlers(currentRecord: ChatRecord) {
  return {
    onEvent: async (data: ChatStreamEvent) => {
      switch (data.type) {
        case 'question':
          currentRecord.question = data.question
          break
        case 'info':
          console.info(data.msg)
          break
        case 'brief':
          _currentChat.value.brief = data.brief
          _chatList.value.forEach((chat: Chat) => {
            if (chat.id === _currentChat.value.id) chat.brief = data.brief
          })
          break
        case 'datasource':
          if (!_currentChat.value.datasource) _currentChat.value.datasource = data.id
          break
        case 'batch-start':
          currentRecord.sql_answer = ''
          currentRecord.chart_answer = ''
          activeChartReasoningIndex = undefined
          break
        case 'step-sql-result':
          appendReasoningToRecord('sql_answer', data.reasoning_content ?? '')
          break
        case 'step-chart-result': {
          const chartIndex = Number(data.index ?? 0)
          if (activeChartReasoningIndex !== chartIndex) {
            currentRecord.chart_answer = ''
            activeChartReasoningIndex = chartIndex
          }
          appendReasoningToRecord('chart_answer', data.reasoning_content ?? '')
          break
        }
        case 'agent-thought': {
          const thought = data.content ?? ''
          const lastStage = agentStages.value[agentStages.value.length - 1]
          if (lastStage && lastStage.type === 'thought' && lastStage.status === 'running') {
            lastStage.content = (lastStage.content || '') + thought
          } else {
            if (lastStage && lastStage.status === 'running') {
              lastStage.status = 'completed'
            }
            agentStages.value.push({
              id: `thought-${Date.now()}-${agentStages.value.length}`,
              type: 'thought',
              title: t('chat.log.AGENT_STEP') || '思考',
              content: thought,
              status: 'running',
            })
          }
          break
        }
        case 'agent-tool-call': {
          const lastStage = agentStages.value[agentStages.value.length - 1]
          if (lastStage && lastStage.status === 'running') {
            lastStage.status = 'completed'
          }
          const tName = data.tool || ''
          const tLabel = data.displayName || `工具调用 (${tName})`
          agentStages.value.push({
            id: `tool-${Date.now()}-${agentStages.value.length}`,
            type: 'tool',
            title: tLabel,
            toolName: tName,
            toolArgs: data.args || {},
            sql: data.args?.sql || undefined,
            status: 'running',
          })
          break
        }
        case 'analysis': {
          const lastStage = agentStages.value[agentStages.value.length - 1]
          if (lastStage && lastStage.status === 'running') {
            lastStage.status = 'completed'
          }
          analysisText.value += data.content ?? ''
          const reasoning = data.reasoning_content ?? ''
          analysisThinking.value += reasoning
          appendReasoningToRecord('analysis_thinking', reasoning)
          break
        }
        case 'analysis-reasoning':
        case 'prediction-reasoning': {
          const reasoning = data.reasoning_content || data.content || ''
          analysisThinking.value += reasoning
          appendReasoningToRecord('analysis_thinking', reasoning)
          break
        }
        case 'clarification-reasoning':
          currentRecord.intent_reasoning_content =
            (currentRecord.intent_reasoning_content || '') +
            (data.reasoning_content || data.content || '')
          break
      }
      await nextTick()
    },
    onError: (record: ChatRecord) => emits('error', record.id),
    onFinish: async (record: ChatRecord) => {
      agentStages.value.forEach((s) => {
        if (s.status === 'running') s.status = 'completed'
      })
      if (analysisText.value) currentRecord.analysis = analysisText.value
      if (record.id && record.run_status !== 'awaiting_input') {
        if (hydrateRecordData(record, true)) hydratedTerminalRecordId = record.id
      }
      emits('finish', record.id, record.run_status)
    },
    onDone: () => {
      _loading.value = false
    },
  }
}

const sendMessage = async () => {
  _loading.value = true

  if (index.value < 0) {
    _loading.value = false
    return
  }

  const currentRecord: ChatRecord = _currentChat.value.records[index.value]
  if (_currentChatId.value === undefined) {
    _loading.value = false
    return
  }

  steps.value = []
  agentStages.value = []
  analysisText.value = ''
  analysisThinking.value = ''
  overallQuality.value = undefined
  activeChartReasoningIndex = undefined

  try {
    await turn.run(_currentChatId.value, currentRecord, turnHandlers(currentRecord))
  } finally {
    _loading.value = false
  }
}

const regenerate = async () => {
  const currentRecord = props.message?.record
  if (!currentRecord?.id || !_currentChatId.value || _loading.value) return
  _loading.value = true
  try {
    await turn.run(_currentChatId.value, currentRecord, turnHandlers(currentRecord), {
      regenerate: true,
    })
  } finally {
    _loading.value = false
  }
}

async function resumeClarification(payload: {
  interrupt: ConversationInterrupt
  answers: ResumeAnswer[]
  displayText: string
}) {
  const currentRecord = props.message?.record
  if (!currentRecord || _loading.value) return
  _loading.value = true

  try {
    await turn.resume(
      currentRecord,
      payload.interrupt,
      payload.answers,
      turnHandlers(currentRecord)
    )
  } finally {
    _loading.value = false
  }
}

async function correctClarification(payload: {
  interrupt: ConversationInterrupt
  answer: ResumeAnswer
  supersedesEvidenceId: string
}) {
  const currentRecord = props.message?.record
  if (!currentRecord || _loading.value) return
  _loading.value = true
  try {
    await turn.correct(
      currentRecord,
      payload.interrupt,
      payload.answer,
      payload.supersedesEvidenceId,
      turnHandlers(currentRecord)
    )
  } finally {
    _loading.value = false
  }
}

function stop() {
  turn.detach()
  _loading.value = false
  emits('stop')
}

const enableThousandsSeparatorList = ref<Array<string>>([])
const showLabel = ref<boolean>(false)

const reasoningItems = computed(() =>
  recordReasoningNames.value
    .map((name) => props.message?.record?.[name])
    .filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
)

onBeforeUnmount(() => {
  turn.detach()
  _loading.value = false
})

watch(
  () =>
    [
      props.message?.record?.run_id,
      props.message?.record?.run_status,
      props.message?.record?.id,
    ] as const,
  ([runId, status]) => {
    const record = props.message?.record
    if (!record || !runId) return
    if (status === 'awaiting_input') {
      // Snapshot-only: clarification card already lives on the record.
      void turn.attach(record, turnHandlers(record))
      return
    }
    if (!['queued', 'running'].includes(status || '')) return
    // Live send/resume already owns the subscription — do not wipe buffers.
    if (turn.owned.value || turn.running.value) return
    // Replay from cursor 0 — clear local stream buffers so append handlers
    // do not duplicate anything already mirrored onto the record.
    steps.value = []
    analysisText.value = ''
    analysisThinking.value = ''
    overallQuality.value = undefined
    activeChartReasoningIndex = undefined
    record.sql_answer = ''
    record.chart_answer = ''
    record.intent_reasoning_content = ''
    record.analysis_thinking = ''
    _loading.value = true
    void turn.attach(record, turnHandlers(record)).finally(() => {
      if (!turn.owned.value && !turn.running.value) {
        _loading.value = false
      }
    })
  },
  { immediate: true }
)

watch(
  () =>
    [props.message?.record?.id, props.message?.record?.finish, props.message?.isTyping] as const,
  ([recordId, finish, typing]) => {
    if (
      recordId &&
      finish &&
      !typing &&
      props.message?.record?.run_status !== 'awaiting_input' &&
      hydratedTerminalRecordId !== recordId &&
      props.message?.record
    ) {
      hydrateHistory(props.message.record)
    }
  },
  { immediate: true }
)

defineExpose({ sendMessage, regenerate, index: () => index.value, stop })
</script>

<template>
  <BaseAnswer v-if="message" :message="message" :reasoning-items="reasoningItems">
    <div v-if="_loading && steps.length === 0 && !isAwaitingInput" class="multi-step-loading">
      <span>{{ runStageText }}</span>
    </div>

    <AgentStagesView
      v-if="agentStages.length > 0"
      :stages="agentStages"
      :is-typing="message?.isTyping"
    />

    <ClarificationCard
      v-for="interrupt in visibleInterrupts"
      :key="interrupt.interrupt_id"
      :interrupt="interrupt"
      :disabled="_loading"
      :correctable="isAwaitingInput && interrupt.status === 'consumed'"
      @submit="resumeClarification"
      @correct="correctClarification"
    />

    <div v-if="!isAwaitingInput" class="multi-step-container">
      <div v-if="overallQuality" class="result-quality-toolbar">
        <QualityStamp :quality="overallQuality" />
      </div>

      <div
        v-for="step in steps"
        :key="`step-${step.recordId ?? 'x'}-${step.index}`"
        :class="isMultiStep ? 'step-card' : 'single-step-block'"
      >
        <template v-if="isMultiStep">
          <div class="step-header">
            <span class="step-number">{{ step.index + 1 }}</span>
            <span class="step-title">
              {{ step.title || t('chat.chart_type.table') + ' ' + (step.index + 1) }}
            </span>
            <el-button
              v-if="step.sql"
              class="step-sql-toggle"
              text
              size="small"
              @click="step.showSql = !step.showSql"
            >
              <el-icon size="14">
                <icon_sql_outlined />
              </el-icon>
              <span class="step-sql-toggle-text">
                {{ step.showSql ? t('chat.collapse_sql') : t('chat.show_query') }}
              </span>
            </el-button>
          </div>

          <div v-if="step.showSql && step.sql" class="step-sql-block">
            <SQLComponent :sql="step.sql" />
          </div>
        </template>

        <template v-else>
          <div v-if="step.sql" class="single-step-toolbar">
            <el-button
              v-if="step.sql"
              class="step-sql-toggle"
              text
              size="small"
              @click="step.showSql = !step.showSql"
            >
              <el-icon size="14">
                <icon_sql_outlined />
              </el-icon>
              <span class="step-sql-toggle-text">
                {{ step.showSql ? t('chat.collapse_sql') : t('chat.show_query') }}
              </span>
            </el-button>
          </div>
          <div v-if="step.showSql && step.sql" class="step-sql-block">
            <SQLComponent :sql="step.sql" />
          </div>
        </template>

        <div v-if="step.error" class="step-error">
          <el-alert :title="step.error" type="error" show-icon :closable="false" />
        </div>

        <div v-if="step.chart || step.loading || step.data" class="step-chart-wrapper">
          <ChartBlock
            v-if="step.chart && step.data !== undefined"
            :key="`chart-${step.recordId}-${step.index}-${(step.data?.fields || []).join(',')}`"
            v-model:show-label="showLabel"
            v-model:thousands-separator-list="enableThousandsSeparatorList"
            :message="buildStepMessage(step)"
            :record-id="step.recordId"
            :instance-id="step.index"
            :loading-data="step.loading"
          />
          <div v-else-if="step.loading" class="step-chart-loading">
            <span>{{ t('chat.loading_data') }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="analysisText" class="multi-step-analysis">
      <div class="analysis-label">{{ t('chat.summary') }}</div>
      <MdComponent :message="analysisText" />
    </div>

    <slot></slot>
    <template #tool>
      <slot name="tool"></slot>
    </template>
    <template #footer>
      <slot name="footer"></slot>
    </template>
  </BaseAnswer>
</template>

<style scoped lang="less">
.multi-step-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  color: rgba(100, 106, 115, 1);
  font-size: 14px;
  line-height: 22px;
}

.multi-step-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 6px;
}

.step-card {
  padding: 16px;
  border: 1px solid rgba(222, 224, 227, 1);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-quality-toolbar {
  display: flex;
  justify-content: flex-end;
}

.single-step-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 28px;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--ed-color-primary, rgba(28, 186, 144, 1));
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  line-height: 22px;
  color: rgba(31, 35, 41, 1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-sql-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 24px;
  padding: 0 6px;
  font-size: 13px;
  color: rgba(100, 106, 115, 1);

  &:hover {
    background: rgba(31, 35, 41, 0.06);
    border-radius: 4px;
  }
}

.step-sql-toggle-text {
  font-size: 13px;
  line-height: 20px;
}

.step-sql-block {
  border-radius: 6px;
  overflow: hidden;
}

.step-error {
  margin-top: 4px;
}

.step-chart-wrapper {
  min-height: 80px;
}

.step-chart-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  color: rgba(100, 106, 115, 1);
}

.single-step-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 4px;
}

.multi-step-analysis {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid rgba(222, 224, 227, 1);
  border-radius: 12px;
  background: rgba(248, 249, 250, 1);
}

.analysis-label {
  font-size: 14px;
  font-weight: 500;
  line-height: 22px;
  color: rgba(31, 35, 41, 1);
  margin-bottom: 8px;
}
</style>
