<script lang="ts" setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  knowledgeApi,
  type WikiMaintainRecord,
  type WikiPageSummary,
  type WikiProposal,
} from '@/api/knowledge'
import { runApi, type ConversationInterrupt } from '@/api/chat'

const props = defineProps<{
  corpusKey: string
  page: WikiPageSummary | null
  chatId: number | null
  starter: string
}>()

const visible = defineModel<boolean>('visible', { default: false })
const emit = defineEmits<{ applied: [] }>()

const { t } = useI18n()
const draft = ref('')
const paste = ref('')
const showPaste = ref(false)
const busy = ref(false)
const activeChatId = ref<number | null>(null)
const messages = ref<{ role: 'user' | 'assistant'; content: string }[]>([])
const proposals = ref<WikiProposal[]>([])
const interrupt = ref<ConversationInterrupt | null>(null)
const runId = ref('')
const started = ref(false)
const rejectReason = ref('')
const accepted = ref(false)
const records = ref<WikiMaintainRecord[]>([])
const pageHits = ref<WikiPageSummary[]>([])
const selectedPages = ref<{ belong: string; page_key: string; title: string }[]>([])
const selectedSources = ref<{ source_id: number; title: string }[]>([])

watch(visible, (open) => {
  if (!open) return
  if (props.page) {
    const current = {
      belong: props.page.belong,
      page_key: props.page.page_key,
      title: props.page.title || props.page.page_key,
    }
    if (
      !selectedPages.value.some(
        (item) => item.page_key === current.page_key && item.belong === current.belong
      )
    ) {
      selectedPages.value = [current, ...selectedPages.value]
    }
  }
  void loadContext()
  if (props.starter && activeChatId.value && !started.value) {
    started.value = true
    void send(props.starter)
  }
})

async function loadContext() {
  if (!props.corpusKey) return
  try {
    records.value = unwrap(await knowledgeApi.maintainRecords(props.corpusKey)) || []
    const catalog = unwrap(await knowledgeApi.listPages(props.corpusKey, {}))
    pageHits.value = catalog.pages || []
  } catch {
    records.value = []
  }
}

function addPage(item: WikiPageSummary) {
  if (
    selectedPages.value.some(
      (page) => page.belong === item.belong && page.page_key === item.page_key
    )
  ) {
    return
  }
  selectedPages.value = [
    ...selectedPages.value,
    { belong: item.belong, page_key: item.page_key, title: item.title || item.page_key },
  ]
}

function removePage(belong: string, pageKey: string) {
  selectedPages.value = selectedPages.value.filter(
    (item) => item.belong !== belong || item.page_key !== pageKey
  )
}

async function addRecord(item: WikiMaintainRecord) {
  if (selectedSources.value.some((source) => source.title === item.locator)) return
  busy.value = true
  try {
    const captured = item.source_id
      ? { source_id: item.source_id }
      : unwrap(await knowledgeApi.sediment(item.record_id))
    selectedSources.value = [
      ...selectedSources.value,
      { source_id: captured.source_id, title: item.question || item.locator },
    ]
    if (activeChatId.value) {
      await knowledgeApi.updateMaintainFocus(activeChatId.value, {
        source_ids: [captured.source_id],
      })
    }
  } catch {
    // request interceptor already toasts HTTP errors
  } finally {
    busy.value = false
  }
}

watch(
  () => props.chatId,
  (value) => {
    activeChatId.value = value
    started.value = false
  },
  { immediate: true }
)

function unwrap<T>(value: T | { data?: T }): T {
  if (value && typeof value === 'object' && 'data' in value && value.data) return value.data
  return value as T
}

async function ensureChat() {
  if (activeChatId.value) return activeChatId.value
  if (!selectedPages.value.length && !selectedSources.value.length) {
    throw new Error('context required')
  }
  const opened = unwrap(
    await knowledgeApi.openMaintainChat(props.corpusKey, {
      pages: selectedPages.value.map((item) => ({
        belong: item.belong,
        page_key: item.page_key,
      })),
      source_ids: selectedSources.value.map((item) => item.source_id),
    })
  )
  activeChatId.value = opened.chat_id
  return opened.chat_id
}

async function send(question: string) {
  const text = question.trim()
  if (!text || busy.value || !props.corpusKey) return
  busy.value = true
  proposals.value = []
  interrupt.value = null
  messages.value.push({ role: 'user', content: text })
  draft.value = ''
  try {
    const id = await ensureChat()
    const created = unwrap(await runApi.create({ chat_id: id, question: text }))
    runId.value = created.run_id
    await watchRun(created.run_id)
  } catch {
    busy.value = false
  }
}

async function watchRun(id: string) {
  const terminal = new Set(['succeeded', 'degraded', 'failed', 'cancelled'])
  for (let attempt = 0; attempt < 150; attempt += 1) {
    const snap = unwrap(await runApi.snapshot(id))
    if (snap.status === 'awaiting_input') {
      proposals.value = unwrap(await knowledgeApi.proposals(id)) || []
      interrupt.value = snap.active_interrupt
      busy.value = false
      return
    }
    if (terminal.has(snap.status)) {
      const text = recordAnswer(snap.record) || snap.error_summary || ''
      if (text) messages.value.push({ role: 'assistant', content: text })
      proposals.value = []
      interrupt.value = null
      busy.value = false
      if (accepted.value && (snap.status === 'succeeded' || snap.status === 'degraded')) {
        accepted.value = false
        emit('applied')
      }
      return
    }
    await new Promise((resolve) => window.setTimeout(resolve, 1000))
  }
  busy.value = false
}

async function decide(optionId: 'accept' | 'reject') {
  const card = interrupt.value
  if (!card || !runId.value || busy.value) return
  busy.value = true
  try {
    await runApi.resume(runId.value, card.interrupt_id, {
      version: card.version,
      idempotency_key: crypto.randomUUID(),
      answers: [{ question_id: 'wiki_patch_accept', mode: 'option', option_id: optionId }],
    })
    if (optionId === 'accept') accepted.value = true
    rejectReason.value = ''
    proposals.value = []
    interrupt.value = null
    await watchRun(runId.value)
  } catch {
    busy.value = false
  }
}

async function supplement() {
  const card = interrupt.value
  const text = rejectReason.value.trim()
  if (!card || !runId.value || busy.value || !text) return
  busy.value = true
  messages.value.push({ role: 'user', content: text })
  try {
    await runApi.resume(runId.value, card.interrupt_id, {
      version: card.version,
      idempotency_key: crypto.randomUUID(),
      answers: [{ question_id: 'wiki_patch_accept', mode: 'custom', text }],
    })
    rejectReason.value = ''
    proposals.value = []
    interrupt.value = null
    await watchRun(runId.value)
  } catch {
    busy.value = false
  }
}

async function submitPaste() {
  const text = paste.value.trim()
  if (!text || busy.value || !props.corpusKey) return
  busy.value = true
  try {
    const opened = unwrap(
      await knowledgeApi.pasteSource(props.corpusKey, {
        title: props.page?.title || '',
        body: text,
      })
    )
    selectedSources.value = [
      ...selectedSources.value,
      { source_id: opened.source_id, title: text.slice(0, 40) },
    ]
    if (activeChatId.value) {
      await knowledgeApi.updateMaintainFocus(activeChatId.value, {
        source_ids: [opened.source_id],
      })
    }
    paste.value = ''
    showPaste.value = false
    busy.value = false
  } catch {
    busy.value = false
  }
}

function payloadText(item: WikiProposal) {
  try {
    return JSON.stringify(item.payload)
  } catch {
    return ''
  }
}

function recordAnswer(record: Record<string, unknown> | undefined): string {
  if (!record) return ''
  if (typeof record.sql_answer === 'string' && record.sql_answer.trim()) {
    return record.sql_answer
  }
  const answer = record.answer
  if (answer && typeof answer === 'object' && 'content' in answer) {
    const content = (answer as { content?: unknown }).content
    return typeof content === 'string' ? content : ''
  }
  return ''
}
</script>

<template>
  <el-drawer
    v-model="visible"
    :title="t('knowledge.wiki_maintain')"
    size="420px"
    append-to-body
    class="wiki-maintain-drawer"
  >
    <p class="wiki-maintain-hint">{{ t('knowledge.wiki_maintain_hint') }}</p>
    <div class="wiki-maintain-picks">
      <button
        v-for="item in selectedPages"
        :key="`${item.belong}/${item.page_key}`"
        type="button"
        class="wiki-maintain-chip"
        @click="removePage(item.belong, item.page_key)"
      >
        {{ item.title }}
      </button>
      <span v-for="item in selectedSources" :key="item.source_id" class="wiki-maintain-chip">
        {{ item.title }}
      </span>
    </div>
    <el-select
      class="wiki-maintain-select"
      filterable
      :placeholder="t('knowledge.wiki_pick_page')"
      @change="addPage"
    >
      <el-option
        v-for="item in pageHits"
        :key="`${item.belong}/${item.page_key}`"
        :label="item.title || item.page_key"
        :value="item"
      />
    </el-select>
    <el-select
      class="wiki-maintain-select"
      filterable
      :placeholder="t('knowledge.wiki_pick_record')"
      @change="addRecord"
    >
      <el-option
        v-for="item in records"
        :key="item.record_id"
        :label="item.question"
        :value="item"
      />
    </el-select>
    <div class="wiki-maintain-log">
      <p v-if="!messages.length" class="wiki-maintain-empty">
        {{ t('knowledge.wiki_maintain_empty') }}
      </p>
      <p
        v-for="(item, index) in messages"
        :key="index"
        class="wiki-maintain-line"
        :class="item.role"
      >
        {{ item.content }}
      </p>
      <p v-if="busy" class="wiki-maintain-line assistant">{{ t('knowledge.wiki_working') }}</p>
    </div>
    <section v-if="proposals.length" class="wiki-maintain-proposals">
      <h4>{{ t('knowledge.wiki_proposals') }}</h4>
      <article v-for="item in proposals" :key="item.id">
        <strong>{{ item.scope || item.op }}</strong>
        <span>{{ item.belong }}/{{ item.page_key }}</span>
        <span>{{ item.trust }} {{ item.source_ref }}</span>
        <span>{{ item.claim_path }}</span>
        <code>{{ payloadText(item) }}</code>
        <pre v-if="item.diff" class="wiki-maintain-diff">{{ item.diff }}</pre>
      </article>
      <el-input
        v-model="rejectReason"
        class="wiki-maintain-reason"
        :placeholder="t('knowledge.wiki_supplement')"
      />
      <div class="wiki-maintain-actions">
        <el-button type="primary" :disabled="busy" @click="decide('accept')">
          {{ t('knowledge.wiki_accept') }}
        </el-button>
        <el-button :disabled="busy" @click="decide('reject')">
          {{ t('knowledge.wiki_reject') }}
        </el-button>
        <el-button :disabled="busy || !rejectReason.trim()" @click="supplement">
          {{ t('knowledge.wiki_supplement_send') }}
        </el-button>
      </div>
    </section>
    <div class="wiki-maintain-compose">
      <el-input
        v-model="draft"
        type="textarea"
        :rows="3"
        :placeholder="t('knowledge.wiki_maintain_placeholder')"
        @keydown.enter.exact.prevent="send(draft)"
      />
      <div class="wiki-maintain-actions">
        <el-button :disabled="busy" @click="showPaste = !showPaste">
          {{ t('knowledge.wiki_paste') }}
        </el-button>
        <el-button type="primary" :disabled="busy || !draft.trim()" @click="send(draft)">
          {{ t('knowledge.wiki_maintain_send') }}
        </el-button>
      </div>
      <div v-if="showPaste" class="wiki-maintain-paste">
        <el-input
          v-model="paste"
          type="textarea"
          :rows="6"
          :placeholder="t('knowledge.wiki_paste_placeholder')"
        />
        <el-button type="primary" :disabled="busy || !paste.trim()" @click="submitPaste">
          {{ t('knowledge.wiki_paste_submit') }}
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<style scoped>
.wiki-maintain-hint,
.wiki-maintain-empty,
.wiki-maintain-page {
  margin: 0 0 8px;
  color: var(--ed-text-color-secondary);
  font-size: 12px;
  line-height: 18px;
}

.wiki-maintain-picks {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.wiki-maintain-chip {
  border: 1px solid var(--ed-border-color);
  border-radius: 999px;
  background: var(--ed-fill-color-light);
  color: var(--ed-text-color-primary);
  font-size: 12px;
  line-height: 20px;
  padding: 0 8px;
}

.wiki-maintain-select {
  width: 100%;
  margin-bottom: 8px;
}

.wiki-maintain-log {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 160px;
  max-height: 320px;
  overflow: auto;
  margin-bottom: 12px;
}

.wiki-maintain-line {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 13px;
}

.wiki-maintain-line.user {
  color: var(--ed-text-color-primary);
}

.wiki-maintain-line.assistant {
  color: var(--ed-text-color-regular);
}

.wiki-maintain-proposals {
  margin-bottom: 12px;
  padding: 10px;
  border: 1px solid var(--ed-border-color);
  border-radius: 8px;
}

.wiki-maintain-proposals h4 {
  margin: 0 0 8px;
  font-size: 13px;
}

.wiki-maintain-proposals article {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 8px;
  font-size: 12px;
}

.wiki-maintain-proposals code {
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--ed-text-color-secondary);
}

.wiki-maintain-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.wiki-maintain-reason {
  margin-bottom: 8px;
}

.wiki-maintain-diff {
  margin: 4px 0 0;
  padding: 8px;
  max-height: 160px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 11px;
  line-height: 1.45;
  color: var(--ed-text-color-regular);
  background: var(--ed-fill-color-light);
  border-radius: 6px;
}

.wiki-maintain-paste {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  margin-top: 8px;
}
</style>
