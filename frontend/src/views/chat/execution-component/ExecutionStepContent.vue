<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatLogHistoryItem } from '@/api/chat'
import { executionStepStatus } from '@/features/conversation/executionLog'

const props = defineProps<{ item: ChatLogHistoryItem }>()
const { t, te } = useI18n()

const translate = (key?: string, params?: Record<string, any>) =>
  key && te(key) ? t(key, params || {}) : ''
const summary = computed(() =>
  translate(props.item.summary_key, props.item.summary_params as Record<string, any>)
)
const running = computed(() => executionStepStatus(props.item) === 'running')
const modelCalls = computed(() => props.item.model_calls || [])
const hasDetail = computed(() => Object.keys(props.item.detail || {}).length > 0)
const hasRawIo = computed(
  () => props.item.input != null || props.item.output != null || !!props.item.reasoning_content
)

const ROLE_LABELS: Record<string, string> = {
  system: 'system',
  human: 'user',
  user: 'user',
  ai: 'assistant',
  assistant: 'assistant',
  aimessage: 'assistant',
}

function isRecord(value: unknown): value is Record<string, any> {
  return !!value && typeof value === 'object' && !Array.isArray(value)
}

function messageRole(item: Record<string, any>): string {
  const raw = String(item.role || item.type || 'message').toLowerCase()
  return ROLE_LABELS[raw] || raw
}

function messageText(item: Record<string, any>): string {
  const content = item.content
  if (typeof content === 'string') return content
  if (Array.isArray(content)) {
    return content
      .map((part) => {
        if (typeof part === 'string') return part
        if (isRecord(part) && typeof part.text === 'string') return part.text
        return JSON.stringify(part)
      })
      .join('')
  }
  if (content == null) return ''
  try {
    return JSON.stringify(content, null, 2)
  } catch {
    return String(content)
  }
}

function isMessage(value: unknown): value is Record<string, any> {
  return isRecord(value) && ('content' in value || 'role' in value || 'type' in value)
}

function formatMessages(messages: Record<string, any>[]): string {
  return messages.map((item) => `--- ${messageRole(item)} ---\n${messageText(item)}`).join('\n\n')
}

const displayValue = (value: any) => {
  if (value == null) return ''
  if (typeof value === 'string') return value
  if (Array.isArray(value) && value.every(isMessage)) return formatMessages(value)
  if (isMessage(value)) return formatMessages([value])
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

const callTokens = (call: Record<string, any>) =>
  Number(call.usage?.total_tokens || call.usage?.total_token_count || 0)
const callDuration = (call: Record<string, any>) =>
  call.elapsed_ms ? `${(Number(call.elapsed_ms) / 1000).toFixed(2)}s` : '—'
const callStatusType = (call: Record<string, any>) =>
  call.status === 'success' ? 'success' : call.status === 'invalid' ? 'danger' : 'info'
const callStatusText = (call: Record<string, any>) => {
  const key = `chat.audit.model_call_${call.status || 'completed'}`
  return te(key) ? t(key) : String(call.status || '')
}

const compactError = (value: unknown) => {
  const text = String(value || '').trim()
  if (!text) return ''
  const firstLine = text.split('\n', 1)[0]
  return firstLine.length > 300 ? `${firstLine.slice(0, 300)}…` : firstLine
}

const processDetail = computed(() => {
  const detail = { ...(props.item.detail || {}) }
  if (Array.isArray(detail.attempts)) {
    detail.attempts = detail.attempts.map((attempt: Record<string, any>, index: number) => ({
      attempt: attempt.attempt || index + 1,
      decision: attempt.decision,
      error: compactError(attempt.error),
    }))
  }
  if (detail.error) detail.error = compactError(detail.error)
  return detail
})
</script>

<template>
  <div class="execution-step-content">
    <div v-if="running" class="processing">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>{{ summary || t('chat.audit.processing') }}</span>
    </div>
    <div v-if="!running && summary" class="business-summary">{{ summary }}</div>
    <div v-if="modelCalls.length" class="model-calls">
      <section
        v-for="(call, callIndex) in modelCalls"
        :key="`${call.purpose || 'model'}-${call.attempt}-${callIndex}`"
        class="model-call"
      >
        <div class="model-call-header">
          <strong>
            {{ call.purpose || t('chat.audit.model_call', { value: call.attempt }) }}
          </strong>
          <span v-if="call.model_name">{{ call.model_name }}</span>
          <el-tag size="small" :type="callStatusType(call)">{{ callStatusText(call) }}</el-tag>
          <span>{{ callTokens(call) || '—' }} tokens</span>
          <span>{{ callDuration(call) }}</span>
        </div>
        <div class="call-body">
          <section v-if="call.input != null" class="io-block">
            <h5>{{ t('chat.audit.raw_input') }}</h5>
            <pre class="raw-value">{{ displayValue(call.input) }}</pre>
          </section>
          <section v-if="call.output != null" class="io-block">
            <h5>{{ t('chat.audit.raw_output') }}</h5>
            <pre class="raw-value sql-output">{{ displayValue(call.output) }}</pre>
          </section>
          <section v-if="call.reasoning" class="io-block">
            <h5>{{ t('chat.audit.reasoning') }}</h5>
            <pre class="raw-value">{{ call.reasoning }}</pre>
          </section>
          <section v-if="call.error" class="io-block">
            <h5>{{ t('chat.audit.call_error') }}</h5>
            <pre class="raw-value error-value">{{ call.error }}</pre>
          </section>
        </div>
      </section>
      <div v-if="hasDetail" class="process-detail">
        <div class="detail-title">{{ t('chat.audit.process_detail') }}</div>
        <pre class="raw-value">{{ displayValue(processDetail) }}</pre>
      </div>
    </div>
    <div v-else-if="hasRawIo || hasDetail" class="call-body direct-tabs">
      <section v-if="item.input != null" class="io-block">
        <h5>{{ t('chat.audit.raw_input') }}</h5>
        <pre class="raw-value">{{ displayValue(item.input) }}</pre>
      </section>
      <section v-if="item.output != null" class="io-block">
        <h5>{{ t('chat.audit.raw_output') }}</h5>
        <pre class="raw-value sql-output">{{ displayValue(item.output) }}</pre>
      </section>
      <section v-if="item.reasoning_content" class="io-block">
        <h5>{{ t('chat.audit.reasoning') }}</h5>
        <pre class="raw-value">{{ item.reasoning_content }}</pre>
      </section>
      <section v-if="hasDetail" class="io-block">
        <h5>{{ t('chat.audit.process_detail') }}</h5>
        <pre class="raw-value">{{ displayValue(item.detail) }}</pre>
      </section>
    </div>
    <details v-else-if="!running && item.message" class="legacy-detail">
      <summary>{{ t('chat.audit.raw_record') }}</summary>
      <pre class="raw-value">{{ displayValue(item.message) }}</pre>
    </details>
  </div>
</template>

<style scoped lang="less">
.execution-step-content {
  padding: 10px 16px 4px;
  color: #646a73;
  font-size: 13px;
  line-height: 20px;
}
.processing {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 36px;
}
.business-summary {
  padding: 8px 10px;
  margin-bottom: 6px;
  border-radius: 6px;
  background: #f5f6f7;
  color: #1f2329;
}
.raw-tabs :deep(.ed-tabs__header) {
  margin-bottom: 8px;
}
.direct-tabs {
  margin-top: 2px;
}
.io-block + .io-block {
  margin-top: 10px;
}
.io-block h5 {
  margin: 0 0 6px;
  color: #1f2329;
  font-size: 13px;
  font-weight: 500;
}
.model-call {
  margin: 8px 0 12px;
  padding: 10px 12px 12px;
  border: 1px solid #dee0e3;
  border-radius: 8px;
  background: #fff;
}
.model-call-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  color: #646a73;
}
.model-call-header strong {
  margin-right: auto;
  color: #1f2329;
}
.process-detail {
  margin: 8px 0;
}
.detail-title {
  margin-bottom: 6px;
  color: #1f2329;
  font-weight: 500;
}
.raw-value {
  max-height: 260px;
  margin: 0;
  padding: 10px 12px;
  overflow: auto;
  border: 1px solid #dee0e3;
  border-radius: 6px;
  background: #f7f8fa;
  color: #1f2329;
  font:
    12px/1.55 ui-monospace,
    SFMono-Regular,
    Menlo,
    Monaco,
    Consolas,
    monospace;
  white-space: pre-wrap;
  word-break: break-word;
}
.sql-output {
  white-space: pre;
}
.error-value {
  color: #d54941;
}
.legacy-detail summary {
  cursor: pointer;
  padding: 6px 0;
}
</style>
