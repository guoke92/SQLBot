<script lang="ts" setup>
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type {
  KnowledgeImportItemResult,
  KnowledgeImportReport,
  KnowledgePackageDetail,
  KnowledgePackageItem,
  KnowledgePackageSummary,
} from '@/api/knowledge'
import KnowledgeItemDetail from './KnowledgeItemDetail.vue'
import {
  issueTranslationKey,
  knowledgeItemSummary,
  knowledgeItemTitle,
  knowledgeIssueText,
} from '../presentation'

const props = defineProps<{
  packages: KnowledgePackageSummary[]
  detail: KnowledgePackageDetail | null
  preview: KnowledgeImportReport | null
  selectedPackageId: string
  loading: boolean
  mode: 'preview' | 'applied' | 'registered'
}>()

const emit = defineEmits<{
  selectPackage: [packageId: string]
  query: [
    query: { keyword: string; kind: string; readiness: string; page: number; pageSize: number },
  ]
  advance: [item: KnowledgePackageItem, action: 'publish' | 'approve_publish']
  reject: [item: KnowledgePackageItem]
  gotoReview: [item: KnowledgePackageItem]
  openImport: []
}>()

const { t, te } = useI18n()
const query = reactive({ keyword: '', kind: '', readiness: '', page: 1, pageSize: 15 })
const detailVisible = ref(false)
const detailItem = ref<KnowledgeImportItemResult | null>(null)
const selectedItem = ref<KnowledgePackageItem | null>(null)

const selectedPackage = computed(() =>
  props.packages.find((item) => item.package_id === props.selectedPackageId)
)

const packageInfo = computed(() => props.detail?.package || selectedPackage.value)
const counts = computed(() => {
  if (props.mode === 'registered' && props.detail) {
    return {
      total: props.detail.total,
      kind: props.detail.kind_counts,
      readiness: props.detail.readiness_counts,
    }
  }
  return {
    total: props.preview?.total || 0,
    kind: props.preview?.kind_counts || {},
    readiness: props.preview?.readiness_counts || {},
  }
})

const previewItems = computed(() => {
  if (props.mode === 'registered') return []
  const keyword = query.keyword.trim().toLowerCase()
  return (props.preview?.items || []).filter((item) => {
    if (query.kind && item.kind !== query.kind) return false
    if (query.readiness && item.readiness !== query.readiness) return false
    if (!keyword) return true
    return [item.item_id, knowledgeItemTitle(item), knowledgeItemSummary(item)]
      .join(' ')
      .toLowerCase()
      .includes(keyword)
  })
})

const visiblePreviewItems = computed(() => {
  const start = (query.page - 1) * query.pageSize
  return previewItems.value.slice(start, start + query.pageSize)
})

const displayItems = computed(() =>
  props.mode === 'registered' ? props.detail?.items || [] : visiblePreviewItems.value
)
const total = computed(() =>
  props.mode === 'registered' ? props.detail?.total || 0 : previewItems.value.length
)

watch(
  () => props.selectedPackageId,
  () => {
    query.keyword = ''
    query.kind = ''
    query.readiness = ''
    query.page = 1
  }
)

function asDisplayItem(item: KnowledgePackageItem | KnowledgeImportItemResult) {
  if ('payload' in item) {
    return {
      item_id: item.item_id,
      kind: item.kind,
      readiness: item.readiness,
      action: item.runtime_action || 'registered',
      target_id: item.runtime_target_id,
      messages: item.messages || [],
      issues: item.issues || [],
      normalized: item.payload,
    } satisfies KnowledgeImportItemResult
  }
  return item
}

function openDetail(item: KnowledgePackageItem | KnowledgeImportItemResult) {
  selectedItem.value = 'payload' in item ? item : null
  detailItem.value = asDisplayItem(item)
  detailVisible.value = true
}

function submitQuery() {
  query.page = 1
  if (props.mode === 'registered') emit('query', { ...query })
}

function toggleKind(kind: string) {
  query.kind = query.kind === kind ? '' : kind
  submitQuery()
}

function changePage(page: number) {
  query.page = page
  if (props.mode === 'registered') emit('query', { ...query })
}

function changePageSize(pageSize: number) {
  query.pageSize = pageSize
  query.page = 1
  if (props.mode === 'registered') emit('query', { ...query })
}

function kindLabel(kind: string) {
  return t(`knowledge.kind_${kind}`)
}

function readinessLabel(readiness: string) {
  return t(`knowledge.readiness_${readiness}`)
}

function readinessType(readiness: string) {
  if (readiness === 'ready') return 'success'
  if (readiness === 'invalid') return 'danger'
  if (readiness === 'review_required') return 'warning'
  return 'info'
}

function readinessDescription(readiness: string) {
  return t(`knowledge.readiness_${readiness}_hint`)
}

function runtimeAction(item: KnowledgePackageItem | KnowledgeImportItemResult) {
  return 'payload' in item ? item.runtime_action || 'registered' : item.action
}

function nextStep(item: KnowledgePackageItem | KnowledgeImportItemResult) {
  const action = runtimeAction(item)
  if (action === 'staged' || action === 'candidate') return 'review'
  if (action === 'imported' || action === 'updated' || action.startsWith('kept_')) return 'complete'
  if (item.kind === 'evidence') return 'evidence'
  if (item.readiness === 'invalid') return 'repair'
  if (item.readiness === 'review_required') {
    return item.kind === 'terminology' ? 'approve_publish' : 'repair'
  }
  return 'publish'
}

function rowAction(item: KnowledgePackageItem | KnowledgeImportItemResult) {
  if (!('payload' in item)) return ''
  const step = nextStep(item)
  if (step === 'review') return 'review'
  if (step === 'approve_publish') return 'approve_publish'
  if (step === 'publish') return 'publish'
  if (step === 'repair') return 'repair'
  return ''
}

function invokeAction(item: KnowledgePackageItem, action: string) {
  detailVisible.value = false
  if (action === 'review') {
    emit('gotoReview', item)
  } else if (action === 'repair') {
    emit('openImport')
  } else if (action === 'approve_publish') emit('advance', item, 'approve_publish')
  else if (action === 'publish') emit('advance', item, 'publish')
}

function rejectSelected() {
  if (!selectedItem.value) return
  detailVisible.value = false
  emit('reject', selectedItem.value)
}

function sourceLabel(source: Record<string, unknown>) {
  return String(
    source.uri || source.path || source.name || source.source_id || source.source || '-'
  )
}

function firstIssueLabel(item: KnowledgePackageItem | KnowledgeImportItemResult) {
  const issue = asDisplayItem(item).issues[0]
  if (!issue) return '-'
  const key = issueTranslationKey(issue)
  return knowledgeIssueText(issue, te(key) ? t(key) : '')
}
</script>

<template>
  <section class="package-workbench">
    <aside class="package-sidebar">
      <div class="sidebar-heading">
        <span>{{ t('knowledge.registered_sources') }}</span>
        <el-tag type="info" round>{{ packages.length }}</el-tag>
      </div>
      <div v-if="packages.length" class="package-list">
        <button
          v-for="knowledgePackage in packages"
          :key="knowledgePackage.package_id"
          type="button"
          class="package-list-item"
          :class="{ active: knowledgePackage.package_id === selectedPackageId }"
          @click="emit('selectPackage', knowledgePackage.package_id)"
        >
          <strong>{{ knowledgePackage.title }}</strong>
          <span>{{ knowledgePackage.item_count }} {{ t('knowledge.items_unit') }}</span>
          <small>{{ knowledgePackage.package_id }} · Rev {{ knowledgePackage.revision }}</small>
        </button>
      </div>
      <el-empty v-else :description="t('knowledge.no_imported_packages')" :image-size="64" />
    </aside>

    <main v-loading="loading" class="package-content">
      <template v-if="preview || detail">
        <header class="package-header">
          <div>
            <div class="title-line">
              <h3>{{ mode === 'preview' ? t('knowledge.preview_result') : packageInfo?.title }}</h3>
              <el-tag :type="mode === 'preview' ? 'warning' : 'success'">
                {{
                  mode === 'preview'
                    ? t('knowledge.preview_result')
                    : t('knowledge.registered_source')
                }}
              </el-tag>
            </div>
            <p>{{ packageInfo?.description || t('knowledge.package_source_hint') }}</p>
            <small>{{ preview?.package_id || packageInfo?.package_id }}</small>
          </div>
          <el-popover
            v-if="detail?.sources?.length"
            placement="bottom-end"
            :width="420"
            trigger="click"
          >
            <template #reference>
              <el-button>{{ detail.sources.length }} {{ t('knowledge.sources_unit') }}</el-button>
            </template>
            <div class="source-list">
              <div v-for="source in detail.sources" :key="sourceLabel(source)">
                {{ sourceLabel(source) }}
              </div>
            </div>
          </el-popover>
        </header>

        <div class="summary-grid">
          <button
            type="button"
            class="summary-card primary"
            :class="{ selected: !query.kind }"
            @click="toggleKind('')"
          >
            <strong>{{ counts.total }}</strong
            ><span>{{ t('knowledge.total_knowledge') }}</span>
          </button>
          <button
            v-for="(count, key) in counts.kind"
            :key="String(key)"
            type="button"
            class="summary-card"
            :class="{ selected: query.kind === key }"
            @click="toggleKind(String(key))"
          >
            <strong>{{ count }}</strong
            ><span>{{ kindLabel(String(key)) }}</span>
          </button>
        </div>

        <div class="readiness-guide">
          <div v-for="(count, key) in counts.readiness" :key="String(key)">
            <el-tag :type="readinessType(String(key))" size="small">
              {{ readinessLabel(String(key)) }} · {{ count }}
            </el-tag>
            <span>{{ readinessDescription(String(key)) }}</span>
          </div>
        </div>

        <div class="knowledge-toolbar">
          <el-input
            v-model="query.keyword"
            clearable
            :placeholder="t('knowledge.search_knowledge')"
            class="search-input"
            @keyup.enter="submitQuery"
            @clear="submitQuery"
          />
          <el-select
            v-model="query.readiness"
            clearable
            :placeholder="t('knowledge.readiness')"
            @change="submitQuery"
          >
            <el-option
              v-for="(_count, key) in counts.readiness"
              :key="String(key)"
              :label="readinessLabel(String(key))"
              :value="String(key)"
            />
          </el-select>
          <span>{{ t('knowledge.filtered_items', { count: total }) }}</span>
        </div>

        <el-table :data="displayItems" size="small" class="knowledge-table" @row-click="openDetail">
          <el-table-column :label="t('knowledge.knowledge_content')" min-width="360">
            <template #default="{ row }">
              <div class="knowledge-cell">
                <strong>{{ knowledgeItemTitle(asDisplayItem(row)) }}</strong>
                <span>{{ knowledgeItemSummary(asDisplayItem(row)) || '-' }}</span>
                <small>{{ row.item_id }}</small>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('knowledge.knowledge_type')" width="110">
            <template #default="{ row }"
              ><el-tag type="info">{{ kindLabel(row.kind) }}</el-tag></template
            >
          </el-table-column>
          <el-table-column :label="t('knowledge.readiness')" width="120">
            <template #default="{ row }"
              ><el-tag :type="readinessType(row.readiness)">{{
                readinessLabel(row.readiness)
              }}</el-tag></template
            >
          </el-table-column>
          <el-table-column :label="t('knowledge.next_step')" min-width="190">
            <template #default="{ row }">{{ t(`knowledge.next_step_${nextStep(row)}`) }}</template>
          </el-table-column>
          <el-table-column :label="t('knowledge.validation_result')" min-width="240">
            <template #default="{ row }">
              <span class="issue-summary" :class="{ error: row.readiness === 'invalid' }">
                {{ firstIssueLabel(row) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column :label="t('knowledge.actions')" width="180" fixed="right">
            <template #default="{ row }">
              <el-button link @click.stop="openDetail(row)">{{ t('knowledge.details') }}</el-button>
              <el-button
                v-if="rowAction(row)"
                link
                type="primary"
                @click.stop="invokeAction(row, rowAction(row))"
              >
                {{ t(`knowledge.next_action_${rowAction(row)}`) }}
              </el-button>
            </template>
          </el-table-column>
          <template #empty
            ><el-empty :description="t('knowledge.no_matching_knowledge')" :image-size="64"
          /></template>
        </el-table>

        <el-pagination
          v-if="total > 0"
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          class="pagination"
          layout="total, sizes, prev, pager, next"
          :page-sizes="[10, 15, 30, 50]"
          :total="total"
          @current-change="changePage"
          @size-change="changePageSize"
        />
      </template>
      <el-empty v-else :description="t('knowledge.select_package_to_view')" />
    </main>

    <el-drawer
      v-model="detailVisible"
      :title="t('knowledge.knowledge_details')"
      size="min(760px, 94vw)"
      destroy-on-close
    >
      <KnowledgeItemDetail v-if="detailItem" :item="detailItem">
        <template v-if="selectedItem && rowAction(selectedItem)" #actions>
          <el-button v-if="selectedItem" type="danger" plain @click="rejectSelected">
            {{ t('knowledge.reject') }}
          </el-button>
          <el-button type="primary" @click="invokeAction(selectedItem, rowAction(selectedItem))">
            {{ t(`knowledge.next_action_${rowAction(selectedItem)}`) }}
          </el-button>
        </template>
      </KnowledgeItemDetail>
    </el-drawer>
  </section>
</template>

<style scoped>
.package-workbench {
  display: grid;
  min-height: 580px;
  overflow: hidden;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  grid-template-columns: 230px minmax(0, 1fr);
}
.package-sidebar {
  background: var(--el-fill-color-extra-light);
  border-right: 1px solid var(--el-border-color-lighter);
}
.sidebar-heading {
  display: flex;
  padding: 16px;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.package-list {
  max-height: 720px;
  padding: 8px;
  overflow: auto;
}
.package-list-item {
  display: grid;
  width: 100%;
  padding: 12px;
  margin-bottom: 5px;
  gap: 5px;
  color: var(--el-text-color-primary);
  text-align: left;
  cursor: pointer;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 7px;
}
.package-list-item:hover {
  background: var(--el-fill-color-light);
}
.package-list-item.active {
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
}
.package-list-item strong,
.package-list-item span,
.package-list-item small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.package-list-item span,
.package-list-item small {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.package-content {
  min-width: 0;
  padding: 18px;
}
.package-header {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  justify-content: space-between;
}
.title-line {
  display: flex;
  gap: 10px;
  align-items: center;
}
.title-line h3 {
  margin: 0;
  font-size: 18px;
}
.package-header p {
  max-width: 900px;
  margin: 7px 0;
  color: var(--el-text-color-secondary);
  line-height: 1.55;
}
.package-header small {
  color: var(--el-text-color-placeholder);
}
.summary-grid {
  display: flex;
  padding: 14px 0 10px;
  overflow-x: auto;
  gap: 8px;
}
.summary-card {
  display: grid;
  min-width: 92px;
  padding: 10px 14px;
  text-align: left;
  cursor: pointer;
  background: var(--el-fill-color-extra-light);
  border: 1px solid transparent;
  border-radius: 8px;
}
.summary-card.primary {
  background: var(--el-color-primary-light-9);
}
.summary-card.selected {
  border-color: var(--el-color-primary-light-5);
}
.summary-card strong {
  font-size: 20px;
}
.summary-card span {
  margin-top: 3px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.readiness-guide {
  display: grid;
  padding: 10px 12px;
  margin-bottom: 12px;
  gap: 8px 16px;
  background: var(--el-fill-color-extra-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.readiness-guide > div {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 8px;
}
.readiness-guide span {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.4;
}
.knowledge-toolbar {
  display: flex;
  margin-bottom: 12px;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.knowledge-toolbar .search-input {
  width: min(360px, 100%);
}
.knowledge-toolbar :deep(.el-select) {
  width: 150px;
}
.knowledge-cell {
  display: grid;
  gap: 5px;
  line-height: 1.45;
}
.knowledge-cell span {
  color: var(--el-text-color-regular);
}
.knowledge-cell small {
  color: var(--el-text-color-placeholder);
}
.issue-summary {
  color: var(--el-text-color-secondary);
  line-height: 1.45;
}
.issue-summary.error {
  color: var(--el-color-danger);
}
.knowledge-table :deep(.el-table__row) {
  cursor: pointer;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
.source-list {
  display: grid;
  max-height: 300px;
  overflow: auto;
  gap: 8px;
  color: var(--el-text-color-regular);
  font-size: 13px;
}
@media (max-width: 960px) {
  .package-workbench {
    grid-template-columns: 1fr;
  }
  .package-sidebar {
    border-right: 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }
  .package-list {
    display: flex;
    max-height: none;
    overflow-x: auto;
  }
  .package-list-item {
    min-width: 230px;
  }
  .readiness-guide {
    grid-template-columns: 1fr;
  }
}
</style>
