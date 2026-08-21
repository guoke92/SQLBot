<script lang="ts" setup>
import { computed, reactive, ref } from 'vue'
import type { KnowledgeUnitPage, KnowledgeUnitSummary } from '@/api/knowledge'
import { statusLabel, statusTagType } from '../presentation'
import {
  ACTION_LABELS,
  actionsForLifecycle,
  batchUnitActions,
  runUnitAction,
  type UnitAction,
} from '../unitActions'
import KnowledgeUnitDrawer from './KnowledgeUnitDrawer.vue'
import ValidationIssueList from './ValidationIssueList.vue'

const lifecycleTabs = [
  { id: 'IN_REVIEW', label: '待审核' },
  { id: 'APPROVED', label: '已批准' },
  { id: 'REJECTED', label: '已拒绝' },
  { id: 'DRAFT', label: '草稿' },
  { id: 'PUBLISHED', label: '已发布' },
  { id: 'RETIRED', label: '已退役' },
] as const

const props = defineProps<{ page: KnowledgeUnitPage | null; loading: boolean }>()
const emit = defineEmits<{
  load: [
    query: {
      keyword: string
      lifecycle: string
      validation: string
      page: number
      pageSize: number
    },
  ]
}>()

const query = reactive({
  keyword: '',
  lifecycle: 'IN_REVIEW',
  validation: '',
  page: 1,
  pageSize: 15,
})
const drawerVisible = ref(false)
const selected = ref<KnowledgeUnitSummary | null>(null)
const selection = ref<KnowledgeUnitSummary[]>([])
const actingKey = ref('')
const batchLoading = ref(false)
const groupedItems = computed(() =>
  [...(props.page?.items || [])].sort(
    (left, right) =>
      left.domain.localeCompare(right.domain, 'zh-CN') ||
      left.title.localeCompare(right.title, 'zh-CN')
  )
)
const currentTab = computed(
  () => lifecycleTabs.find((item) => item.id === query.lifecycle) || lifecycleTabs[0]
)
const emptyHint = computed(() => `当前没有${currentTab.value.label}的知识单元`)

function lifecycleCount(status: string) {
  return Number(props.page?.lifecycle_counts?.[status] || 0)
}

function domainSpan({
  columnIndex,
  rowIndex,
}: {
  columnIndex: number
  rowIndex: number
  row: KnowledgeUnitSummary
}) {
  if (columnIndex !== 1) return
  const items = groupedItems.value
  const domain = items[rowIndex]?.domain
  if (rowIndex > 0 && items[rowIndex - 1]?.domain === domain) return [0, 0]
  let rowspan = 1
  while (rowIndex + rowspan < items.length && items[rowIndex + rowspan].domain === domain) {
    rowspan += 1
  }
  return [rowspan, 1]
}

function load(reset = false) {
  if (reset) query.page = 1
  emit('load', { ...query })
}

function selectLifecycle(status: string) {
  if (query.lifecycle === status) return
  query.lifecycle = status
  load(true)
}

function open(item: KnowledgeUnitSummary) {
  selected.value = item
  drawerVisible.value = true
}

function onRowClick(row: KnowledgeUnitSummary, column: { type?: string }) {
  if (column.type === 'selection') return
  open(row)
}

function rowActions(row: KnowledgeUnitSummary): UnitAction[] {
  return actionsForLifecycle(row.lifecycle_status)
}

function actionLabel(row: KnowledgeUnitSummary, action: UnitAction) {
  if (action === 'publish') {
    return row.lifecycle_status === 'RETIRED' ? '重新发布' : '发布'
  }
  return ACTION_LABELS[action]
}

async function runRowAction(row: KnowledgeUnitSummary, action: UnitAction) {
  const key = `${row.unit_id}:${row.revision}`
  actingKey.value = key
  try {
    const ok = await runUnitAction(row.unit_id, row.revision, action)
    if (ok) load()
  } finally {
    actingKey.value = ''
  }
}

function onSelectionChange(rows: KnowledgeUnitSummary[]) {
  selection.value = rows
}

function rowKey(row: KnowledgeUnitSummary) {
  return `${row.unit_id}:${row.revision}`
}

type ElButtonType = 'primary' | 'success' | 'warning' | 'info' | 'danger'

const ACTION_BUTTON_TYPE: Record<UnitAction, ElButtonType> = {
  approve: 'success',
  publish: 'primary',
  unpublish: 'warning',
  reject: 'danger',
  request: 'info',
}

function actionButtonType(action: UnitAction): ElButtonType {
  return ACTION_BUTTON_TYPE[action]
}

async function runBatch(action: UnitAction) {
  if (!selection.value.length) return
  batchLoading.value = true
  try {
    const outcome = await batchUnitActions(selection.value, action)
    if (outcome.success) {
      selection.value = []
      load()
    }
  } finally {
    batchLoading.value = false
  }
}
</script>

<template>
  <section class="review-center">
    <header class="hero">
      <div>
        <h3>知识审核中心</h3>
        <p>以完整业务知识单元为审核对象，在同一处核对流程、数据、口径、查询和证据。</p>
      </div>
      <el-tag :type="statusTagType(query.lifecycle)" round>
        {{ lifecycleCount(query.lifecycle) }} {{ currentTab.label }}
      </el-tag>
    </header>

    <div class="status-tabs">
      <button
        v-for="tab in lifecycleTabs"
        :key="tab.id"
        type="button"
        :class="{ active: query.lifecycle === tab.id }"
        @click="selectLifecycle(tab.id)"
      >
        <span>{{ tab.label }}</span>
        <strong>{{ lifecycleCount(tab.id) }}</strong>
      </button>
    </div>

    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        clearable
        placeholder="搜索知识单元、领域或标识"
        @keyup.enter="load(true)"
        @clear="load(true)"
      />
      <el-select v-model="query.validation" clearable placeholder="校验状态" @change="load(true)">
        <el-option label="通过" value="PASS" />
        <el-option label="警告" value="WARNING" />
        <el-option label="失败" value="FAIL" />
        <el-option label="未校验" value="NOT_RUN" />
      </el-select>
    </div>

    <div v-if="selection.length" class="batch-bar">
      <span class="batch-count">已选 {{ selection.length }} 项</span>
      <el-button
        type="primary"
        plain
        size="small"
        :loading="batchLoading"
        @click="runBatch('approve')"
      >
        批量批准
      </el-button>
      <el-button type="primary" size="small" :loading="batchLoading" @click="runBatch('publish')">
        批量发布
      </el-button>
      <el-button
        type="warning"
        plain
        size="small"
        :loading="batchLoading"
        @click="runBatch('unpublish')"
      >
        批量撤销发布
      </el-button>
      <el-button
        type="danger"
        plain
        size="small"
        :loading="batchLoading"
        @click="runBatch('reject')"
      >
        批量拒绝
      </el-button>
      <el-button size="small" :disabled="batchLoading" @click="selection = []">清除选择</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="groupedItems"
      :row-key="rowKey"
      :span-method="domainSpan"
      @row-click="onRowClick"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="46" />
      <el-table-column label="业务域" width="140">
        <template #default="{ row }">
          <strong>{{ row.domain }}</strong>
        </template>
      </el-table-column>
      <el-table-column label="业务知识单元" min-width="320">
        <template #default="{ row }">
          <div class="unit-cell">
            <strong>{{ row.title }}</strong>
            <span>{{ row.domain }} · {{ row.unit_key }}</span>
            <small
              >Revision {{ row.revision }} · 置信度 {{ Math.round(row.confidence * 100) }}%</small
            >
          </div>
        </template>
      </el-table-column>
      <el-table-column label="生命周期" width="130">
        <template #default="{ row }"
          ><el-tag :type="statusTagType(row.lifecycle_status)">{{
            statusLabel(row.lifecycle_status)
          }}</el-tag></template
        >
      </el-table-column>
      <el-table-column label="校验" min-width="220">
        <template #default="{ row }">
          <el-popover
            v-if="row.validation_issue_count"
            placement="left"
            :width="420"
            trigger="hover"
          >
            <ValidationIssueList
              compact
              :status="row.validation_status"
              :summary="row.validation_summary_text"
              :issues="row.validation_issues"
            />
            <template #reference>
              <div class="validation-tags">
                <el-tag v-if="row.validation_error_count" type="danger">
                  失败 {{ row.validation_error_count }}
                </el-tag>
                <el-tag v-if="row.validation_warning_count" type="warning">
                  告警 {{ row.validation_warning_count }}
                </el-tag>
                <el-tag
                  v-if="!row.validation_error_count && !row.validation_warning_count"
                  :type="statusTagType(row.validation_status)"
                >
                  {{ statusLabel(row.validation_status) }}
                  <template v-if="row.validation_issue_count">
                    · {{ row.validation_issue_count }}
                  </template>
                </el-tag>
              </div>
            </template>
          </el-popover>
          <el-tag v-else :type="statusTagType(row.validation_status)">{{
            statusLabel(row.validation_status)
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="数据绑定" width="120">
        <template #default="{ row }">{{ statusLabel(row.binding_status) }}</template>
      </el-table-column>
      <el-table-column label="操作" min-width="280">
        <template #default="{ row }">
          <div class="row-actions">
            <el-button
              v-for="action in rowActions(row)"
              :key="action"
              size="small"
              :type="actionButtonType(action)"
              :plain="action === 'request' || action === 'unpublish'"
              :loading="actingKey === rowKey(row)"
              @click.stop="runRowAction(row, action)"
            >
              {{ actionLabel(row, action) }}
            </el-button>
            <el-button size="small" @click.stop="open(row)">详情</el-button>
          </div>
        </template>
      </el-table-column>
      <template #empty><el-empty :description="emptyHint" :image-size="72" /></template>
    </el-table>

    <el-pagination
      v-if="page?.total"
      v-model:current-page="query.page"
      v-model:page-size="query.pageSize"
      class="pagination"
      layout="total, sizes, prev, pager, next"
      :page-sizes="[10, 15, 30, 50]"
      :total="page.total"
      @current-change="load()"
      @size-change="load(true)"
    />

    <KnowledgeUnitDrawer v-model="drawerVisible" mode="review" :item="selected" @changed="load()" />
  </section>
</template>

<style scoped>
.review-center {
  padding-bottom: 24px;
}
.hero {
  display: flex;
  padding: 18px;
  margin-bottom: 14px;
  align-items: flex-start;
  justify-content: space-between;
  background: linear-gradient(135deg, var(--el-color-primary-light-9), var(--el-bg-color));
  border: 1px solid var(--el-color-primary-light-8);
  border-radius: 10px;
}
.hero h3 {
  margin: 0;
}
.hero p {
  margin: 7px 0 0;
  color: var(--el-text-color-secondary);
}
.status-tabs {
  display: flex;
  margin-bottom: 14px;
  gap: 8px;
  overflow: auto;
}
.status-tabs button {
  display: flex;
  min-width: 108px;
  padding: 10px 14px;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  cursor: pointer;
  background: var(--el-fill-color-extra-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
}
.status-tabs button.active {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary);
}
.status-tabs span {
  font-size: 13px;
}
.status-tabs strong {
  font-size: 18px;
}
.toolbar {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 180px;
  gap: 10px;
  margin-bottom: 12px;
}
.unit-cell {
  display: grid;
  gap: 5px;
}
.unit-cell span,
.unit-cell small {
  color: var(--el-text-color-secondary);
}
.pagination {
  justify-content: flex-end;
  margin-top: 14px;
}
.validation-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.batch-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
  background: var(--el-color-primary-light-9);
  border: 1px solid var(--el-color-primary-light-7);
  border-radius: 8px;
  flex-wrap: wrap;
}
.batch-count {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-color-primary);
  margin-right: 4px;
}
.row-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
@media (max-width: 700px) {
  .toolbar {
    grid-template-columns: 1fr;
  }
  .hero {
    gap: 10px;
  }
}
</style>
