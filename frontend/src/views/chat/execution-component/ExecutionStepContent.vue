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

// LLM 出参 content 是 JSON 字符串但缩进不稳定（紧凑/缩进取决于模型输出），
// 统一尝试 parse 后 pretty-print；非 JSON 文本原样返回（chat 172 问题 3）
function prettyJsonText(text: string): string {
  const trimmed = text.trim()
  if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) return text
  try {
    return JSON.stringify(JSON.parse(trimmed), null, 2)
  } catch {
    return text
  }
}

function messageText(item: Record<string, any>): string {
  const content = item.content
  if (typeof content === 'string') {
    return String(item.type || item.role || '').toLowerCase() === 'ai' ||
      String(item.role || '').toLowerCase() === 'assistant'
      ? prettyJsonText(content)
      : content
  }
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

// ── 检索上下文卡片化（chat 169：平铺卡片还原真实返回，不做折叠/摘要）────
const wikiRecall = computed(() => (props.item.detail as any)?.wiki)
// schema 分节卡片（每表一卡，含来源标注）
const schemaSections = computed<Record<string, any>[]>(() => {
  const sections = (props.item.detail as any)?.schema_sections
  return Array.isArray(sections) ? sections : []
})
// 检索视图门控：wiki 命中块（第一次检索 span）或 schema 分节（topup 扩窗 span，
// chat 172 问题 2 —— 两种 CHOOSE_TABLE 卡片统一走美化渲染）
const hasRecallView = computed(
  () =>
    (isRecord(wikiRecall.value) && Array.isArray(wikiRecall.value.hits)) ||
    schemaSections.value.length > 0
)
const recallHits = computed(() =>
  isRecord(wikiRecall.value) && Array.isArray(wikiRecall.value.hits)
    ? (wikiRecall.value.hits as Record<string, any>[])
    : []
)
// 命中页完整渲染文本（page_key → text）；卡片 body 直接显示原文
const recallPassages = computed<Record<string, string>>(() => {
  const passages = (wikiRecall.value as any)?.passages
  return isRecord(passages) ? (passages as Record<string, string>) : {}
})
const recallTraceLines = computed<string[]>(() => {
  const trace = (wikiRecall.value as any)?.trace
  if (!isRecord(trace)) return []
  const lines: string[] = []
  lines.push(t('chat.audit.trace_visible', { count: trace.visible_pages ?? 0 }))
  const channels = trace.channels as Record<string, any> | undefined
  if (channels) {
    for (const [name, ch] of Object.entries(channels)) {
      if (!isRecord(ch)) continue
      lines.push(
        `${name}: ${ch.chunks ?? 0} chunks` +
          (Array.isArray(ch.top) && ch.top.length
            ? ` · top: ${ch.top.map((x: any) => x.page_key).join(', ')}`
            : '')
      )
    }
  }
  if (Array.isArray(trace.window) && trace.window.length) {
    lines.push(
      t('chat.audit.trace_window', { count: trace.window.length }) +
        `: ${trace.window.map((x: any) => x.page_key).join(', ')}`
    )
  }
  if (Array.isArray(trace.graph_neighbors) && trace.graph_neighbors.length) {
    lines.push(
      `graph expansion (quota ${trace.graph_quota ?? 0}): ` +
        trace.graph_neighbors.map((x: any) => x.page_key).join(', ')
    )
  }
  return lines
})
const anchorAttribution = computed<Record<string, any>>(
  () => ((wikiRecall.value as any)?.anchor_attribution as Record<string, any>) || {}
)
// 原始完整 detail（原始值卡片，无截断）
const rawDetail = computed(() => props.item.detail)

const SOURCE_TAG_TYPES: Record<string, string> = {
  lexical: 'primary',
  vector: 'success',
  graph: 'warning',
}

const sourceTagType = (source: string) => SOURCE_TAG_TYPES[source] || 'info'
const originTagType = (origin: string) => (origin === 'closure' ? 'success' : 'info')
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
      <!-- 检索上下文：平铺卡片（schema 卡 / wiki 页卡 / 召回过程卡 / 原始值卡），
           不折叠不摘要，还原真实返回数据（chat 169 问题 3） -->
      <template v-if="hasRecallView">
        <section v-if="recallTraceLines.length" class="model-call recall-card">
          <div class="model-call-header">
            <strong>{{ t('chat.audit.recall_trace') }}</strong>
            <span>{{ wikiRecall.elapsed_ms }}ms</span>
            <el-tag v-if="wikiRecall.embedding_built" size="small" type="warning">
              embedding built
            </el-tag>
          </div>
          <pre class="raw-value">{{ recallTraceLines.join('\n') }}</pre>
          <pre v-if="Object.keys(anchorAttribution).length" class="raw-value">{{
            Object.entries(anchorAttribution)
              .map(
                ([table, refs]) =>
                  `${table} ← ${(refs as any[]).map((r) => `${r.page_key}(${r.field})`).join(', ')}`
              )
              .join('\n')
          }}</pre>
        </section>
        <section
          v-for="section in schemaSections"
          :key="`schema-${section.table}`"
          class="model-call recall-card"
        >
          <div class="model-call-header">
            <strong>{{ section.table }}</strong>
            <el-tag size="small" :type="originTagType(section.origin)">
              {{ section.origin }}
            </el-tag>
            <span>{{ section.chars }} chars</span>
          </div>
          <pre class="raw-value">{{ section.text }}</pre>
        </section>
        <section
          v-for="(hit, hitIndex) in recallHits"
          :key="`wiki-${hit.page_key}-${hitIndex}`"
          class="model-call recall-card"
          :class="{ 'recall-card-filtered': hit.filtered }"
        >
          <div class="model-call-header">
            <strong>{{ hit.title }}</strong>
            <code class="recall-key">{{ hit.page_key }}</code>
            <el-tag size="small" :type="sourceTagType(hit.source)">
              {{ hit.source }}
            </el-tag>
            <el-tag v-if="hit.filtered" size="small" type="info">
              {{ t('chat.audit.recall_filtered') }}
            </el-tag>
            <span
              class="recall-score"
              :title="`vector ${hit.vector_score ?? '—'} · lexical ${hit.lexical_score ?? '—'}`"
            >
              {{ Number(hit.score || 0).toFixed(3) }}
            </span>
          </div>
          <pre v-if="recallPassages[hit.page_key]" class="raw-value">{{
            recallPassages[hit.page_key]
          }}</pre>
        </section>
        <section class="model-call recall-card">
          <div class="model-call-header">
            <strong>{{ t('chat.audit.recall_tab_raw') }}</strong>
          </div>
          <pre class="raw-value">{{ displayValue(rawDetail) }}</pre>
        </section>
      </template>
      <template v-else>
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
          <pre class="raw-value">{{ displayValue(processDetail) }}</pre>
        </section>
      </template>
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
.recall-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.recall-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.recall-row {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: default;
}
.recall-row.filtered {
  opacity: 0.55;
}
.recall-passage {
  margin-left: 26px;
  max-height: 320px;
}
.recall-index {
  width: 18px;
  color: #646a73;
  text-align: right;
}
.recall-title {
  min-width: 120px;
  color: #1f2329;
}
.recall-key {
  padding: 0 6px;
  border-radius: 4px;
  background: #f5f6f7;
  color: #4e5059;
  font-size: 12px;
}
.recall-scores {
  margin-left: auto;
}
.recall-score {
  color: #8f959e;
  font-size: 12px;
}
.resource-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.resource-chip {
  font-family: monospace;
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
