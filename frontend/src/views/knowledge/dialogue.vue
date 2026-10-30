<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus-secondary'
import { chatApi, ChatRecord, type ConversationInterrupt, type ResumeAnswer } from '@/api/chat'
import type { ChatStreamEvent } from '@/hooks/useChatStream'
import {
  knowledgeApi,
  type WikiConversationGroup,
  type WikiDialogueGroup,
  type WikiDialogueItem,
  type WikiMaterialPreview,
  type WikiPageSummary,
  type WikiProposal,
} from '@/api/knowledge'
import { useConversationTurn } from '@/features/conversation/useConversationTurn'
import AgentStagesView from '@/views/chat/answer/AgentStagesView.vue'
import WikiReview from '@/views/knowledge/WikiReview.vue'
import RecordPreview from '@/views/knowledge/RecordPreview.vue'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import {
  applyDelta,
  belongsToRun,
  extractProcessItem,
  itemsForRun,
  removeItem,
  replaceItems,
  sortedItems,
  upsertItem,
  type ProcessItem,
  type TimelineMap,
} from '@/features/conversation/processTimeline'

type Chip =
  | { kind: 'page'; belong: string; page_key: string; title: string }
  | { kind: 'source'; source_id: number; title: string; locator: string }
  | { kind: 'record'; record_id: number; title: string }
  | { kind: 'paste'; title: string; body: string }

const { t } = useI18n()
const route = useRoute()
const turn = useConversationTurn()
const busy = computed(() => turn.running.value || turn.owned.value)

const corpusKey = ref('')
const laneGroups = ref<WikiDialogueGroup[]>([])
const collapsed = ref<Record<string, boolean>>({})
const chatId = ref<number | null>(null)
const records = ref<ChatRecord[]>([])
const liveRecord = ref<ChatRecord | null>(null)
const timelineMap = ref<TimelineMap>(new Map())
const proposals = ref<WikiProposal[]>([])
const draft = ref('')
const chips = ref<Chip[]>([])
const menu = ref<'' | 'page' | 'chat' | 'paste'>('')
const pages = ref<WikiPageSummary[]>([])
const pageQuery = ref('')
const groups = ref<WikiConversationGroup[]>([])
const pasteTitle = ref('')
const pasteBody = ref('')

type SideTab = {
  id: string
  title: string
  kind: 'preview' | 'change'
  preview: WikiMaterialPreview | null
  loading: boolean
  proposal: WikiProposal | null
}

const tabs = ref<SideTab[]>([])
const activeTab = ref('')
const sideWidth = ref(420)
const sideDragging = ref(false)
let stopSideResize: (() => void) | undefined

const dialogueColumns = computed(() =>
  tabs.value.length
    ? { gridTemplateColumns: `280px minmax(0, 1fr) 6px ${sideWidth.value}px` }
    : undefined
)
let pollTimer: ReturnType<typeof setInterval> | undefined
let focusEpoch = 0

const timelineItems = computed(() => sortedItems(timelineMap.value))
const filteredPages = computed(() => {
  const q = pageQuery.value.trim().toLowerCase()
  if (!q) return pages.value.slice(0, 40)
  return pages.value
    .filter((item) => `${item.title} ${item.page_key}`.toLowerCase().includes(q))
    .slice(0, 40)
})
const canSend = computed(
  () => !!corpusKey.value && chips.value.length > 0 && !!draft.value.trim() && !busy.value
)

function unwrap<T>(value: T | { data?: T }): T {
  if (value && typeof value === 'object' && 'data' in value && value.data) return value.data
  return value as T
}

function relativeTime(value: string) {
  if (!value) return ''
  const then = new Date(value).getTime()
  if (Number.isNaN(then)) return ''
  const minutes = Math.max(0, Math.round((Date.now() - then) / 60000))
  if (minutes < 1) return t('knowledge.wiki_just_now')
  if (minutes < 60) return t('knowledge.wiki_minutes_ago', { n: minutes })
  const hours = Math.round(minutes / 60)
  if (hours < 24) return t('knowledge.wiki_hours_ago', { n: hours })
  return t('knowledge.wiki_days_ago', { n: Math.round(hours / 24) })
}

function chipLabel(chip: Chip) {
  if (chip.kind === 'page') return chip.title || chip.page_key
  if (chip.kind === 'paste') return chip.title || t('knowledge.wiki_paste')
  return chip.title
}

function groupCollapsed(group: WikiDialogueGroup) {
  if (group.corpus_key in collapsed.value) return collapsed.value[group.corpus_key]
  return group.pending === 0 && group.processing === 0
}

function toggleGroup(corpus: string) {
  const group = laneGroups.value.find((item) => item.corpus_key === corpus)
  collapsed.value = {
    ...collapsed.value,
    [corpus]: group ? !groupCollapsed(group) : true,
  }
}

async function loadLane() {
  laneGroups.value = unwrap(await knowledgeApi.dialogueGroups()) || []
  if (!corpusKey.value) {
    const requested = String(route.query.corpus || '')
    corpusKey.value =
      laneGroups.value.find((item) => item.corpus_key === requested)?.corpus_key ||
      laneGroups.value[0]?.corpus_key ||
      ''
  }
}

async function loadPages() {
  if (!corpusKey.value) return
  const catalog = await knowledgeApi.listPages(corpusKey.value)
  pages.value = catalog?.pages || []
}

async function loadGroups() {
  if (!corpusKey.value) return
  groups.value = unwrap(await knowledgeApi.conversations(corpusKey.value)) || []
}

function ingest(record: ChatRecord, item: ProcessItem | undefined, mode: 'upsert' | 'delta') {
  if (!item || !belongsToRun(item, record.run_id)) return
  timelineMap.value =
    mode === 'delta' ? applyDelta(timelineMap.value, item) : upsertItem(timelineMap.value, item)
}

function turnHandlers(record: ChatRecord) {
  return {
    onEvent: (data: ChatStreamEvent) => {
      if (data.type === 'message') {
        record.sql_answer = `${record.sql_answer || ''}${data.content || ''}`
      }
      if (data.type === 'process_upsert') {
        ingest(record, extractProcessItem(data as Record<string, unknown>), 'upsert')
      }
      if (data.type === 'process_delta') {
        ingest(record, extractProcessItem(data as Record<string, unknown>), 'delta')
      }
      if (data.type === 'process_remove') {
        const removeId = (data as Record<string, unknown>).id
        if (removeId != null)
          timelineMap.value = removeItem(timelineMap.value, removeId as number | string)
      }
    },
    onFinish: async () => {
      await hydrate(record)
      await refreshProposals()
      await loadLane()
    },
  }
}

async function hydrate(record: ChatRecord) {
  if (!record.id) return
  const timeline = await chatApi.get_timeline(record.id, {
    silent: true,
    runId: record.run_id,
    view: 'compact',
  })
  if (timeline?.items) {
    timelineMap.value = replaceItems(itemsForRun(timeline.items as ProcessItem[], record.run_id))
  }
}

const activeSide = computed(() => tabs.value.find((item) => item.id === activeTab.value) || null)

function term(group: string, code: string) {
  if (!code) return ''
  const key = `knowledge.${group}_${code}`
  const text = t(key)
  return text === key ? code : text
}

function claimLabel(item: WikiProposal) {
  return [term('wiki_op', item.op), item.detail || item.claim_path].filter(Boolean).join(' ')
}

async function refreshProposals() {
  if (!chatId.value) {
    proposals.value = []
    return
  }
  proposals.value = unwrap(await knowledgeApi.chatProposals(chatId.value)) || []
  const open = new Set(proposals.value.map((item) => item.id))
  tabs.value = tabs.value.filter((tab) => tab.kind !== 'change' || open.has(tab.proposal?.id || 0))
  for (const tab of tabs.value) {
    if (tab.kind !== 'change' || !tab.proposal) continue
    tab.proposal = proposals.value.find((item) => item.id === tab.proposal?.id) || tab.proposal
  }
  if (activeTab.value && !tabs.value.some((tab) => tab.id === activeTab.value)) {
    activeTab.value = tabs.value[0]?.id || ''
  }
}

async function loadFocus(id: number) {
  const epoch = ++focusEpoch
  const focus = unwrap(await knowledgeApi.maintainFocus(id))
  if (epoch !== focusEpoch || chatId.value !== id) return
  chips.value = [
    ...(focus?.pages || []).map((item) => ({
      kind: 'page' as const,
      belong: item.belong,
      page_key: item.page_key,
      title: item.title || item.page_key,
    })),
    ...(focus?.sources || []).map((item) => ({
      kind: 'source' as const,
      source_id: item.source_id,
      title: item.title || item.locator,
      locator: item.locator,
    })),
  ]
}

function timelineInterrupts(record: ChatRecord) {
  return (record.interrupts || []).filter((item) => {
    const questions = item.payload?.questions || []
    return !questions.some((question) => question.question_id === 'wiki_patch_accept')
  })
}

function startSideResize(event: PointerEvent) {
  const root = (event.currentTarget as HTMLElement).parentElement
  if (!root) return
  const startX = event.clientX
  const startWidth = sideWidth.value
  sideDragging.value = true
  const move = (ev: PointerEvent) => {
    const max = Math.max(280, root.clientWidth - 280 - 280 - 6)
    sideWidth.value = Math.min(max, Math.max(280, startWidth - (ev.clientX - startX)))
  }
  const up = () => {
    sideDragging.value = false
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', up)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    stopSideResize = undefined
  }
  stopSideResize = up
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  window.addEventListener('pointermove', move)
  window.addEventListener('pointerup', up)
}

function clearTabs() {
  tabs.value = []
  activeTab.value = ''
}

function closeTab(id: string) {
  tabs.value = tabs.value.filter((tab) => tab.id !== id)
  if (activeTab.value === id) activeTab.value = tabs.value[0]?.id || ''
}

function chipTabId(chip: Chip) {
  if (chip.kind === 'page') return `page:${chip.belong}/${chip.page_key}`
  if (chip.kind === 'record') return `record:${chip.record_id}`
  if (chip.kind === 'source') return `source:${chip.source_id}`
  return `paste:${chip.title}:${chip.body.slice(0, 32)}`
}

function feedbackLabel(value: string) {
  if (value === 'up') return t('qa.feedback_up')
  if (value === 'down') return t('qa.feedback_down')
  return value
}

function errorText(error: unknown) {
  const data = (error as { response?: { data?: unknown } })?.response?.data
  if (typeof data === 'string' && data) return data
  if (data && typeof data === 'object') {
    const body = data as { msg?: unknown; detail?: unknown }
    if (typeof body.msg === 'string' && body.msg) return body.msg
    if (typeof body.detail === 'string' && body.detail) return body.detail
  }
  return ''
}

async function openPreview(chip: Chip) {
  const id = chipTabId(chip)
  const existing = tabs.value.find((tab) => tab.id === id)
  if (existing) {
    activeTab.value = id
    return
  }
  const tab: SideTab = {
    id,
    title: chipLabel(chip),
    kind: 'preview',
    preview: null,
    loading: true,
    proposal: null,
  }
  tabs.value = [...tabs.value, tab]
  activeTab.value = id
  try {
    if (chip.kind === 'paste') {
      tab.preview = {
        kind: 'document',
        title: chip.title || t('knowledge.wiki_paste'),
        subtitle: '',
        question: '',
        body: chip.body,
        feedback: '',
        comment: '',
      }
      return
    }
    if (!corpusKey.value) return
    const params =
      chip.kind === 'page'
        ? { kind: 'page' as const, belong: chip.belong, page_key: chip.page_key }
        : chip.kind === 'record'
          ? { kind: 'record' as const, record_id: chip.record_id }
          : { kind: 'source' as const, source_id: chip.source_id }
    tab.preview = unwrap(await knowledgeApi.previewMaterial(corpusKey.value, params))
  } catch (error) {
    closeTab(id)
    ElMessage.error(errorText(error) || t('knowledge.wiki_preview_failed'))
  } finally {
    tab.loading = false
  }
}

function openChange(item: WikiProposal) {
  const id = `change:${item.id}`
  if (!tabs.value.some((tab) => tab.id === id)) {
    tabs.value = [
      ...tabs.value,
      {
        id,
        title: [item.belong, item.page_key].filter(Boolean).join('/') || item.claim_path,
        kind: 'change',
        preview: null,
        loading: false,
        proposal: item,
      },
    ]
  }
  activeTab.value = id
}

async function decideChange(item: WikiProposal, decision: 'accept' | 'reject') {
  try {
    await knowledgeApi.decideProposal(item.id, decision)
    await refreshProposals()
    await loadLane()
  } catch (error) {
    ElMessage.error(errorText(error) || t('knowledge.wiki_send_failed'))
  }
}

async function openChat(id: number) {
  chatId.value = id
  menu.value = ''
  draft.value = ''
  chips.value = []
  clearTabs()
  await loadFocus(id)
  const info = chatApi.toChatInfo(await chatApi.get(id))
  records.value = info?.records || []
  liveRecord.value = records.value[records.value.length - 1] || null
  timelineMap.value = new Map()
  await refreshProposals()
  if (!liveRecord.value) return
  await hydrate(liveRecord.value)
  const status = liveRecord.value.run_status || ''
  if (['queued', 'running'].includes(status) && !busy.value) {
    await turn.attach(liveRecord.value, turnHandlers(liveRecord.value))
  }
}

function startNew(corpus?: string) {
  focusEpoch += 1
  if (corpus) corpusKey.value = corpus
  else if (!corpusKey.value && laneGroups.value[0]) {
    corpusKey.value = laneGroups.value[0].corpus_key
  }
  chatId.value = null
  records.value = []
  liveRecord.value = null
  timelineMap.value = new Map()
  proposals.value = []
  draft.value = ''
  chips.value = []
  menu.value = ''
  clearTabs()
  if (corpus) collapsed.value = { ...collapsed.value, [corpus]: false }
}

async function choose(item: WikiDialogueItem, corpus: string) {
  if (corpus && corpus !== corpusKey.value) corpusKey.value = corpus
  if (item.chat_id) await openChat(item.chat_id)
}

function addPage(page: WikiPageSummary) {
  if (
    chips.value.some(
      (item) =>
        item.kind === 'page' && item.page_key === page.page_key && item.belong === page.belong
    )
  ) {
    return
  }
  chips.value.push({
    kind: 'page',
    belong: page.belong,
    page_key: page.page_key,
    title: page.title || page.page_key,
  })
}

function addRecords(rows: WikiConversationGroup['records'], title: string) {
  rows.forEach((row) => {
    if (chips.value.some((chip) => chip.kind === 'record' && chip.record_id === row.record_id)) {
      return
    }
    chips.value.push({
      kind: 'record',
      record_id: row.record_id,
      title: row.question || title,
    })
  })
  menu.value = ''
}

function pasteDocument() {
  const body = pasteBody.value.trim()
  if (!body) return
  chips.value.push({
    kind: 'paste',
    title: pasteTitle.value.trim(),
    body,
  })
  pasteTitle.value = ''
  pasteBody.value = ''
  menu.value = ''
}

function removeChip(index: number) {
  chips.value.splice(index, 1)
}

async function send() {
  if (!canSend.value || !corpusKey.value) {
    if (!chips.value.length) ElMessage.warning(t('knowledge.wiki_need_context'))
    return
  }
  const question = draft.value.trim()
  if (!question) return
  const pagesPayload = chips.value
    .filter((item): item is Extract<Chip, { kind: 'page' }> => item.kind === 'page')
    .map((item) => ({ belong: item.belong, page_key: item.page_key }))
  const sourceIds = chips.value
    .filter((item): item is Extract<Chip, { kind: 'source' }> => item.kind === 'source')
    .map((item) => item.source_id)
  const recordIds = chips.value
    .filter((item): item is Extract<Chip, { kind: 'record' }> => item.kind === 'record')
    .map((item) => item.record_id)
  try {
    if (recordIds.length) {
      const captured = unwrap(await knowledgeApi.captureMaterials(recordIds)) || []
      captured.forEach((item) => sourceIds.push(item.source_id))
    }
    for (const item of chips.value) {
      if (item.kind !== 'paste') continue
      const created = unwrap(
        await knowledgeApi.pasteSource(corpusKey.value, { title: item.title, body: item.body })
      )
      sourceIds.push(created.source_id)
    }
    let id = chatId.value
    if (!id) {
      const opened = unwrap(
        await knowledgeApi.openMaintainChat(corpusKey.value, {
          pages: pagesPayload,
          source_ids: sourceIds,
          brief: question.slice(0, 20),
        })
      )
      id = opened.chat_id
      chatId.value = id
    } else {
      await knowledgeApi.updateMaintainFocus(id, {
        pages: pagesPayload,
        source_ids: sourceIds,
        replace: true,
      })
    }
    await loadFocus(id)
    const record = new ChatRecord()
    record.question = question
    record.sql_answer = ''
    records.value = [...records.value, record]
    liveRecord.value = record
    timelineMap.value = new Map()
    proposals.value = []
    draft.value = ''
    await turn.run(id, record, turnHandlers(record))
    await loadLane()
  } catch (error) {
    ElMessage.error(errorText(error) || t('knowledge.wiki_send_failed'))
  }
}

async function resumeClarification(payload: {
  interrupt: ConversationInterrupt
  answers: ResumeAnswer[]
  displayText: string
}) {
  if (!liveRecord.value) return
  await turn.resume(
    liveRecord.value,
    payload.interrupt,
    payload.answers,
    turnHandlers(liveRecord.value)
  )
  await refreshProposals()
  await loadLane()
}

async function correctClarification(payload: {
  interrupt: ConversationInterrupt
  answer: ResumeAnswer
  supersedesEvidenceId: string
}) {
  if (!liveRecord.value) return
  await turn.correct(
    liveRecord.value,
    payload.interrupt,
    payload.answer,
    payload.supersedesEvidenceId,
    turnHandlers(liveRecord.value)
  )
}

watch(laneGroups, async (next) => {
  if (!chatId.value || busy.value) return
  const row = next
    .flatMap((group) => group.items)
    .find((item) => item.kind === 'chat' && item.chat_id === chatId.value)
  if (row?.run_status && row.run_status !== liveRecord.value?.run_status) {
    await openChat(chatId.value)
  }
})

watch(corpusKey, async (next) => {
  if (!next) return
  await Promise.all([loadPages(), loadGroups()])
})

onMounted(async () => {
  await loadLane()
  const requested = Number(route.query.chat || 0)
  if (requested) await openChat(requested)
  pollTimer = setInterval(() => {
    void loadLane()
  }, 4000)
})

onBeforeUnmount(() => {
  stopSideResize?.()
  if (pollTimer) clearInterval(pollTimer)
  turn.detach()
})
</script>

<template>
  <main class="wiki-dialogue" :style="dialogueColumns">
    <aside class="lane-list">
      <button type="button" class="new-chat" @click="startNew()">
        {{ t('knowledge.wiki_dialogue_new') }}
      </button>
      <section v-for="group in laneGroups" :key="group.corpus_key" class="corpus-group">
        <header class="corpus-head">
          <button type="button" class="corpus-toggle" @click="toggleGroup(group.corpus_key)">
            <span class="chevron">{{ groupCollapsed(group) ? '▸' : '▾' }}</span>
            <strong>{{ group.name || group.corpus_key }}</strong>
          </button>
          <span v-if="group.processing" class="count processing">
            {{ t('knowledge.wiki_dialogue_processing') }} {{ group.processing }}
          </span>
          <span v-if="group.pending" class="count pending">
            {{ t('knowledge.wiki_dialogue_pending') }} {{ group.pending }}
          </span>
          <button type="button" class="corpus-add" @click="startNew(group.corpus_key)">+</button>
        </header>
        <div v-show="!groupCollapsed(group)">
          <button
            v-for="item in group.items"
            :key="`${item.kind}-${item.chat_id || item.source_id}`"
            type="button"
            class="lane-row"
            :class="{ 'is-active': item.kind === 'chat' && item.chat_id === chatId }"
            @click="choose(item, group.corpus_key)"
          >
            <span class="lane-copy">
              <strong>{{ item.title }}</strong>
              <small>{{ relativeTime(item.update_time) }}</small>
            </span>
            <i v-if="item.status !== 'done'" class="lane-dot" :class="item.status" />
          </button>
        </div>
      </section>
    </aside>

    <section class="thread">
      <div class="messages">
        <article v-for="(record, index) in records" :key="record.id || index" class="turn">
          <p class="ask">{{ record.question }}</p>
          <AgentStagesView
            v-if="record === liveRecord"
            :items="timelineItems"
            :interrupts="timelineInterrupts(record)"
            :loading="busy"
            :is-typing="busy"
            :awaiting-input="record.run_status === 'awaiting_input'"
            :record-id="record.id"
            @submit-clarification="resumeClarification"
            @correct-clarification="correctClarification"
          />
          <MdComponent v-if="record.sql_answer" :message="record.sql_answer" />
          <p v-else-if="record === liveRecord && proposals.length && !busy" class="result-note">
            {{ t('knowledge.wiki_result_changes', { n: proposals.length }) }}
          </p>
        </article>
      </div>
      <section v-if="proposals.length" class="change-list">
        <header>{{ t('knowledge.wiki_changes') }} {{ proposals.length }}</header>
        <button
          v-for="item in proposals"
          :key="item.id"
          type="button"
          class="change-row"
          :class="{ 'is-active': activeTab === `change:${item.id}` }"
          @click="openChange(item)"
        >
          <strong>{{ [item.belong, item.page_key].filter(Boolean).join('/') }}</strong>
          <small>{{ claimLabel(item) }}</small>
        </button>
      </section>

      <footer class="composer">
        <div class="chips">
          <span v-for="(chip, index) in chips" :key="`${chip.kind}-${index}`" class="chip">
            <button type="button" class="chip-open" @click="openPreview(chip)">
              {{ chipLabel(chip) }}
            </button>
            <button type="button" @click="removeChip(index)">×</button>
          </span>
          <button type="button" class="chip add" @click="menu = menu ? '' : 'page'">
            {{ t('knowledge.wiki_attach') }}
          </button>
        </div>
        <div v-if="menu" class="attach-menu">
          <div class="attach-tabs">
            <button type="button" :class="{ on: menu === 'page' }" @click="menu = 'page'">
              {{ t('knowledge.wiki_pick_page') }}
            </button>
            <button type="button" :class="{ on: menu === 'chat' }" @click="menu = 'chat'">
              {{ t('knowledge.wiki_pick_record') }}
            </button>
            <button type="button" :class="{ on: menu === 'paste' }" @click="menu = 'paste'">
              {{ t('knowledge.wiki_paste') }}
            </button>
            <button type="button" disabled>{{ t('knowledge.wiki_db_soon') }}</button>
          </div>
          <div v-if="menu === 'page'">
            <el-input v-model="pageQuery" size="small" />
            <button
              v-for="page in filteredPages"
              :key="`${page.belong}/${page.page_key}`"
              type="button"
              class="pick"
              @click="addPage(page)"
            >
              {{ page.title || page.page_key }}
            </button>
          </div>
          <div v-else-if="menu === 'chat'">
            <article v-for="group in groups" :key="group.chat_id" class="group">
              <header>
                <strong>{{ group.title }}</strong>
                <button type="button" @click="addRecords(group.records, group.title)">
                  {{ t('knowledge.wiki_whole_chat') }}
                </button>
              </header>
              <button
                v-for="row in group.records"
                :key="row.record_id"
                type="button"
                class="pick"
                @click="addRecords([row], row.question)"
              >
                {{ row.question }}
              </button>
            </article>
          </div>
          <div v-else class="paste">
            <el-input v-model="pasteTitle" size="small" />
            <el-input
              v-model="pasteBody"
              type="textarea"
              :rows="4"
              :placeholder="t('knowledge.wiki_paste_placeholder')"
            />
            <el-button size="small" type="primary" @click="pasteDocument">
              {{ t('knowledge.wiki_paste_submit') }}
            </el-button>
          </div>
        </div>
        <el-input
          v-model="draft"
          type="textarea"
          :rows="3"
          :placeholder="t('knowledge.wiki_maintain_placeholder')"
          @keydown.enter.exact.prevent="send"
        />
        <el-button type="primary" :disabled="!canSend" @click="send">
          {{ t('knowledge.wiki_maintain_send') }}
        </el-button>
      </footer>
    </section>
    <div
      v-if="tabs.length"
      class="side-split"
      :class="{ 'is-dragging': sideDragging }"
      role="separator"
      aria-orientation="vertical"
      :title="t('knowledge.wiki_resize_side')"
      @pointerdown.prevent="startSideResize"
    />
    <aside v-if="tabs.length" class="side">
      <div class="side-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="side-tab"
          :class="{ on: tab.id === activeTab }"
          @click="activeTab = tab.id"
        >
          <span>{{ tab.title }}</span>
          <i @click.stop="closeTab(tab.id)">×</i>
        </button>
      </div>
      <div v-if="activeSide?.kind === 'preview'" class="side-body">
        <p v-if="activeSide.loading" class="preview-sub">{{ t('knowledge.wiki_preview') }}</p>
        <RecordPreview
          v-else-if="
            activeSide.preview?.kind === 'record' &&
            activeSide.preview.chat_id &&
            activeSide.preview.record_id
          "
          :chat-id="activeSide.preview.chat_id"
          :record-id="activeSide.preview.record_id"
        />
        <template v-else>
          <p v-if="activeSide.preview?.subtitle" class="preview-sub">
            {{ activeSide.preview.subtitle }}
          </p>
          <p v-if="activeSide.preview?.question" class="preview-q">
            {{ activeSide.preview.question }}
          </p>
          <p v-if="activeSide.preview?.feedback" class="preview-sub">
            {{ feedbackLabel(activeSide.preview.feedback) }}
            <span v-if="activeSide.preview.comment"> · {{ activeSide.preview.comment }}</span>
          </p>
          <MdComponent v-if="activeSide.preview?.body" :message="activeSide.preview.body" />
          <p v-else-if="!activeSide.loading" class="preview-sub">
            {{ t('knowledge.wiki_preview_empty') }}
          </p>
        </template>
      </div>
      <div v-else-if="activeSide?.proposal" class="side-body">
        <WikiReview :proposals="[activeSide.proposal]" :actions="false" />
        <div class="side-actions">
          <el-button type="primary" @click="decideChange(activeSide.proposal, 'accept')">
            {{ t('knowledge.wiki_accept') }}
          </el-button>
          <el-button @click="decideChange(activeSide.proposal, 'reject')">
            {{ t('knowledge.wiki_reject') }}
          </el-button>
        </div>
      </div>
    </aside>
  </main>
</template>

<style scoped>
.wiki-dialogue {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  height: calc(100vh - 48px);
  min-height: 0;
  color: var(--ed-text-color-primary);
}

.side-split {
  cursor: col-resize;
  touch-action: none;
}

.side-split::after {
  content: '';
  display: block;
  width: 1px;
  height: 100%;
  margin: 0 auto;
  background: var(--ed-border-color);
}

.side-split:hover::after,
.side-split.is-dragging::after {
  width: 2px;
  background: var(--ed-color-primary);
}

.change-list {
  border-top: 1px solid var(--ed-border-color);
  padding: 8px 16px;
}

.change-list header {
  margin-bottom: 4px;
  font-size: 12px;
  color: var(--ed-text-color-secondary);
}

.change-row {
  display: flex;
  width: 100%;
  align-items: baseline;
  gap: 8px;
  padding: 6px 8px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: inherit;
  text-align: left;
  cursor: pointer;
}

.change-row.is-active,
.change-row:hover {
  background: color-mix(in srgb, var(--ed-color-primary) 10%, #fff);
}

.change-row small,
.result-note {
  color: var(--ed-text-color-secondary);
}

.result-note {
  margin: 8px 0 0;
}

.side {
  display: flex;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  flex-direction: column;
}

.side-tabs {
  display: flex;
  gap: 4px;
  overflow: auto;
  padding: 8px 8px 0;
  border-bottom: 1px solid var(--ed-border-color);
}

.side-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 180px;
  padding: 6px 8px;
  border: 0;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.side-tab span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.side-tab.on {
  border-bottom-color: var(--ed-color-primary);
}

.side-tab i {
  font-style: normal;
}

.side-body {
  min-height: 0;
  overflow: auto;
  padding: 12px;
}

.side-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.lane-list {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: auto;
  border-right: 1px solid var(--ed-border-color);
  padding: 12px;
  gap: 8px;
}

.new-chat,
.corpus-add,
.corpus-toggle {
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.new-chat {
  padding: 8px 10px;
  border: 1px solid var(--ed-border-color);
  border-radius: 8px;
  text-align: left;
  font-weight: 600;
}

.corpus-head {
  display: flex;
  align-items: center;
  gap: 6px;
}

.corpus-toggle {
  display: flex;
  flex: 1;
  align-items: center;
  gap: 6px;
  min-width: 0;
  padding: 6px 0;
  text-align: left;
}

.corpus-toggle strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.count {
  flex: none;
  font-size: 11px;
  color: var(--ed-text-color-secondary);
}

.count.pending {
  color: var(--ed-color-warning);
}

.corpus-add {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  font-size: 16px;
  line-height: 20px;
}

.corpus-add:hover,
.new-chat:hover {
  background: color-mix(in srgb, var(--ed-color-primary) 12%, #fff);
}

.counts {
  display: flex;
  gap: 12px;
  margin: 8px 0;
  color: var(--ed-text-color-secondary);
  font-size: 12px;
}

.lane-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  text-align: left;
  cursor: pointer;
  color: inherit;
}

.lane-row.is-active,
.lane-row:hover {
  background: color-mix(in srgb, var(--ed-color-primary) 12%, #fff);
}

.lane-copy {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.lane-copy strong,
.pick {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lane-copy small {
  color: var(--ed-text-color-secondary);
}

.lane-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex: none;
}

.lane-dot.pending {
  background: var(--ed-color-warning);
}

.lane-dot.processing {
  border: 2px solid var(--ed-color-primary);
  border-right-color: transparent;
  animation: spin 0.8s linear infinite;
}

.thread {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}

.messages {
  flex: 1;
  overflow: auto;
  padding: 16px 20px;
}

.ask {
  font-weight: 600;
}

.proposals {
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
  font-size: 13px;
}

.proposals pre,
.paste :deep(textarea) {
  white-space: pre-wrap;
}

.composer {
  border-top: 1px solid var(--ed-border-color);
  padding: 12px 16px 16px;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--ed-color-primary) 12%, #fff);
  font-size: 12px;
}

.chip-open {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview {
  min-height: 0;
  overflow: auto;
  border-left: 1px solid var(--ed-border-color);
  padding: 16px;
}

.preview header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.preview header button {
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 18px;
}

.preview-sub,
.preview-q {
  color: var(--ed-text-color-secondary);
  white-space: pre-wrap;
}

.preview-q {
  color: var(--ed-text-color-primary);
}

.chip button,
.attach-tabs button,
.pick,
.group header button {
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.chip.add {
  border: 0;
  cursor: pointer;
}

.attach-menu {
  max-height: 240px;
  overflow: auto;
  margin-bottom: 8px;
  padding: 8px;
  border: 1px solid var(--ed-border-color);
  border-radius: 8px;
}

.attach-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.attach-tabs button.on {
  color: var(--ed-color-primary);
}

.attach-tabs button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.pick,
.group {
  display: block;
  width: 100%;
  text-align: left;
  padding: 4px 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
