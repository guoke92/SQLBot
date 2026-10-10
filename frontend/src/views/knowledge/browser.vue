<script lang="ts" setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus-secondary'
import {
  knowledgeApi,
  type WikiCorpusRow,
  type WikiPageDetail,
  type WikiPageSummary,
} from '@/api/knowledge'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import MaintainDrawer from '@/views/knowledge/maintain-drawer.vue'

const { t } = useI18n()
const route = useRoute()
const maintainOpen = ref(false)
const maintainChatId = ref<number | null>(null)
const maintainStarter = ref('')

const loading = ref(false)
const detailLoading = ref(false)
const corpora = ref<WikiCorpusRow[]>([])
const corpusKey = ref('')
const query = ref('')
const status = ref('')
const pages = ref<WikiPageSummary[]>([])
const counts = ref<{ belong: string; count: number }[]>([])
const selected = ref<WikiPageSummary | null>(null)
const detail = ref<WikiPageDetail | null>(null)
const tabs = ref<WikiPageSummary[]>([])
const expanded = ref<Record<string, boolean>>({})
const bodyEl = ref<HTMLElement | null>(null)
const outline = ref<{ id: string; text: string; level: number }[]>([])
const listRefs = new Map<string, HTMLElement>()

const belongLabel = (name: string) => {
  const key = `knowledge.belong_${name}`
  const label = t(key)
  return label === key ? name : label
}

const statusLabel = (name: string) => {
  if (name === 'published') return t('knowledge.wiki_published')
  if (name === 'draft') return t('knowledge.wiki_draft')
  if (name === 'retired') return t('knowledge.wiki_retired')
  return name
}

const statusTag = (name: string): 'success' | 'warning' | 'info' => {
  if (name === 'published') return 'success'
  if (name === 'draft') return 'warning'
  return 'info'
}

const pageIdentity = (page: { belong: string; page_key: string }) =>
  `${page.belong}/${page.page_key}`

const grouped = computed(() =>
  counts.value.map((item) => ({
    ...item,
    label: belongLabel(item.belong),
    pages: pages.value.filter((page) => page.belong === item.belong),
  }))
)

const readingBody = computed(() => linkifyWiki(readableMarkdown(detail.value?.body || '')))

const backlinks = computed(() => {
  const current = detail.value
  if (!current) return []
  const names = new Set(
    [current.page_key, current.title, pageIdentity(current)].map((item) => item.trim())
  )
  return pages.value.filter((page) => {
    if (pageIdentity(page) === pageIdentity(current)) return false
    return (page.links || []).some((link) => names.has(link.split('#')[0].trim()))
  })
})

function readableMarkdown(body: string): string {
  return body.replace(/\n{3,}/g, '\n\n').trim()
}

function linkifyWiki(body: string): string {
  return body.replace(/\[\[([^\]|]+?)(?:\|([^\]]+))?\]\]/g, (_match, target, alias) => {
    const raw = String(target || '').trim()
    const base = raw.split('#')[0].trim()
    const hash = raw.includes('#') ? raw.slice(raw.indexOf('#') + 1).trim() : ''
    const label = String(alias || hash || base.split('/').pop() || base).replace(/[[\]]/g, '')
    return `[${label}](#wiki=${encodeURIComponent(base)})`
  })
}

function setListRef(id: string, el: unknown) {
  if (el instanceof HTMLElement) listRefs.set(id, el)
  else listRefs.delete(id)
}

const loadCorpora = async () => {
  corpora.value = (await knowledgeApi.listCorpora()) || []
  if (!corpusKey.value && corpora.value.length) {
    corpusKey.value = corpora.value[0].corpus_key
  }
}

let pageLoad = 0
const loadPages = async () => {
  const key = corpusKey.value
  const token = ++pageLoad
  if (!key) {
    pages.value = []
    counts.value = []
    return
  }
  loading.value = true
  try {
    const catalog = await knowledgeApi.listPages(key, {
      q: query.value || undefined,
      status: status.value || undefined,
    })
    if (token !== pageLoad) return
    counts.value = catalog?.counts || []
    pages.value = catalog?.pages || []
    if (query.value.trim()) {
      const next: Record<string, boolean> = {}
      for (const item of counts.value) next[item.belong] = true
      expanded.value = next
    }
    if (!selected.value && pages.value.length) {
      openPage(pages.value[0], false)
    } else if (selected.value) {
      expanded.value = { ...expanded.value, [selected.value.belong]: true }
    }
  } finally {
    if (token === pageLoad) loading.value = false
  }
}

let detailLoad = 0
const loadDetail = async (page: WikiPageSummary | null) => {
  const key = corpusKey.value
  const token = ++detailLoad
  if (!page || !key) {
    detail.value = null
    outline.value = []
    return
  }
  detailLoading.value = true
  try {
    const next = await knowledgeApi.readPage(key, page.belong, page.page_key)
    if (token !== detailLoad) return
    detail.value = next
    await refreshOutline()
  } finally {
    if (token === detailLoad) detailLoading.value = false
  }
}

async function refreshOutline() {
  await nextTick()
  const root = bodyEl.value
  if (!root) {
    outline.value = []
    return
  }
  outline.value = [...root.querySelectorAll('h1, h2, h3')].map((el, index) => {
    const id = `wiki-h-${index}`
    el.id = id
    return {
      id,
      text: (el.textContent || '').trim(),
      level: Number(el.tagName.slice(1)),
    }
  })
}

function scrollToHeading(id: string) {
  bodyEl.value?.querySelector(`#${id}`)?.scrollIntoView({ block: 'start' })
}

function toggleGroup(belong: string) {
  expanded.value = { ...expanded.value, [belong]: !groupOpen(belong) }
}

function expandAll() {
  const next: Record<string, boolean> = {}
  for (const item of counts.value) next[item.belong] = true
  expanded.value = next
}

function collapseAll() {
  const next: Record<string, boolean> = {}
  for (const item of counts.value) next[item.belong] = false
  expanded.value = next
}

function groupOpen(belong: string) {
  if (query.value.trim() && expanded.value[belong] !== false) return true
  return expanded.value[belong] === true
}

function openPage(page: WikiPageSummary, reveal = true) {
  if (!tabs.value.some((item) => pageIdentity(item) === pageIdentity(page))) {
    tabs.value = [...tabs.value, page]
  }
  selected.value = page
  expanded.value = { ...expanded.value, [page.belong]: true }
  if (!reveal) return
  void nextTick(() => {
    listRefs.get(pageIdentity(page))?.scrollIntoView({ block: 'nearest' })
  })
}

function closeTab(page: WikiPageSummary) {
  const id = pageIdentity(page)
  const next = tabs.value.filter((item) => pageIdentity(item) !== id)
  tabs.value = next
  if (selected.value && pageIdentity(selected.value) === id) {
    selected.value = next.at(-1) || null
  }
}

function closeOtherTabs() {
  if (!selected.value) return
  tabs.value = [selected.value]
}

function resolvePage(target: string): WikiPageSummary | undefined {
  const normalized = target.replace(/\.md$/i, '').split('#')[0].trim()
  return pages.value.find(
    (page) =>
      pageIdentity(page) === normalized || page.page_key === normalized || page.title === normalized
  )
}

function openTarget(target: string) {
  const hit = resolvePage(target)
  if (!hit) {
    ElMessage.info(t('knowledge.wiki_link_missing'))
    return
  }
  if (status.value && hit.status !== status.value) status.value = ''
  if (query.value.trim()) {
    const needle = query.value.trim().toLowerCase()
    const haystack = `${hit.title} ${hit.page_key} ${(hit.aliases || []).join(' ')}`.toLowerCase()
    if (!haystack.includes(needle)) query.value = ''
  }
  openPage(hit)
}

function onBodyClick(event: MouseEvent) {
  const anchor = (event.target as HTMLElement | null)?.closest('a')
  if (!anchor) return
  const href = anchor.getAttribute('href') || ''
  if (!href.startsWith('#wiki=')) return
  event.preventDefault()
  openTarget(decodeURIComponent(href.slice('#wiki='.length)))
}

let queryTimer: number | null = null
watch(query, () => {
  if (queryTimer != null) window.clearTimeout(queryTimer)
  queryTimer = window.setTimeout(() => {
    void loadPages()
  }, 200)
})

watch(corpusKey, () => {
  selected.value = null
  detail.value = null
  tabs.value = []
  expanded.value = {}
  void loadPages()
})

watch(status, () => {
  void loadPages()
})

watch(selected, (page) => {
  void loadDetail(page)
})

onMounted(async () => {
  await loadCorpora()
  const corpus = String(route.query.corpus || '')
  if (corpus && corpora.value.some((item) => item.corpus_key === corpus)) {
    corpusKey.value = corpus
  }
  const maintain = Number(route.query.maintain || 0)
  if (maintain) {
    maintainChatId.value = maintain
    maintainStarter.value = sessionStorage.getItem('wiki-maintain-starter') || ''
    sessionStorage.removeItem('wiki-maintain-starter')
    maintainOpen.value = true
  }
})

function openMaintain() {
  maintainChatId.value = null
  maintainStarter.value = ''
  maintainOpen.value = true
}

async function promoteCurrent() {
  if (!detail.value || !corpusKey.value) return
  await knowledgeApi.promotePage(corpusKey.value, detail.value.belong, detail.value.page_key)
  await loadDetail(selected.value)
  await loadPages()
}

function onMaintainApplied() {
  void loadDetail(selected.value)
  void loadPages()
}
</script>

<template>
  <main class="wiki-browser">
    <div class="wiki-toolbar">
      <el-select
        v-model="corpusKey"
        class="wiki-corpus"
        :placeholder="t('knowledge.wiki_select_corpus')"
      >
        <el-option
          v-for="item in corpora"
          :key="item.corpus_key"
          :label="item.name || item.corpus_key"
          :value="item.corpus_key"
        />
      </el-select>
      <div class="wiki-heading">
        <h2 class="wiki-title">{{ t('knowledge.wiki_browser') }}</h2>
        <p class="wiki-subtitle">{{ t('knowledge.wiki_browser_hint') }}</p>
      </div>
      <el-button class="wiki-maintain-btn" :disabled="!corpusKey" @click="openMaintain">
        {{ t('knowledge.wiki_maintain') }}
      </el-button>
    </div>

    <div v-if="!corpora.length" class="wiki-empty">{{ t('knowledge.wiki_empty') }}</div>

    <div v-else class="wiki-split">
      <aside class="wiki-tree">
        <div class="wiki-tree-tools">
          <el-input v-model="query" clearable :placeholder="t('knowledge.wiki_search_page')" />
          <div class="wiki-status-row">
            <button
              type="button"
              class="wiki-status-chip"
              :class="{ 'is-active': status === '' }"
              @click="status = ''"
            >
              {{ t('knowledge.wiki_all_status') }}
            </button>
            <button
              type="button"
              class="wiki-status-chip"
              :class="{ 'is-active': status === 'published' }"
              @click="status = 'published'"
            >
              {{ t('knowledge.wiki_published') }}
            </button>
            <button
              type="button"
              class="wiki-status-chip"
              :class="{ 'is-active': status === 'draft' }"
              @click="status = 'draft'"
            >
              {{ t('knowledge.wiki_draft') }}
            </button>
            <button
              type="button"
              class="wiki-status-chip"
              :class="{ 'is-active': status === 'retired' }"
              @click="status = 'retired'"
            >
              {{ t('knowledge.wiki_retired') }}
            </button>
          </div>
          <div class="wiki-tree-actions">
            <button type="button" @click="expandAll">{{ t('knowledge.wiki_expand_all') }}</button>
            <button type="button" @click="collapseAll">
              {{ t('knowledge.wiki_collapse_all') }}
            </button>
          </div>
        </div>
        <div v-loading="loading" class="wiki-tree-list">
          <p v-if="!grouped.length" class="wiki-empty">{{ t('knowledge.wiki_no_pages') }}</p>
          <section v-for="group in grouped" :key="group.belong">
            <button type="button" class="wiki-group-title" @click="toggleGroup(group.belong)">
              <span class="wiki-caret">{{ groupOpen(group.belong) ? '▾' : '▸' }}</span>
              <span class="wiki-group-name">{{ group.label }}</span>
              <span class="wiki-count">{{ group.count }}</span>
            </button>
            <template v-if="groupOpen(group.belong)">
              <button
                v-for="page in group.pages"
                :key="pageIdentity(page)"
                :ref="(el) => setListRef(pageIdentity(page), el)"
                type="button"
                class="wiki-page"
                :class="{ 'is-active': selected && pageIdentity(selected) === pageIdentity(page) }"
                @click="openPage(page)"
              >
                <span class="wiki-page-title">
                  <i class="wiki-status-dot" :class="`is-${page.status}`"></i>
                  {{ page.title || page.page_key }}
                </span>
                <span class="wiki-page-key">{{ page.page_key }}</span>
              </button>
            </template>
          </section>
        </div>
      </aside>

      <section class="wiki-read">
        <div class="wiki-tabs">
          <div
            v-for="tab in tabs"
            :key="pageIdentity(tab)"
            class="wiki-tab"
            :class="{ 'is-active': selected && pageIdentity(selected) === pageIdentity(tab) }"
          >
            <button type="button" class="wiki-tab-title" @click="openPage(tab)">
              {{ tab.title || tab.page_key }}
            </button>
            <button type="button" class="wiki-tab-close" @click="closeTab(tab)">×</button>
          </div>
          <button
            v-if="tabs.length > 1"
            type="button"
            class="wiki-tab-extra"
            @click="closeOtherTabs"
          >
            {{ t('knowledge.wiki_close_others') }}
          </button>
        </div>

        <div v-loading="detailLoading" class="wiki-detail">
          <p v-if="!detail" class="wiki-empty">{{ t('knowledge.wiki_pick_page') }}</p>
          <template v-else>
            <header :key="pageIdentity(detail)" class="wiki-detail-head">
              <p class="wiki-page-id">{{ detail.page_key }}</p>
              <h3>{{ detail.title }}</h3>
              <div class="wiki-chips">
                <el-tag size="small" effect="plain">{{ belongLabel(detail.belong) }}</el-tag>
                <el-tag size="small" :type="statusTag(detail.status)">
                  {{ statusLabel(detail.status) }}
                </el-tag>
                <el-tag v-if="detail.domain" size="small" effect="plain" type="info">
                  {{ detail.domain }}
                </el-tag>
                <el-tag v-if="detail.inactive" size="small" type="warning">
                  {{ t('knowledge.wiki_inactive_on') }}
                </el-tag>
                <el-tag size="small" :type="detail.recall ? 'success' : 'info'" effect="plain">
                  {{
                    detail.recall ? t('knowledge.wiki_recall_on') : t('knowledge.wiki_recall_off')
                  }}
                </el-tag>
                <el-button
                  v-if="detail.status !== 'published'"
                  size="small"
                  @click="promoteCurrent"
                >
                  {{ t('knowledge.wiki_promote') }}
                </el-button>
              </div>
            </header>
            <p v-if="detail.parse_error" class="wiki-parse-error">
              {{ t('knowledge.wiki_parse_error') }}：{{ detail.parse_error }}
            </p>

            <div class="wiki-detail-grid">
              <article ref="bodyEl" class="wiki-body" @click="onBodyClick">
                <MdComponent v-if="readingBody" :message="readingBody" />
              </article>
              <aside class="wiki-facts">
                <section v-if="outline.length">
                  <h4>{{ t('knowledge.wiki_outline') }}</h4>
                  <button
                    v-for="item in outline"
                    :key="item.id"
                    type="button"
                    class="wiki-outline"
                    :style="{ paddingLeft: `${(item.level - 1) * 12}px` }"
                    @click="scrollToHeading(item.id)"
                  >
                    {{ item.text }}
                  </button>
                </section>
                <section v-if="detail.aliases.length">
                  <h4>{{ t('knowledge.wiki_aliases') }}</h4>
                  <div class="wiki-chip-row">
                    <span v-for="item in detail.aliases" :key="item" class="wiki-pill">{{
                      item
                    }}</span>
                  </div>
                </section>
                <section v-if="detail.maps_to">
                  <h4>{{ t('knowledge.wiki_maps_to') }}</h4>
                  <button
                    type="button"
                    class="wiki-link"
                    @click="openTarget(detail.maps_to.split('.')[0])"
                  >
                    {{ detail.maps_to }}
                  </button>
                </section>
                <section v-if="detail.field_targets.length">
                  <h4>{{ t('knowledge.wiki_field_targets') }}</h4>
                  <button
                    v-for="item in detail.field_targets"
                    :key="item"
                    type="button"
                    class="wiki-link"
                    @click="openTarget(item.split('.')[0])"
                  >
                    {{ item }}
                  </button>
                </section>
                <section v-if="detail.anchors.length">
                  <h4>{{ t('knowledge.wiki_anchors') }}</h4>
                  <p>{{ detail.anchors.join('、') }}</p>
                </section>
                <section v-if="detail.databases.length">
                  <h4>{{ t('knowledge.wiki_databases') }}</h4>
                  <p>{{ detail.databases.join('、') }}</p>
                </section>
                <section v-if="detail.related.length || detail.links.length">
                  <h4>{{ t('knowledge.wiki_links') }}</h4>
                  <div class="wiki-chip-row">
                    <button
                      v-for="item in detail.related"
                      :key="`related-${item}`"
                      type="button"
                      class="wiki-pill wiki-pill-btn"
                      @click="openTarget(item)"
                    >
                      {{ item }}
                    </button>
                    <button
                      v-for="item in detail.links"
                      :key="`link-${item.target}-${item.alias}`"
                      type="button"
                      class="wiki-pill wiki-pill-btn"
                      @click="openTarget(item.target)"
                    >
                      {{ item.alias || item.target }}
                    </button>
                  </div>
                </section>
                <section v-if="backlinks.length">
                  <h4>{{ t('knowledge.wiki_backlinks') }}</h4>
                  <div class="wiki-chip-row">
                    <button
                      v-for="item in backlinks"
                      :key="pageIdentity(item)"
                      type="button"
                      class="wiki-pill wiki-pill-btn"
                      @click="openPage(item)"
                    >
                      {{ item.title || item.page_key }}
                    </button>
                  </div>
                </section>
                <section v-if="detail.also_confused_with.length">
                  <h4>{{ t('knowledge.wiki_confused') }}</h4>
                  <p>{{ detail.also_confused_with.join('、') }}</p>
                  <p v-if="detail.adjudication">{{ detail.adjudication }}</p>
                </section>
                <section v-if="detail.ground.length">
                  <h4>{{ t('knowledge.wiki_ground') }}</h4>
                  <p v-for="item in detail.ground" :key="`${item.kind}-${item.label}`">
                    {{ item.kind }}<template v-if="item.label"> · {{ item.label }}</template>
                  </p>
                </section>
                <section v-if="detail.reviews.length">
                  <h4>{{ t('knowledge.wiki_reviews') }}</h4>
                  <article v-for="item in detail.reviews" :key="`${item.type}-${item.title}`">
                    <p class="wiki-review-title">{{ item.title }}</p>
                    <p>{{ item.body }}</p>
                  </article>
                </section>
                <section v-if="detail.findings.length">
                  <h4>{{ t('knowledge.wiki_findings') }}</h4>
                  <p v-for="item in detail.findings" :key="`${item.code}-${item.message}`">
                    {{ item.message }}
                  </p>
                </section>
              </aside>
            </div>
          </template>
        </div>
      </section>
    </div>
    <MaintainDrawer
      v-model:visible="maintainOpen"
      :corpus-key="corpusKey"
      :page="selected"
      :chat-id="maintainChatId"
      :starter="maintainStarter"
      @applied="onMaintainApplied"
    />
  </main>
</template>

<style scoped>
.wiki-browser {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: calc(100vh - 48px);
  min-height: 0;
  padding: 0;
  box-sizing: border-box;
  color: var(--ed-text-color-primary);
  --wiki-tint: color-mix(in srgb, var(--ed-color-primary) 12%, #fff);
  --wiki-tint-strong: color-mix(in srgb, var(--ed-color-primary) 22%, #fff);
  --wiki-tint-line: color-mix(in srgb, var(--ed-color-primary) 40%, #fff);
}

.wiki-browser button {
  font-family: inherit;
}

.wiki-browser button:focus-visible {
  outline: 2px solid var(--ed-color-primary);
  outline-offset: 1px;
}

.wiki-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.wiki-heading {
  min-width: 0;
}

.wiki-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
}

.wiki-subtitle {
  margin: 2px 0 0;
  color: var(--ed-text-color-secondary);
  font-size: 12px;
  line-height: 18px;
}

.wiki-corpus {
  flex: none;
  width: 220px;
}

.wiki-maintain-btn {
  margin-left: auto;
}

.wiki-split {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  min-height: 0;
  flex: 1;
  border: 1px solid var(--ed-border-color-lighter);
  border-radius: 12px;
  overflow: hidden;
  background: var(--ed-bg-color);
}

.wiki-tree {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  border-right: 1px solid var(--ed-border-color-lighter);
  background: var(--ed-fill-color-lighter, #fafbfc);
}

.wiki-tree-tools {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  border-bottom: 1px solid var(--ed-border-color-lighter);
  background: var(--ed-bg-color);
}

.wiki-status-row {
  display: flex;
  gap: 2px;
  padding: 3px;
  border-radius: 8px;
  background: var(--ed-fill-color);
}

.wiki-status-chip,
.wiki-tree-actions button,
.wiki-tab-extra {
  border: 0;
  background: transparent;
  color: var(--ed-text-color-regular);
  font-size: 12px;
  line-height: 20px;
  border-radius: 6px;
  cursor: pointer;
}

.wiki-status-chip {
  flex: 1;
  padding: 4px 0;
  color: var(--ed-text-color-secondary);
}

.wiki-status-chip:hover,
.wiki-tree-actions button:hover,
.wiki-tab-extra:hover {
  color: var(--ed-text-color-primary);
  background: var(--ed-bg-color);
}

.wiki-status-chip:active,
.wiki-tree-actions button:active,
.wiki-tab-extra:active {
  background: var(--wiki-tint);
  color: var(--ed-color-primary);
}

.wiki-status-chip.is-active {
  background: var(--ed-bg-color);
  color: var(--ed-color-primary);
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(31, 35, 41, 0.12);
}

.wiki-tree-actions,
.wiki-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.wiki-tree-actions button,
.wiki-tab-extra {
  padding: 2px 8px;
}

.wiki-tree-list {
  min-height: 0;
  overflow: auto;
  padding: 8px;
}

.wiki-group-title {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  margin-bottom: 2px;
  padding: 7px 8px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  text-align: left;
  cursor: pointer;
  color: var(--ed-text-color-primary);
  font-weight: 600;
}

.wiki-group-title:hover {
  background: var(--ed-fill-color);
}

.wiki-group-title:active {
  background: var(--wiki-tint);
}

.wiki-caret {
  flex: none;
  width: 12px;
  color: var(--ed-text-color-secondary);
  font-size: 12px;
}

.wiki-group-name {
  min-width: 0;
}

.wiki-count {
  flex: none;
  min-width: 22px;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--ed-fill-color-dark);
  color: var(--ed-text-color-regular);
  font-size: 12px;
  font-weight: 600;
  line-height: 18px;
  text-align: center;
}

.wiki-page {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
  margin-bottom: 2px;
  padding: 7px 8px 7px 26px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  text-align: left;
  cursor: pointer;
  color: inherit;
  box-shadow: inset 2px 0 0 transparent;
  transition:
    background 0.12s ease,
    box-shadow 0.12s ease;
}

.wiki-page:hover {
  background: var(--ed-fill-color);
}

.wiki-page:active {
  background: var(--wiki-tint-strong);
}

.wiki-page.is-active {
  background: var(--wiki-tint);
  box-shadow: inset 3px 0 0 var(--ed-color-primary);
}

.wiki-page.is-active:hover {
  background: var(--wiki-tint-strong);
}

.wiki-page-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  line-height: 20px;
  color: var(--ed-text-color-primary);
}

.wiki-page.is-active .wiki-page-title {
  color: var(--ed-color-primary);
  font-weight: 600;
}

.wiki-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ed-text-color-placeholder);
  flex: none;
}

.wiki-status-dot.is-published {
  background: var(--ed-color-success);
}

.wiki-status-dot.is-draft {
  background: var(--ed-color-warning);
}

.wiki-status-dot.is-retired {
  background: var(--ed-text-color-disabled);
}

.wiki-page-key {
  padding-left: 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
  line-height: 16px;
  color: var(--ed-text-color-secondary);
}

.wiki-read {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  background: var(--ed-bg-color);
}

.wiki-tabs {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  min-height: 40px;
  padding: 6px 10px 0;
  overflow-x: auto;
  border-bottom: 1px solid var(--ed-border-color-lighter);
  background: var(--ed-fill-color-light);
}

.wiki-tab {
  display: flex;
  align-items: center;
  gap: 2px;
  max-width: 200px;
  height: 32px;
  padding: 0 4px 0 10px;
  border-radius: 8px 8px 0 0;
  color: var(--ed-text-color-regular);
  box-shadow: inset 0 2px 0 transparent;
}

.wiki-tab:hover {
  background: var(--ed-bg-color);
  color: var(--ed-text-color-primary);
}

.wiki-tab.is-active {
  background: var(--ed-bg-color);
  color: var(--ed-color-primary);
  font-weight: 600;
  box-shadow: inset 0 2px 0 var(--ed-color-primary);
}

.wiki-tab-title,
.wiki-tab-close {
  border: 0;
  background: transparent;
  cursor: pointer;
  color: inherit;
}

.wiki-tab-title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  line-height: 28px;
  text-align: left;
}

.wiki-tab-close {
  flex: none;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  color: var(--ed-text-color-secondary);
  line-height: 16px;
}

.wiki-tab-close:hover {
  background: var(--ed-fill-color);
  color: var(--ed-text-color-primary);
}

.wiki-tab-close:active {
  background: var(--wiki-tint-strong);
  color: var(--ed-color-primary);
}

.wiki-tab-extra {
  margin-left: auto;
  margin-bottom: 6px;
}

.wiki-detail {
  min-height: 0;
  overflow: auto;
  padding: 20px 24px 28px;
}

.wiki-detail-head {
  padding-bottom: 16px;
  border-bottom: 1px solid var(--ed-border-color-lighter);
  animation: wiki-arrive 0.18s ease;
}

.wiki-page-id {
  margin: 0 0 4px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  line-height: 18px;
  color: var(--ed-text-color-secondary);
}

.wiki-detail-head h3 {
  margin: 0 0 10px;
  font-size: 22px;
  font-weight: 600;
  line-height: 30px;
}

.wiki-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.wiki-parse-error {
  margin: 12px 0 0;
  padding: 8px 12px;
  border-radius: 8px;
  background: var(--ed-color-danger-light-9);
  color: var(--ed-color-danger);
  font-size: 13px;
}

.wiki-detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 20px;
  align-items: start;
  margin-top: 18px;
}

.wiki-body {
  min-width: 0;
  padding: 4px 8px 0 0;
}

.wiki-body :deep(.markdown-body) {
  background: transparent;
  font-size: 14px;
  line-height: 1.75;
  color: var(--ed-text-color-primary);
}

.wiki-body :deep(.markdown-body h1),
.wiki-body :deep(.markdown-body h2) {
  margin: 28px 0 12px;
  padding: 0 0 8px 10px;
  border-bottom: 1px solid var(--ed-border-color-lighter);
  border-left: 3px solid var(--ed-color-primary);
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
}

.wiki-body :deep(.markdown-body h1:first-child),
.wiki-body :deep(.markdown-body h2:first-child) {
  margin-top: 0;
}

.wiki-body :deep(.markdown-body h3) {
  margin: 18px 0 8px;
  padding: 0;
  border: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--ed-text-color-regular);
}

.wiki-body :deep(.markdown-body p) {
  margin: 0 0 12px;
}

.wiki-body :deep(.markdown-body ul),
.wiki-body :deep(.markdown-body ol) {
  margin: 0 0 14px;
  padding-left: 0;
  list-style: none;
}

.wiki-body :deep(.markdown-body li) {
  position: relative;
  margin: 4px 0;
  padding: 7px 10px 7px 16px;
  border-radius: 6px;
  background: var(--ed-fill-color-lighter);
}

.wiki-body :deep(.markdown-body li::before) {
  content: '';
  position: absolute;
  left: 6px;
  top: 15px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--ed-text-color-placeholder);
}

.wiki-body :deep(.markdown-body li:hover) {
  background: var(--wiki-tint);
}

.wiki-body :deep(.markdown-body :not(pre) > code) {
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--ed-fill-color);
  font-size: 12px;
  color: var(--ed-text-color-primary);
}

.wiki-body :deep(.markdown-body pre) {
  margin: 0 0 12px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--ed-fill-color-light);
  overflow: auto;
}

.wiki-body :deep(.markdown-body pre code) {
  padding: 0;
  background: transparent;
  font-size: 12px;
  white-space: pre-wrap;
}

.wiki-body :deep(.markdown-body a) {
  color: var(--ed-color-primary);
  font-weight: 500;
  text-decoration: none;
  border-radius: 4px;
}

.wiki-body :deep(.markdown-body a:hover) {
  text-decoration: underline;
  background: var(--wiki-tint);
}

.wiki-body :deep(.markdown-body a:active) {
  background: var(--wiki-tint-strong);
}

.wiki-body :deep(.markdown-body table) {
  display: table;
  width: 100%;
  margin: 8px 0 16px;
  border-collapse: collapse;
  font-size: 13px;
}

.wiki-body :deep(.markdown-body th),
.wiki-body :deep(.markdown-body td) {
  border: 1px solid var(--ed-border-color-lighter);
  padding: 8px 12px;
}

.wiki-body :deep(.markdown-body th) {
  background: var(--ed-fill-color-light);
  font-weight: 600;
}

.wiki-facts {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.wiki-facts section {
  margin: 0;
  padding: 12px;
  border-radius: 10px;
  background: var(--ed-fill-color-light);
}

.wiki-facts h4 {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--ed-text-color-secondary);
}

.wiki-facts p {
  margin: 0 0 6px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--ed-text-color-regular);
}

.wiki-facts p:last-child {
  margin-bottom: 0;
}

.wiki-outline,
.wiki-link {
  display: block;
  width: 100%;
  margin: 0;
  padding: 5px 8px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  text-align: left;
  cursor: pointer;
  font-size: 13px;
  line-height: 20px;
  color: var(--ed-text-color-regular);
}

.wiki-link {
  color: var(--ed-color-primary);
}

.wiki-outline:hover,
.wiki-link:hover {
  background: var(--ed-bg-color);
  color: var(--ed-color-primary);
}

.wiki-outline:active,
.wiki-link:active {
  background: var(--wiki-tint-strong);
}

.wiki-pill {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 2px 8px;
  border: 0;
  border-radius: 999px;
  background: var(--ed-bg-color);
  box-shadow: inset 0 0 0 1px var(--ed-border-color);
  font-size: 12px;
  line-height: 20px;
  color: var(--ed-text-color-primary);
}

.wiki-pill-btn {
  cursor: pointer;
  color: var(--ed-color-primary);
}

.wiki-pill-btn:hover {
  background: var(--wiki-tint);
  box-shadow: inset 0 0 0 1px var(--wiki-tint-line);
}

.wiki-pill-btn:active {
  background: var(--wiki-tint-strong);
}

.wiki-review-title {
  font-weight: 600;
  color: var(--ed-text-color-primary);
}

.wiki-empty {
  margin: 0;
  padding: 24px 8px;
  color: var(--ed-text-color-secondary);
}

@keyframes wiki-arrive {
  from {
    opacity: 0.35;
    transform: translateY(4px);
  }

  to {
    opacity: 1;
    transform: none;
  }
}
</style>
