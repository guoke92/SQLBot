<script setup lang="ts">
import BaseAnswer from './BaseAnswer.vue'
import { Chat, chatApi, ChatInfo, type ChatMessage, ChatRecord, questionApi } from '@/api/chat.ts'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, type Ref } from 'vue'
import ChartBlock from '@/views/chat/chat-block/ChartBlock.vue'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import SQLComponent from '@/views/chat/component/SQLComponent.vue'
import { useChatStream, type ChatStreamEvent } from '@/hooks/useChatStream'
import { useI18n } from 'vue-i18n'
import icon_sql_outlined from '@/assets/svg/icon_sql_outlined.svg'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface StepState {
  index: number
  title: string
  sql: string
  sqlReasoning: string
  chartReasoning: string
  /** Chart config JSON string (same contract as ChatRecord.chart). */
  chart: string
  /** Chart data object {fields, data, ...} — never the multi-step envelope. */
  data: { fields?: string[]; data?: any[]; fields_info?: any; limit?: number } | undefined
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
const analysisText = ref('')
const analysisThinking = ref('')
/** In-flight GET /data; coalesces concurrent progressive fetches. */
let hydrateInflight: Promise<void> | null = null
let hydrateSeq = 0

const isMultiStep = computed(() => steps.value.filter((s) => s.sql || s.chart || s.error).length > 1)

const recordReasoningNames = computed(() => ['sql_answer', 'chart_answer', 'analysis_thinking'] as const)

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
      sqlReasoning: '',
      chartReasoning: '',
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

function appendReasoningToRecord(kind: 'sql_answer' | 'chart_answer' | 'analysis_thinking', text: string) {
  if (!text || index.value < 0) return
  const rec = _currentChat.value.records[index.value] as any
  rec[kind] = (rec[kind] || '') + text
}

/**
 * Apply full multi-step / legacy GET /data payload to all steps.
 * Never assigns the multi envelope onto a single step's `data`.
 */
function applyFullPayload(payload: any, recordId?: number) {
  if (!payload) return

  if (Array.isArray(payload.steps)) {
    if (payload.analysis) {
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
    // Drop trailing empty slots if payload is shorter (shouldn't happen)
    if (steps.value.length > payload.steps.length) {
      // keep length so progressive sql from SSE is not wiped mid-stream;
      // only trim fully empty trailing placeholders
      while (
        steps.value.length > payload.steps.length &&
        !steps.value[steps.value.length - 1].sql &&
        !steps.value[steps.value.length - 1].chart
      ) {
        steps.value.pop()
      }
    }
    return
  }

  // Legacy single payload {fields, data}
  const step = ensureStep(0)
  if (recordId !== undefined) step.recordId = recordId
  step.data = payload
  step.loading = false
}

function hydrateRecordData(recordId?: number): Promise<void> {
  if (!recordId) return Promise.resolve()
  const seq = ++hydrateSeq
  // Mark incomplete steps loading for UX
  steps.value.forEach((s) => {
    if (!s.data && !s.error) s.loading = true
  })

  const run = chatApi
    .get_chart_data(recordId)
    .then((response) => {
      if (seq !== hydrateSeq) return // superseded
      applyFullPayload(response, recordId)
      // Mirror first step onto parent record for toolbar / analysis entry points
      if (index.value >= 0 && steps.value[0]) {
        const rec = _currentChat.value.records[index.value]
        if (steps.value[0].sql) rec.sql = steps.value[0].sql
        if (steps.value[0].chart) rec.chart = steps.value[0].chart as any
        if (steps.value[0].engineType) rec.engine_type = steps.value[0].engineType
      }
    })
    .catch((err) => {
      if (seq !== hydrateSeq) return
      console.error('MultiStep hydrateRecordData error:', err)
      steps.value.forEach((s) => {
        if (!s.data && !s.error) {
          s.error = String(err)
          s.loading = false
        }
      })
    })
    .finally(() => {
      if (seq === hydrateSeq) {
        hydrateInflight = null
        emits('scrollBottom')
      }
    })

  hydrateInflight = run
  return run
}

function hydrateHistory(record: ChatRecord) {
  analysisText.value = ''
  analysisThinking.value = ''
  steps.value = []
  hydrateSeq++

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

  hydrateRecordData(record.id).catch(() => {
    /* errors applied in hydrateRecordData */
  })
}

// ---------------------------------------------------------------------------
// SSE stream
// ---------------------------------------------------------------------------

const stream = useChatStream({ bigInt: true })

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
  hydrateSeq++
  hydrateInflight = null

  try {
    stream.createController()
    const param = {
      question: currentRecord.question,
      chat_id: _currentChatId.value,
    }
    await stream.run((controller) => questionApi.add(param, controller) as Promise<Response>, {
      onEvent: async (data: ChatStreamEvent) => {
        switch (data.type) {
          case 'id':
            currentRecord.id = data.id
            _currentChat.value.records[index.value].id = data.id
            break
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

          case 'batch-start':
          case 'batch-plans':
            break

          case 'step-sql-result': {
            const si = Number(data.index ?? 0)
            const step = ensureStep(si)
            const reason = data.reasoning_content ?? ''
            step.sqlReasoning += reason
            appendReasoningToRecord('sql_answer', reason)
            break
          }
          case 'step-sql': {
            const si = Number(data.index ?? 0)
            const step = ensureStep(si)
            step.sql = data.content ?? ''
            if (data.engine_type) step.engineType = data.engine_type
            const title = (data as any).title || (data as any).brief
            if (title) step.title = title
            if (si === 0) {
              _currentChat.value.records[index.value].sql = step.sql
              if (data.engine_type) {
                _currentChat.value.records[index.value].engine_type = data.engine_type
              }
            }
            break
          }
          case 'step-data': {
            // Progressive: one GET hydrates whole multi payload (not step-isolated).
            const si = Number(data.index ?? 0)
            const step = ensureStep(si)
            const rid = data.record_id ?? data.id ?? currentRecord.id
            step.recordId = rid
            if (data.datasource) step.datasource = data.datasource
            step.loading = true
            // Coalesce: only one in-flight fetch; superseding ids cancelled by seq
            if (!hydrateInflight) {
              hydrateRecordData(rid)
            }
            break
          }
          case 'step-error': {
            const si = Number(data.index ?? 0)
            const step = ensureStep(si)
            step.error = String(data.error ?? data.content ?? data.msg ?? '')
            step.loading = false
            break
          }
          case 'step-chart-result': {
            const si = Number(data.index ?? 0)
            const step = ensureStep(si)
            const reason = data.reasoning_content ?? ''
            step.chartReasoning += reason
            appendReasoningToRecord('chart_answer', reason)
            break
          }
          case 'step-chart': {
            const si = Number(data.index ?? 0)
            const step = ensureStep(si)
            step.chart = data.content ?? ''
            // Data may already be present from step-data hydrate
            if (step.data !== undefined) step.loading = false
            if (si === 0) {
              _currentChat.value.records[index.value].chart = step.chart
            }
            break
          }
          case 'analysis': {
            analysisText.value += data.content ?? ''
            const reason = data.reasoning_content ?? ''
            analysisThinking.value += reason
            appendReasoningToRecord('analysis_thinking', reason)
            break
          }
          case 'error':
            currentRecord.error = data.content
            emits('error', currentRecord.id)
            break
          case 'finish':
            if (analysisText.value) {
              ;(_currentChat.value.records[index.value] as any).analysis = analysisText.value
            }
            // Authoritative final hydrate after complete_node persist
            if (currentRecord.id) {
              await hydrateRecordData(currentRecord.id)
            }
            emits('finish', currentRecord.id)
            break
        }
        await nextTick()
      },
      onTransportError: (error) => {
        if (!currentRecord.error) currentRecord.error = ''
        if (currentRecord.error.trim().length !== 0) {
          currentRecord.error = currentRecord.error + '\n'
        }
        currentRecord.error = currentRecord.error + 'Error:' + error
        console.error('Error:', error)
        emits('error')
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
  stream.stop()
  _loading.value = false
  emits('stop')
}

const enableThousandsSeparatorList = ref<Array<string>>([])
const showLabel = ref<boolean>(false)

onBeforeUnmount(() => {
  stop()
})

onMounted(() => {
  if (props.message?.record?.id && props.message?.record?.finish) {
    hydrateHistory(props.message.record)
  }
})

defineExpose({ sendMessage, index: () => index.value, stop })
</script>

<template>
  <BaseAnswer
    v-if="message"
    :message="message"
    :reasoning-name="[...recordReasoningNames]"
    :loading="_loading"
  >
    <div v-if="_loading && steps.length === 0" class="multi-step-loading">
      <span>{{ t('qa.thinking') }}</span>
    </div>

    <div class="multi-step-container">
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
