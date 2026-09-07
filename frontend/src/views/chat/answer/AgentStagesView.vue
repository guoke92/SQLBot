<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import SQLComponent from '@/views/chat/component/SQLComponent.vue'
import ExecutionDetails from '@/views/chat/ExecutionDetails.vue'
import icon_up_outlined from '@/assets/svg/icon_up_outlined.svg'
import icon_down_outlined from '@/assets/svg/icon_down_outlined.svg'
import icon_logs_outlined from '@/assets/svg/icon_logs_outlined.svg'
import { useChatConfigStore } from '@/stores/chatConfig.ts'
import {
  narrativeDurationMs,
  projectNarrative,
  type NarrativeBlock,
  type ProcessItem,
} from '@/features/conversation/processTimeline'

const { t } = useI18n()
const chatConfig = useChatConfigStore()

const props = withDefaults(
  defineProps<{
    items: ProcessItem[]
    isTyping?: boolean
    recordId?: number
    duration?: number | null
    totalTokens?: number | null
  }>(),
  {
    items: () => [],
    isTyping: false,
    recordId: undefined,
    duration: null,
    totalTokens: null,
  }
)

const processOpen = ref(true)
const userExpanded = ref<Record<string, boolean>>({})
const thoughtInlineRefs = ref<Record<string, HTMLElement | null>>({})
const executionDetailsRef = ref<InstanceType<typeof ExecutionDetails>>()

const blocks = computed(() => projectNarrative(props.items))
const computedSeconds = computed(() => {
  if (props.duration != null && props.duration > 0) {
    return Number(Number(props.duration).toFixed(2))
  }
  const ms = narrativeDurationMs(blocks.value)
  return ms > 0 ? Number((ms / 1000).toFixed(2)) : null
})
const hasRunning = computed(() =>
  blocks.value.some((block) => {
    if (block.item.status === 'running') return true
    if (block.type === 'tool') {
      return block.artifacts.some((item) => item.status === 'running')
    }
    return false
  })
)
const isLive = computed(() => Boolean(props.isTyping || hasRunning.value))
const isTerminal = computed(() => !isLive.value)
const showLogBtn = computed(() => chatConfig.getShowLog)

watch(
  isLive,
  (live) => {
    // Keep the process narrative visible while live and after completion so
    // thought content remains reachable; users can still collapse via summary.
    if (live) {
      processOpen.value = true
    }
  },
  { immediate: true }
)

watch(
  () =>
    blocks.value
      .filter((block) => block.type === 'thought' && block.item.status === 'running')
      .map((block) => block.key)
      .join('|'),
  (keys) => {
    if (!keys || !isLive.value) return
    for (const key of keys.split('|')) {
      if (!key) continue
      if (userExpanded.value[key] === undefined) {
        userExpanded.value = { ...userExpanded.value, [key]: true }
      }
    }
  },
  { immediate: true }
)

function setThoughtInlineRef(key: string, el: unknown) {
  thoughtInlineRefs.value[key] = (el as HTMLElement | null) || null
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

/** Multiline expand is opt-in; live thoughts default to a single scrolling line. */
function isExpanded(block: NarrativeBlock): boolean {
  return userExpanded.value[block.key] === true
}

function isActiveThought(block: NarrativeBlock): boolean {
  const thoughts = blocks.value.filter((item) => item.type === 'thought')
  return thoughts.length > 0 && thoughts[thoughts.length - 1].key === block.key
}

function blockTitle(block: NarrativeBlock): string {
  if (block.type === 'thought') {
    if (block.item.status === 'running' || (isLive.value && isActiveThought(block))) {
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

function toolSql(block: Extract<NarrativeBlock, { type: 'tool' }>): string {
  const fromArtifact = block.artifacts.find((item) => item.artifact?.sql)?.artifact?.sql
  if (fromArtifact) return fromArtifact
  const args = block.item.tool?.args
  if (args && typeof args.sql === 'string') return args.sql
  return ''
}

function previewRows(block: Extract<NarrativeBlock, { type: 'tool' }>) {
  return block.artifacts.find((item) => item.artifact?.preview_rows?.length)?.artifact
    ?.preview_rows
}

function statusClass(block: NarrativeBlock): string {
  if (block.type === 'clarification' && block.item.status === 'running') return 'is-waiting'
  if (block.item.status === 'failed') return 'is-failed'
  if (block.item.status === 'interrupted') return 'is-failed'
  if (block.item.status === 'running') return 'is-running'
  return 'is-done'
}

function showInlineThought(block: NarrativeBlock): boolean {
  return block.type === 'thought' && !isExpanded(block) && Boolean(thoughtPlain(block.item))
}

watch(
  () =>
    blocks.value
      .filter((block) => block.type === 'thought')
      .map((block) => `${block.key}:${thoughtPlain(block.item).length}:${isExpanded(block)}`)
      .join('|'),
  async () => {
    await nextTick()
    for (const block of blocks.value) {
      if (block.type !== 'thought' || isExpanded(block)) continue
      const el = thoughtInlineRefs.value[block.key]
      if (!el) continue
      const stick =
        block.item.status === 'running' || (isLive.value && isActiveThought(block))
      if (stick) {
        el.scrollLeft = el.scrollWidth
      }
    }
  }
)

const summaryLabel = computed(() => {
  const seconds = computedSeconds.value
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
  <div v-if="blocks.length" class="agent-process">
    <div v-if="isTerminal" class="process-summary" @click="toggleProcess">
      <span class="summary-label">{{ summaryLabel }}</span>
      <span class="summary-actions">
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
              'is-live':
                block.item.status === 'running' || (isLive && isActiveThought(block)),
            }"
          >
            {{ thoughtPlain(block.item) }}
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
            <div class="thought-stream">
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
</style>
