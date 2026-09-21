<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import SQLComponent from '@/views/chat/component/SQLComponent.vue'
import ClarificationCard from '@/features/conversation/ClarificationCard.vue'
import ExecutionDetails from '@/views/chat/ExecutionDetails.vue'
import icon_up_outlined from '@/assets/svg/icon_up_outlined.svg'
import icon_down_outlined from '@/assets/svg/icon_down_outlined.svg'
import icon_logs_outlined from '@/assets/svg/icon_logs_outlined.svg'
import { useChatConfigStore } from '@/stores/chatConfig.ts'
import type { ConversationInterrupt, ResumeAnswer } from '@/api/chat'
import {
  processingDurationMs,
  projectNarrative,
  thoughtSnippet,
  type NarrativeBlock,
  type ProcessItem,
} from '@/features/conversation/processTimeline'

const { t } = useI18n()
const chatConfig = useChatConfigStore()

const props = withDefaults(
  defineProps<{
    items: ProcessItem[]
    interrupts?: ConversationInterrupt[]
    isTyping?: boolean
    loading?: boolean
    awaitingInput?: boolean
    recordId?: number
    duration?: number | null
    totalTokens?: number | null
    deliveredDatasetIds?: string[]
  }>(),
  {
    items: () => [],
    interrupts: () => [],
    isTyping: false,
    loading: false,
    awaitingInput: false,
    recordId: undefined,
    duration: null,
    totalTokens: null,
    deliveredDatasetIds: () => [],
  }
)

const emit = defineEmits<{
  submitClarification: [
    payload: {
      interrupt: ConversationInterrupt
      answers: ResumeAnswer[]
      displayText: string
    },
  ]
  correctClarification: [
    payload: {
      interrupt: ConversationInterrupt
      answer: ResumeAnswer
      supersedesEvidenceId: string
    },
  ]
}>()

const STICK_NEAR_PX = 24

const processOpen = ref(false)
const userExpanded = ref<Record<string, boolean>>({})
const stickCancelled = ref<Record<string, boolean>>({})
const thoughtInlineRefs = ref<Record<string, HTMLElement | null>>({})
const thoughtBodyRefs = ref<Record<string, HTMLElement | null>>({})
const executionDetailsRef = ref<InstanceType<typeof ExecutionDetails>>()
const nowMs = ref(Date.now())
const programmaticStick = new Set<string>()
let liveTickTimer: ReturnType<typeof setInterval> | undefined

const blocks = computed(() => projectNarrative(props.items))
const hasRunning = computed(() =>
  blocks.value.some((block) => {
    if (block.item.status === 'running') return true
    if (block.type === 'tool') {
      return block.artifacts.some((item) => item.status === 'running')
    }
    return false
  })
)
const isLive = computed(() => Boolean(props.isTyping || props.loading || hasRunning.value))
const isTerminal = computed(() => !isLive.value)
const showLogBtn = computed(() => chatConfig.getShowLog)
const liveStartedAt = ref<number | null>(null)
const computedSeconds = computed(() => {
  if (isTerminal.value && props.duration != null && props.duration > 0) {
    return Number(Number(props.duration).toFixed(2))
  }
  void nowMs.value
  const fromBlocks = processingDurationMs(blocks.value, nowMs.value)
  if (fromBlocks > 0) {
    return Number((fromBlocks / 1000).toFixed(isLive.value ? 1 : 2))
  }
  if (isLive.value && liveStartedAt.value != null) {
    const fromSend = nowMs.value - liveStartedAt.value
    if (fromSend <= 0) return 0
    return Number((fromSend / 1000).toFixed(1))
  }
  return isLive.value ? 0 : null
})

const currentAction = computed(() => {
  if (props.awaitingInput) return t('chat.summary.clarification_waiting')
  const running = blocks.value.find((block) => {
    if (block.item.status === 'running') return true
    return block.type === 'tool' && block.artifacts.some((item) => item.status === 'running')
  })
  if (!running) return t('chat.timeline.thinking')
  if (running.type === 'thought') return t('chat.timeline.thinking')
  return running.item.title || t('chat.timeline.tool.generic')
})

watch(
  isLive,
  (live) => {
    if (liveTickTimer !== undefined) {
      clearInterval(liveTickTimer)
      liveTickTimer = undefined
    }
    if (live) {
      processOpen.value = true
      if (liveStartedAt.value == null) liveStartedAt.value = Date.now()
      nowMs.value = Date.now()
      liveTickTimer = setInterval(() => {
        nowMs.value = Date.now()
      }, 250)
    } else {
      processOpen.value = false
      liveStartedAt.value = null
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  if (liveTickTimer !== undefined) {
    clearInterval(liveTickTimer)
  }
})

function setThoughtInlineRef(key: string, el: unknown) {
  thoughtInlineRefs.value[key] = (el as HTMLElement | null) || null
}

function setThoughtBodyRef(key: string, el: unknown) {
  thoughtBodyRefs.value[key] = (el as HTMLElement | null) || null
}

function regionKey(blockKey: string, region: 'body' | 'inline') {
  return `${blockKey}:${region}`
}

function markProgrammatic(key: string) {
  programmaticStick.add(key)
  window.setTimeout(() => {
    programmaticStick.delete(key)
  }, 80)
}

function isStreamingThought(block: NarrativeBlock): boolean {
  return block.type === 'thought' && block.item.status === 'running'
}

function parseThoughtWatch(snapshot: string | undefined): Map<string, { expanded: boolean; status: string }> {
  const out = new Map<string, { expanded: boolean; status: string }>()
  if (!snapshot) return out
  for (const part of snapshot.split('|')) {
    if (!part) continue
    const [key, , expanded, status] = part.split(':')
    if (!key) continue
    out.set(key, { expanded: expanded === 'true', status: status || '' })
  }
  return out
}

function toggleProcess() {
  if (!isTerminal.value) return
  processOpen.value = !processOpen.value
}

function openExecutionDetails(event: Event) {
  event.stopPropagation()
  if (!props.recordId || !executionDetailsRef.value) return
  executionDetailsRef.value.getLogList(props.recordId)
}

function toggleBlock(key: string, fallback: boolean) {
  const current = userExpanded.value[key]
  userExpanded.value[key] = !(current === undefined ? fallback : current)
}

/** Clarification and the in-flight step stay open; everything else is one line. */
function isExpanded(block: NarrativeBlock): boolean {
  const override = userExpanded.value[block.key]
  if (override !== undefined) return override
  if (block.type === 'clarification') return true
  if (block.item.status === 'running') return true
  return (
    block.type === 'tool' && block.artifacts.some((item) => item.status === 'running')
  )
}

function blockTitle(block: NarrativeBlock): string {
  if (block.type === 'thought') {
    if (isStreamingThought(block)) {
      return t('chat.timeline.thinking')
    }
    const seconds =
      block.item.duration_ms != null ? (block.item.duration_ms / 1000).toFixed(1) : null
    return seconds
      ? t('chat.timeline.thought_for', { seconds })
      : block.item.title || t('chat.timeline.thought')
  }
  if (block.type === 'clarification') {
    return block.item.title || t('chat.timeline.clarification')
  }
  return block.item.title || block.item.title_key || t('chat.timeline.tool.generic')
}

function blockSummary(block: NarrativeBlock): string {
  if (block.type === 'tool') {
    const artifact = block.artifacts[0]
    if (artifact?.summary) return artifact.summary
    if (artifact?.artifact?.row_count != null) {
      return t('chat.summary.query_rows', { count: artifact.artifact.row_count })
    }
  }
  return block.item.summary || ''
}

function thoughtContent(item: ProcessItem): string {
  return item.thought?.content || ''
}

function thoughtPlain(item: ProcessItem): string {
  return thoughtContent(item).replace(/\s+/g, ' ').trim()
}

function thoughtLine(item: ProcessItem): string {
  return thoughtSnippet(thoughtContent(item))
}

function toolSql(block: Extract<NarrativeBlock, { type: 'tool' }>): string {
  // Prefer tool args (model-authored, usually multi-line) when artifact SQL was
  // flattened by execution rewrite; otherwise use the artifact display SQL.
  const args = block.item.tool?.args
  const fromArgs = args && typeof args.sql === 'string' ? args.sql : ''
  const fromArtifact = block.artifacts.find((item) => item.artifact?.sql)?.artifact?.sql || ''
  if (fromArgs.includes('\n') && !String(fromArtifact).includes('\n')) {
    return fromArgs
  }
  return fromArtifact || fromArgs
}

function previewRows(block: Extract<NarrativeBlock, { type: 'tool' }>) {
  const delivered = new Set((props.deliveredDatasetIds || []).map(String))
  const artifact = block.artifacts.find((item) => item.artifact?.preview_rows?.length)
  const datasetId = artifact?.artifact?.dataset_id
  if (datasetId && delivered.has(String(datasetId))) return undefined
  return artifact?.artifact?.preview_rows
}

function statusClass(block: NarrativeBlock): string {
  if (block.type === 'clarification' && block.item.status === 'running') return 'is-waiting'
  if (block.item.status === 'failed') return 'is-failed'
  if (block.item.status === 'interrupted') return 'is-failed'
  if (block.item.status === 'running') return 'is-running'
  return 'is-done'
}

function showInlineThought(block: NarrativeBlock): boolean {
  return block.type === 'thought' && !isExpanded(block) && Boolean(thoughtLine(block.item))
}

function interruptForBlock(block: NarrativeBlock): ConversationInterrupt | undefined {
  if (block.type !== 'clarification') return undefined
  const interruptId = block.item.meta?.interrupt_id
  if (typeof interruptId === 'string' && interruptId) {
    return props.interrupts.find((item) => item.interrupt_id === interruptId)
  }
  // Legacy rows without meta: only auto-bind when exactly one interrupt exists.
  if (props.interrupts.length === 1) return props.interrupts[0]
  return undefined
}

function syntheticInterrupt(block: NarrativeBlock): ConversationInterrupt | undefined {
  if (block.type !== 'clarification') return undefined
  const card = block.item.meta?.clarification_card
  if (!card || typeof card !== 'object') return undefined
  const interruptId =
    typeof block.item.meta?.interrupt_id === 'string'
      ? block.item.meta.interrupt_id
      : `timeline-${block.key}`
  const version =
    typeof block.item.meta?.version === 'number' ? block.item.meta.version : 1
  return {
    interrupt_id: interruptId,
    version,
    status: block.item.status === 'running' ? 'open' : 'consumed',
    payload: card as ConversationInterrupt['payload'],
  }
}

function resolveInterrupt(block: NarrativeBlock): ConversationInterrupt | undefined {
  return interruptForBlock(block) || syntheticInterrupt(block)
}

function onRegionScroll(blockKey: string, region: 'body' | 'inline', event: Event) {
  const key = regionKey(blockKey, region)
  if (programmaticStick.has(key)) return
  const el = event.target as HTMLElement | null
  if (!el) return
  const distance =
    region === 'body'
      ? el.scrollHeight - el.scrollTop - el.clientHeight
      : el.scrollWidth - el.scrollLeft - el.clientWidth
  stickCancelled.value = {
    ...stickCancelled.value,
    [key]: distance > STICK_NEAR_PX,
  }
}

function syncThoughtRegions(prevSnapshot?: string) {
  const prev = parseThoughtWatch(prevSnapshot)
  for (const block of blocks.value) {
    if (block.type !== 'thought') continue
    const streaming = isStreamingThought(block)
    const expanded = isExpanded(block)
    const prevState = prev.get(block.key)
    const justCompleted = prevState?.status === 'running' && !streaming
    const justOpened = Boolean(prevState && !prevState.expanded && expanded)
    if (expanded) {
      const el = thoughtBodyRefs.value[block.key]
      if (!el) continue
      const key = regionKey(block.key, 'body')
      if (streaming && !stickCancelled.value[key]) {
        markProgrammatic(key)
        el.scrollTop = el.scrollHeight
        requestAnimationFrame(() => {
          if (stickCancelled.value[key]) return
          markProgrammatic(key)
          el.scrollTop = el.scrollHeight
        })
      } else if (justCompleted || (justOpened && !streaming)) {
        markProgrammatic(key)
        el.scrollTop = 0
      }
      continue
    }
    const el = thoughtInlineRefs.value[block.key]
    if (!el) continue
    const key = regionKey(block.key, 'inline')
    if (streaming && !stickCancelled.value[key]) {
      markProgrammatic(key)
      el.scrollLeft = el.scrollWidth
    } else if (justCompleted) {
      markProgrammatic(key)
      el.scrollLeft = 0
    }
  }
}

watch(
  () =>
    blocks.value
      .filter((block) => block.type === 'thought')
      .map(
        (block) =>
          `${block.key}:${thoughtPlain(block.item).length}:${isExpanded(block)}:${block.item.status}`
      )
      .join('|'),
  async (_curr, prev) => {
    await nextTick()
    syncThoughtRegions(prev)
  },
  { flush: 'post', immediate: true }
)

const summaryLabel = computed(() => {
  const seconds = computedSeconds.value
  if (isLive.value) {
    if (seconds != null) {
      return t('chat.timeline.working_as', { action: currentAction.value, seconds })
    }
    return currentAction.value
  }
  const tokens = props.totalTokens
  if (seconds != null && tokens != null) {
    return t('chat.timeline.worked_for_with_tokens', { seconds, tokens })
  }
  if (seconds != null) {
    return t('chat.timeline.worked_for', { seconds })
  }
  if (tokens != null) {
    return t('chat.timeline.tokens_only', { tokens })
  }
  return t('chat.timeline.process')
})
</script>

<template>
  <div v-if="blocks.length || isLive" class="agent-process">
    <div
      class="process-summary"
      :class="{ 'is-live': isLive }"
      @click="toggleProcess"
    >
      <span class="summary-label">{{ summaryLabel }}</span>
      <span v-if="isTerminal" class="summary-actions">
        <button
          v-if="showLogBtn && recordId"
          type="button"
          class="details-btn"
          :title="t('parameter.execution_details')"
          @click="openExecutionDetails"
        >
          <el-icon size="14">
            <icon_logs_outlined />
          </el-icon>
        </button>
        <el-icon class="toggle-icon">
          <icon_up_outlined v-if="processOpen" />
          <icon_down_outlined v-else />
        </el-icon>
      </span>
    </div>

    <div v-show="isLive || processOpen" class="process-blocks">
      <div
        v-for="block in blocks"
        :key="block.key"
        class="process-block"
        :class="[statusClass(block), `kind-${block.type}`]"
      >
        <button
          type="button"
          class="block-header"
          @click="toggleBlock(block.key, isExpanded(block))"
        >
          <span class="block-title">{{ blockTitle(block) }}</span>
          <span
            v-if="showInlineThought(block)"
            :ref="(el) => setThoughtInlineRef(block.key, el)"
            class="thought-inline"
            :class="{
              'is-live': isStreamingThought(block),
            }"
            @scroll.stop="onRegionScroll(block.key, 'inline', $event)"
          >
            {{ thoughtLine(block.item) }}
          </span>
          <span
            v-else-if="blockSummary(block) && !isExpanded(block)"
            class="block-summary"
          >
            {{ blockSummary(block) }}
          </span>
          <el-icon class="toggle-icon">
            <icon_up_outlined v-if="isExpanded(block)" />
            <icon_down_outlined v-else />
          </el-icon>
        </button>

        <div v-show="isExpanded(block)" class="block-body">
          <template v-if="block.type === 'thought'">
            <div
              :ref="(el) => setThoughtBodyRef(block.key, el)"
              class="thought-stream"
              @scroll="onRegionScroll(block.key, 'body', $event)"
            >
              <MdComponent v-if="thoughtContent(block.item)" :message="thoughtContent(block.item)" />
            </div>
          </template>

          <template v-else-if="block.type === 'tool'">
            <div v-if="toolSql(block)" class="tool-sql">
              <SQLComponent :sql="toolSql(block)" />
            </div>
            <div
              v-else-if="block.item.tool?.args && Object.keys(block.item.tool.args).length"
              class="tool-args"
            >
              <pre>{{ JSON.stringify(block.item.tool.args, null, 2) }}</pre>
            </div>
            <div v-if="previewRows(block)?.length" class="tool-preview">
              <pre>{{ JSON.stringify(previewRows(block), null, 2) }}</pre>
            </div>
            <div v-if="blockSummary(block)" class="tool-result">{{ blockSummary(block) }}</div>
          </template>

          <template v-else-if="block.type === 'clarification'">
            <ClarificationCard
              v-if="resolveInterrupt(block)"
              :interrupt="resolveInterrupt(block)!"
              :disabled="loading"
              :correctable="
                awaitingInput && resolveInterrupt(block)?.status === 'consumed'
              "
              @submit="emit('submitClarification', $event)"
              @correct="emit('correctClarification', $event)"
            />
            <div v-else class="clarify-status">
              {{ blockSummary(block) || blockTitle(block) }}
            </div>
          </template>

          <template v-else>
            <div class="clarify-status">{{ blockSummary(block) || blockTitle(block) }}</div>
          </template>
        </div>
      </div>
    </div>

    <ExecutionDetails ref="executionDetailsRef" />
  </div>
</template>

<style scoped lang="less">
.agent-process {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 10px;
}

.process-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 2px;
  border: 0;
  background: transparent;
  cursor: pointer;
  color: #86909c;
  font-size: 12px;
  line-height: 18px;
  user-select: none;

  &:hover {
    color: #4e5969;
  }

  &.is-live {
    cursor: default;

    &:hover {
      color: #86909c;
    }
  }
}

.summary-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  min-width: 0;
}

.summary-actions {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.details-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  padding: 0;
  border: 0;
  border-radius: 4px;
  background: transparent;
  color: #86909c;
  cursor: pointer;

  &:hover {
    background: rgba(31, 35, 41, 0.06);
    color: #4e5969;
  }
}

.process-blocks {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-left: 2px;
}

.process-block {
  border: 0;
  background: transparent;
}

.block-header {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  max-width: 100%;
  padding: 4px 2px;
  border: 0;
  background: transparent;
  cursor: pointer;
  color: #86909c;
  font-size: 12px;
  line-height: 18px;
  text-align: left;

  &:hover {
    color: #4e5969;
  }
}

.block-title {
  flex-shrink: 0;
  font-weight: 500;
  color: inherit;
}

.block-summary {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #a9aeb8;
}

.thought-inline {
  flex: 1 1 auto;
  min-width: 0;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
  color: #86909c;
  font-size: 12px;
  line-height: 18px;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }

  &.is-live {
    color: #86909c;
  }
}

.toggle-icon {
  flex-shrink: 0;
  font-size: 12px;
  color: #c0c4cc;
}

.block-body {
  padding: 2px 2px 8px 12px;
  color: #86909c;
  font-size: 12px;
  line-height: 18px;
}

.thought-stream {
  max-height: 280px;
  overflow: auto;
  padding-right: 4px;
  padding-left: 10px;
  border-left: 2px solid #e5e6eb;
  color: #86909c;
  font-size: 12px;
  line-height: 18px;

  :deep(.markdown-body),
  :deep(.md-render-container) {
    font-size: 12px !important;
    line-height: 18px !important;
    color: #86909c !important;
    background: transparent !important;
  }

  :deep(.markdown-body *) {
    font-size: inherit !important;
    line-height: inherit !important;
    color: inherit !important;
  }

  :deep(p),
  :deep(li),
  :deep(ul),
  :deep(ol) {
    margin: 0 0 4px;
  }

  :deep(ul),
  :deep(ol) {
    padding-left: 1.2em;
  }
}

.tool-sql,
.tool-args,
.tool-preview {
  margin-top: 4px;
}

.tool-args pre,
.tool-preview pre {
  margin: 0;
  padding: 8px;
  border-radius: 6px;
  background: #f7f8fa;
  color: #646a73;
  font-size: 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  max-height: 160px;
  overflow: auto;
}

.tool-result,
.clarify-status {
  margin-top: 4px;
  color: #86909c;
  font-size: 12px;
}

.process-block.is-waiting .block-title {
  color: #ff7d00;
}

.process-block.is-failed .block-title {
  color: #f53f3f;
}

.process-block.is-running .block-title {
  color: #3370ff;
}

.kind-clarification :deep(.clarification-card) {
  margin-top: 4px;
}
</style>
