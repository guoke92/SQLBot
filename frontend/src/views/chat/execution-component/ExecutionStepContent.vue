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
  return messages
    .map((item) => `--- ${messageRole(item)} ---\n${messageText(item)}`)
    .join('\n\n')
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
</script>

<template>
  <div class="execution-step-content">
    <div v-if="running" class="processing">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>{{ summary || t('chat.audit.processing') }}</span>
    </div>
    <div v-if="!running && summary" class="business-summary">{{ summary }}</div>
    <el-collapse v-if="hasRawIo" class="raw-collapse">
      <el-collapse-item :title="t('chat.audit.technical_detail')" name="raw-io">
        <el-tabs class="raw-tabs">
          <el-tab-pane v-if="item.input != null" :label="t('chat.audit.raw_input')">
            <pre class="raw-value">{{ displayValue(item.input) }}</pre>
          </el-tab-pane>
          <el-tab-pane v-if="item.output != null" :label="t('chat.audit.raw_output')">
            <pre class="raw-value">{{ displayValue(item.output) }}</pre>
          </el-tab-pane>
          <el-tab-pane v-if="item.reasoning_content" :label="t('chat.audit.reasoning')">
            <pre class="raw-value">{{ item.reasoning_content }}</pre>
          </el-tab-pane>
        </el-tabs>
      </el-collapse-item>
    </el-collapse>
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
.raw-collapse :deep(.ed-collapse-item__header) {
  height: 36px;
  font-size: 13px;
}
.raw-collapse :deep(.ed-collapse-item__content) {
  padding-bottom: 8px;
}
.raw-tabs :deep(.ed-tabs__header) {
  margin-bottom: 8px;
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
.legacy-detail summary {
  cursor: pointer;
  padding: 6px 0;
}
</style>
