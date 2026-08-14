<script lang="ts" setup>
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type {
  KnowledgeImportItemResult,
  RuntimeKnowledgeItem,
  RuntimeKnowledgePage,
} from '@/api/knowledge'
import { formatTimestamp } from '@/utils/date'
import KnowledgeItemDetail from './KnowledgeItemDetail.vue'

const props = defineProps<{ page: RuntimeKnowledgePage | null; loading: boolean }>()
const emit = defineEmits<{
  load: [
    query: { keyword: string; kind: string; enabled?: boolean; page: number; pageSize: number },
  ]
  disable: [item: RuntimeKnowledgeItem]
  demote: [item: RuntimeKnowledgeItem]
}>()
const { t } = useI18n()
const query = reactive({
  keyword: '',
  kind: '',
  enabled: '' as '' | 'true' | 'false',
  page: 1,
  pageSize: 15,
})
const detailVisible = ref(false)
const selected = ref<RuntimeKnowledgeItem | null>(null)
const kinds = computed(() => props.page?.kind_counts || {})

function requestQuery() {
  return {
    keyword: query.keyword,
    kind: query.kind,
    enabled: query.enabled === '' ? undefined : query.enabled === 'true',
    page: query.page,
    pageSize: query.pageSize,
  }
}

function search() {
  query.page = 1
  emit('load', requestQuery())
}

function toggleKind(kind: string) {
  query.kind = query.kind === kind ? '' : kind
  search()
}

function pageChange(page: number) {
  query.page = page
  emit('load', requestQuery())
}

function sizeChange(pageSize: number) {
  query.page = 1
  query.pageSize = pageSize
  emit('load', requestQuery())
}

function kindLabel(kind: string) {
  return t(`knowledge.kind_${kind}`)
}

function displayItem(item: RuntimeKnowledgeItem): KnowledgeImportItemResult {
  return {
    item_id: `${item.kind}:${item.id}`,
    kind: item.kind,
    readiness: 'ready',
    action: item.enabled ? 'published' : 'disabled',
    target_id: item.id,
    messages: [],
    issues: [],
    normalized: { ...item.payload, label: item.label, summary: item.summary },
  }
}

function openDetail(item: RuntimeKnowledgeItem) {
  selected.value = item
  detailVisible.value = true
}
</script>

<template>
  <section class="runtime-list">
    <header class="section-header">
      <div>
        <h3>{{ t('knowledge.runtime_title') }}</h3>
        <p>{{ t('knowledge.runtime_subtitle') }}</p>
      </div>
      <el-tag type="success" round>{{ page?.total || 0 }}</el-tag>
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
        :placeholder="t('knowledge.search_runtime')"
        @keyup.enter="search"
        @clear="search"
      />
      <el-select
        v-model="query.kind"
        clearable
        :placeholder="t('knowledge.knowledge_type')"
        @change="search"
      >
        <el-option
          v-for="(_count, kind) in kinds"
          :key="String(kind)"
          :label="kindLabel(String(kind))"
          :value="String(kind)"
        />
      </el-select>
      <el-select
        v-model="query.enabled"
        clearable
        :placeholder="t('knowledge.runtime_status')"
        @change="search"
      >
        <el-option :label="t('knowledge.enabled')" value="true" />
        <el-option :label="t('knowledge.disabled')" value="false" />
      </el-select>
    </div>

    <el-table v-loading="loading" :data="page?.items || []" size="small" @row-click="openDetail">
      <el-table-column :label="t('knowledge.knowledge_content')" min-width="380">
        <template #default="{ row }">
          <div class="content-cell">
            <strong>{{ row.label }}</strong
            ><span>{{ row.summary || '-' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="t('knowledge.knowledge_type')" width="110">
        <template #default="{ row }"
          ><el-tag type="info">{{ kindLabel(row.kind) }}</el-tag></template
        >
      </el-table-column>
      <el-table-column :label="t('knowledge.trust_tier')" width="110">
        <template #default="{ row }"
          ><el-tag>{{ row.trust_tier }}</el-tag></template
        >
      </el-table-column>
      <el-table-column :label="t('knowledge.runtime_status')" width="100">
        <template #default="{ row }"
          ><el-tag :type="row.enabled ? 'success' : 'info'">{{
            row.enabled ? t('knowledge.enabled') : t('knowledge.disabled')
          }}</el-tag></template
        >
      </el-table-column>
      <el-table-column :label="t('knowledge.runtime_source')" width="140" prop="source" />
      <el-table-column :label="t('knowledge.created')" width="160">
        <template #default="{ row }">{{
          row.create_time ? formatTimestamp(row.create_time) : '-'
        }}</template>
      </el-table-column>
      <el-table-column :label="t('knowledge.actions')" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link @click.stop="openDetail(row)">{{ t('knowledge.details') }}</el-button>
          <el-button v-if="row.kind === 'caliber'" link @click.stop="emit('demote', row)">{{
            t('knowledge.demote')
          }}</el-button>
          <el-button
            v-if="row.enabled && ['caliber', 'rule'].includes(row.kind)"
            link
            type="danger"
            @click.stop="emit('disable', row)"
            >{{ t('knowledge.disable') }}</el-button
          >
        </template>
      </el-table-column>
      <template #empty
        ><el-empty :description="t('knowledge.no_runtime')" :image-size="72"
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

    <el-drawer
      v-model="detailVisible"
      :title="t('knowledge.knowledge_details')"
      size="min(760px, 94vw)"
      destroy-on-close
    >
      <KnowledgeItemDetail v-if="selected" :item="displayItem(selected)" />
    </el-drawer>
  </section>
</template>

<style scoped>
.runtime-list {
  padding: 2px 0 24px;
}
.section-header {
  display: flex;
  padding: 16px 18px;
  margin-bottom: 14px;
  align-items: flex-start;
  justify-content: space-between;
  background: linear-gradient(135deg, var(--el-color-success-light-9), var(--el-bg-color));
  border: 1px solid var(--el-color-success-light-8);
  border-radius: 10px;
}
.section-header h3 {
  margin: 0;
}
.section-header p {
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
  width: 360px;
}
.toolbar :deep(.el-select) {
  width: 160px;
}
.content-cell {
  display: grid;
  gap: 5px;
  line-height: 1.45;
}
.content-cell span {
  color: var(--el-text-color-regular);
}
:deep(.el-table__row) {
  cursor: pointer;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
