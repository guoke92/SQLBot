<script setup lang="ts">
import BaseAnswer from './BaseAnswer.vue'
import {
  Chat,
  chatApi,
  ChatInfo,
  type ChatMessage,
  ChatRecord,
  type IntentContext,
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

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface StepState {
  index: number
  title: string
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
  'clarification-submit',
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
const analysisText = ref('')
const analysisThinking = ref('')
let hydrateSeq = 0
let hydratedTerminalRecordId: number | undefined
let activeChartReasoningIndex: number | undefined

const isMultiStep = computed(
  () => steps.value.filter((s) => s.sql || s.chart || s.error).length > 1
)

const recordReasoningNames = computed(
  () => ['intent_reasoning_content', 'sql_answer', 'chart_answer', 'analysis_thinking'] as const
)

const intentContext = computed<IntentContext | undefined>(
  () => props.message?.record?.intent_context
)

const isIntentTerminal = computed(() =>
  ['needs_clarification', 'blocked'].includes(intentContext.value?.status || '')
)

const clarificationAnswered = computed(() => {
  const recordId = props.message?.record?.id
  if (!recordId) return false
  return _currentChat.value.records.some(
    (record) => !!record.id && record.clarification_parent_id === recordId
  )
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
  record.data = step.data as any
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
 * Apply full multi-step / legacy GET /data payload to all steps.
 * Never assigns the multi envelope onto a single step's `data`.
 */
function applyFullPayload(payload: any, recordId?: number, authoritative = false) {
  if (!payload) return

  if (Array.isArray(payload.steps)) {
    if (authoritative) {
      steps.value = []
      analysisText.value = String(payload.analysis || '')
    } else if (payload.analysis) {
      analysisText.value = String(payload.analysis)
    }
    payload.steps.forEach((stepPayload: any, i: number) => {
      const step = ensureStep(i)
      if (recordId !== undefined) step.recordId = recordId
      if (stepPayload?.sql) step.sql = stepPayload.sql
      if (stepPayload?.brief) step.title = stepPayload.brief
      if (stepPayload?.chart != null && stepPayload.chart !== '') {
        step.chart = toChartJson(stepPayload.chart)
      }
      if (stepPayload?.error) {
        step.error = String(stepPayload.error)
      }
      // Chart data object only
      if (stepPayload?.data !== undefined && stepPayload?.data !== null) {
        step.data = stepPayload.data
      } else if (!step.error) {
        // Explicit empty result with chart still present
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
        // Only trim fully empty trailing placeholders.
        while (
          steps.value.length > payload.steps.length &&
          !steps.value[steps.value.length - 1].sql &&
          !steps.value[steps.value.length - 1].chart
        ) {
          steps.value.pop()
        }
      }
    }
    return
  }

  // Legacy single payload {fields, data}
  if (authoritative) {
    steps.value = []
  }
  const step = ensureStep(0)
  if (recordId !== undefined) step.recordId = recordId
  step.data = payload
  step.loading = false
}

function hydrateRecordData(recordId?: number, authoritative = false): Promise<boolean> {
  if (!recordId) return Promise.resolve(false)
  const seq = ++hydrateSeq
  // Mark incomplete steps loading for UX
  steps.value.forEach((s) => {
    if (!s.data && !s.error) s.loading = true
  })

  const run = chatApi
    .get_chart_data(recordId)
    .then((response) => {
      if (seq !== hydrateSeq) return false // superseded
      applyFullPayload(response, recordId, authoritative)
      // Mirror first step onto parent record for toolbar / analysis entry points
      if (index.value >= 0 && steps.value[0]) {
        const rec = _currentChat.value.records[index.value]
        if (steps.value[0].sql) rec.sql = steps.value[0].sql
        if (steps.value[0].chart) rec.chart = steps.value[0].chart as any
        if (steps.value[0].engineType) rec.engine_type = steps.value[0].engineType
        if (authoritative) rec.analysis = analysisText.value
      }
      return true
    })
    .catch((err) => {
      if (seq !== hydrateSeq) return false
      console.error('MultiStep hydrateRecordData error:', err)
      steps.value.forEach((s) => {
        if (!s.data && !s.error) {
          s.error = String(err)
          s.loading = false
        }
      })
      return false
    })
    .finally(() => {
      if (seq === hydrateSeq) {
        emits('scrollBottom')
      }
    })

  return run
}

function hydrateHistory(record: ChatRecord) {
  analysisText.value = ''
  analysisThinking.value = ''
  steps.value = []
  hydrateSeq++

  if (
    record.intent_context &&
    ['needs_clarification', 'blocked'].includes(record.intent_context.status)
  ) {
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

  void hydrateRecordData(record.id, true).then((hydrated) => {
    if (hydrated) hydratedTerminalRecordId = record.id
  })
}

// ---------------------------------------------------------------------------
// SSE stream
// ---------------------------------------------------------------------------

const turn = useConversationTurn({ bigInt: true })

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
  analysisText.value = ''
  analysisThinking.value = ''
  activeChartReasoningIndex = undefined
  hydrateSeq++

  try {
    await turn.run(_currentChatId.value, currentRecord, {
      onEvent: async (data: ChatStreamEvent) => {
        switch (data.type) {
          case 'regenerate_record_id':
            currentRecord.regenerate_record_id = data.regenerate_record_id
            _currentChat.value.records[index.value].regenerate_record_id = data.regenerate_record_id
            break
          case 'question':
            currentRecord.question = data.question
            _currentChat.value.records[index.value].question = data.question
            break
          case 'info':
            console.info(data.msg)
            break
          case 'brief':
            _currentChat.value.brief = data.brief
            _chatList.value.forEach((c: Chat) => {
              if (c.id === _currentChat.value.id) {
                c.brief = _currentChat.value.brief
              }
            })
            break
          case 'datasource':
            if (!_currentChat.value.datasource) {
              _currentChat.value.datasource = data.id
            }
            break

          case 'batch-start': {
            currentRecord.sql_answer = ''
            currentRecord.chart_answer = ''
            activeChartReasoningIndex = undefined
            break
          }
          case 'batch-plans':
            break

          case 'step-sql-result': {
            const reason = data.reasoning_content ?? ''
            appendReasoningToRecord('sql_answer', reason)
            break
          }
          case 'step-chart-result': {
            const chartIndex = Number(data.index ?? 0)
            if (activeChartReasoningIndex !== chartIndex) {
              currentRecord.chart_answer = ''
              activeChartReasoningIndex = chartIndex
            }
            const reason = data.reasoning_content ?? ''
            appendReasoningToRecord('chart_answer', reason)
            break
          }
          case 'analysis': {
            analysisText.value += data.content ?? ''
            const reason = data.reasoning_content ?? ''
            analysisThinking.value += reason
            appendReasoningToRecord('analysis_thinking', reason)
            break
          }
          case 'clarification-reasoning': {
            currentRecord.intent_reasoning_content =
              (currentRecord.intent_reasoning_content || '') + (data.content || '')
            break
          }
          case 'clarification':
          case 'clarification-blocked': {
            currentRecord.intent_context = data.intent_context
            _currentChat.value.records[index.value].intent_context = data.intent_context
            break
          }
        }
        await nextTick()
      },
      onError: (record) => {
        emits('error', record.id)
      },
      onFinish: async (record) => {
        if (analysisText.value) {
          ;(_currentChat.value.records[index.value] as any).analysis = analysisText.value
        }
        if (record.id && !isIntentTerminal.value) {
          const hydrated = await hydrateRecordData(record.id, true)
          if (hydrated) hydratedTerminalRecordId = record.id
        }
        emits('finish', record.id, record.intent_context?.status)
      },
      onDone: () => {
        _loading.value = false
      },
    })
  } finally {
    _loading.value = false
  }
}

function stop() {
  turn.stop()
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
  stop()
})

watch(
  () =>
    [props.message?.record?.id, props.message?.record?.finish, props.message?.isTyping] as const,
  ([recordId, finish, typing]) => {
    if (
      recordId &&
      finish &&
      !typing &&
      !isIntentTerminal.value &&
      hydratedTerminalRecordId !== recordId &&
      props.message?.record
    ) {
      hydrateHistory(props.message.record)
    }
  },
  { immediate: true }
)

defineExpose({ sendMessage, index: () => index.value, stop })
</script>

<template>
  <BaseAnswer v-if="message" :message="message" :reasoning-items="reasoningItems">
    <div v-if="_loading && steps.length === 0 && !intentContext" class="multi-step-loading">
      <span>{{ t('qa.thinking') }}</span>
    </div>

    <ClarificationCard
      v-if="intentContext && isIntentTerminal"
      :record-id="message.record?.id"
      :context="intentContext"
      :disabled="_loading"
      :answered="clarificationAnswered"
      @submit="emits('clarification-submit', $event)"
    />

    <div v-if="!isIntentTerminal" class="multi-step-container">
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
          <div v-if="step.sql" class="single-step-sql">
            <el-button
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
            <div v-if="step.showSql" class="step-sql-block">
              <SQLComponent :sql="step.sql" />
            </div>
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

.single-step-sql {
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
