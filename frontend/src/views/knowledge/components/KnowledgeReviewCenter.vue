<script lang="ts" setup>
import { MoreFilled } from '@element-plus/icons-vue'
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type {
  KnowledgeImportItemResult,
  KnowledgeReviewItem,
  KnowledgeReviewPage,
  KnowledgeSuggestion,
} from '@/api/knowledge'
import KnowledgeItemDetail from './KnowledgeItemDetail.vue'
import { knowledgeItemSummary, knowledgeItemTitle } from '../presentation'

const props = defineProps<{
  page: KnowledgeReviewPage | null
  suggestions: KnowledgeSuggestion[]
  loading: boolean
}>()
const emit = defineEmits<{
  load: [query: { keyword: string; kind: string; page: number; pageSize: number }]
  approve: [item: KnowledgeReviewItem]
  reject: [item: KnowledgeReviewItem]
  promote: [item: KnowledgeSuggestion]
}>()
const { t } = useI18n()
const query = reactive({ keyword: '', kind: '', page: 1, pageSize: 15 })
const detailVisible = ref(false)
const selected = ref<KnowledgeReviewItem | null>(null)

const kinds = computed(() => props.page?.kind_counts || {})

function displayItem(item: KnowledgeReviewItem): KnowledgeImportItemResult {
  return {
    item_id: item.item_id || item.review_key,
    kind: item.kind,
    readiness: 'review_required',
    action: item.status,
    target_id: item.id,
    messages: [],
    issues: item.issues || [],
    normalized: {
      ...item.payload,
      provenance: item.provenance,
      quality_snapshot: item.quality_snapshot,
    },
  }
}

function sourceLabel(item: KnowledgeReviewItem) {
  if (item.source === 'package') return t('knowledge.source_package')
  if (item.source === 'relation') return t('knowledge.source_relation')
  return t('knowledge.source_staging')
}

function kindLabel(kind: string) {
  return t(`knowledge.kind_${kind}`)
}

function statusLabel(item: KnowledgeReviewItem) {
  if (item.source === 'relation') return t('knowledge.review_status_relation_candidate')
  if (item.source === 'package') return t('knowledge.readiness_review_required')
  return t('knowledge.review_status_pending_certification')
}

function approveLabel(item: KnowledgeReviewItem) {
  if (item.source === 'relation') return t('knowledge.review_action_confirm_relation')
  if (item.source === 'package') return t('knowledge.next_action_approve_publish')
  return t('knowledge.review_action_certify_publish')
}

function approve(item: KnowledgeReviewItem) {
  detailVisible.value = false
  emit('approve', item)
}

function reject(item: KnowledgeReviewItem) {
  detailVisible.value = false
  emit('reject', item)
}

function search() {
  query.page = 1
  emit('load', { ...query })
}

function toggleKind(kind: string) {
  query.kind = query.kind === kind ? '' : kind
  search()
}

function pageChange(page: number) {
  query.page = page
  emit('load', { ...query })
}

function sizeChange(pageSize: number) {
  query.page = 1
  query.pageSize = pageSize
  emit('load', { ...query })
}

function openDetail(item: KnowledgeReviewItem) {
  selected.value = item
  detailVisible.value = true
}
</script>

<template>
  <section class="review-center">
    <header class="section-header">
      <div>
        <h3>{{ t('knowledge.review_center_title') }}</h3>
        <p>{{ t('knowledge.review_center_subtitle') }}</p>
      </div>
      <el-tag type="warning" round>{{ page?.total || 0 }}</el-tag>
    </header>

    <div v-if="Object.keys(kinds).length" class="count-strip">
      <button
        v-for="(count, kind) in kinds"
        :key="String(kind)"
        type="button"
        :class="{ active: query.kind === kind }"
        @click="toggleKind(String(kind))"
      >
        <strong>{{ count }}</strong
        ><span>{{ kindLabel(String(kind)) }}</span>
      </button>
    </div>

    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        clearable
        :placeholder="t('knowledge.search_reviews')"
        @keyup.enter="search"
        @clear="search"
      />
      <el-button v-if="query.kind" @click="toggleKind(query.kind)">
        {{ t('knowledge.clear_type_filter') }}
      </el-button>
    </div>

    <el-table v-loading="loading" :data="page?.items || []" size="small" @row-click="openDetail">
      <el-table-column :label="t('knowledge.knowledge_content')" min-width="400">
        <template #default="{ row }">
          <div class="content-cell">
            <strong>{{ knowledgeItemTitle(displayItem(row)) }}</strong>
            <span>{{ knowledgeItemSummary(displayItem(row)) || '-' }}</span>
            <small>{{ row.item_id || row.review_key }}</small>
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="t('knowledge.knowledge_type')" width="110">
        <template #default="{ row }"
          ><el-tag type="info">{{ kindLabel(row.kind) }}</el-tag></template
        >
      </el-table-column>
      <el-table-column :label="t('knowledge.review_source')" width="120">
        <template #default="{ row }">{{ sourceLabel(row) }}</template>
      </el-table-column>
      <el-table-column :label="t('knowledge.status')" width="120">
        <template #default="{ row }"
          ><el-tag type="warning">{{ statusLabel(row) }}</el-tag></template
        >
      </el-table-column>
      <el-table-column :label="t('knowledge.actions')" width="250" fixed="right">
        <template #default="{ row }">
          <div class="row-actions" @click.stop>
            <el-button size="small" @click="openDetail(row)">
              {{ t('knowledge.view_details') }}
            </el-button>
            <el-button type="primary" size="small" @click="approve(row)">
              {{ approveLabel(row) }}
            </el-button>
            <el-dropdown trigger="click" @command="reject(row)">
              <el-button :icon="MoreFilled" circle size="small" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="reject">
                    {{ t('knowledge.reject') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
      </el-table-column>
      <template #empty
        ><el-empty :description="t('knowledge.no_reviews')" :image-size="72"
      /></template>
    </el-table>

    <el-pagination
      v-if="page?.total"
      v-model:current-page="query.page"
      v-model:page-size="query.pageSize"
      class="pagination"
      layout="total, sizes, prev, pager, next"
      :page-sizes="[10, 15, 30, 50]"
      :total="page.total"
      @current-change="pageChange"
      @size-change="sizeChange"
    />

    <section v-if="suggestions.length" class="suggestions">
      <div class="suggestion-heading">
        <div>
          <h4>{{ t('knowledge.suggestions') }}</h4>
          <p>{{ t('knowledge.promotion_suggestions_hint') }}</p>
        </div>
      </div>
      <div class="suggestion-list">
        <div v-for="item in suggestions" :key="item.id" class="suggestion-card">
          <div>
            <strong>{{ item.label }}</strong
            ><span>{{ item.trust_tier }}</span>
          </div>
          <small>
            {{ t('knowledge.reproductions') }} {{ item.reproduce_count }} ·
            {{ t('knowledge.applies') }} {{ item.successful_apply_count }} ·
            {{ t('knowledge.positive') }} {{ item.positive_feedback_count }}
          </small>
          <el-button
            v-if="item.recommended_action === 'promote'"
            type="primary"
            size="small"
            @click="emit('promote', item)"
            >{{ t('knowledge.promote') }}</el-button
          >
          <el-tag v-else type="danger">{{ t('knowledge.needs_review') }}</el-tag>
        </div>
      </div>
    </section>

    <el-drawer
      v-model="detailVisible"
      :title="t('knowledge.review_details')"
      size="min(760px, 94vw)"
      destroy-on-close
    >
      <KnowledgeItemDetail v-if="selected" :item="displayItem(selected)">
        <template #actions>
          <el-button type="danger" plain @click="reject(selected)">{{
            t('knowledge.reject')
          }}</el-button>
          <el-button type="primary" @click="approve(selected)">
            {{ approveLabel(selected) }}
          </el-button>
        </template>
      </KnowledgeItemDetail>
    </el-drawer>
  </section>
</template>

<style scoped>
.review-center {
  padding: 2px 0 24px;
}
.section-header {
  display: flex;
  padding: 16px 18px;
  margin-bottom: 14px;
  align-items: flex-start;
  justify-content: space-between;
  background: linear-gradient(135deg, var(--el-color-primary-light-9), var(--el-bg-color));
  border: 1px solid var(--el-color-primary-light-8);
  border-radius: 10px;
}
.section-header h3,
.suggestion-heading h4 {
  margin: 0;
}
.section-header p,
.suggestion-heading p {
  margin: 6px 0 0;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}
.count-strip {
  display: flex;
  margin-bottom: 12px;
  overflow-x: auto;
  gap: 8px;
}
.count-strip button {
  display: flex;
  min-width: 110px;
  padding: 9px 12px;
  align-items: baseline;
  gap: 7px;
  cursor: pointer;
  background: var(--el-fill-color-extra-light);
  border: 1px solid transparent;
  border-radius: 7px;
}
.count-strip button.active {
  border-color: var(--el-color-primary-light-5);
}
.count-strip span {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.toolbar {
  display: flex;
  margin-bottom: 12px;
  gap: 10px;
}
.toolbar :deep(.el-input) {
  width: min(460px, 100%);
}
.content-cell {
  display: grid;
  gap: 5px;
  line-height: 1.45;
}
.content-cell span {
  color: var(--el-text-color-regular);
}
.content-cell small {
  color: var(--el-text-color-placeholder);
}
:deep(.el-table__row) {
  cursor: pointer;
}
.row-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}
.row-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
.suggestions {
  margin-top: 26px;
}
.suggestion-list {
  display: grid;
  margin-top: 12px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 10px;
}
.suggestion-card {
  display: grid;
  padding: 14px;
  align-items: center;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px 14px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
}
.suggestion-card div {
  display: grid;
  gap: 3px;
}
.suggestion-card span,
.suggestion-card small {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.suggestion-card small {
  grid-column: 1;
}
</style>
