<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import type {
  KnowledgeDeployment,
  KnowledgeLifecycle,
  KnowledgeUnitSummary,
  PageResult,
} from '@/api/knowledge'
import { statusLabel, statusTagType } from '../presentation'
import { executeUnitAction, runUnitAction, type UnitAction } from '../unitActions'
import KnowledgeUnitDrawer from './KnowledgeUnitDrawer.vue'

type RuntimeDeployment = KnowledgeDeployment & {
  unit_id: number
  unit_key: string
  unit_title: string
  unit_domain: string
  revision: number
  lifecycle_status?: KnowledgeLifecycle
  datasource_id: number
  binding_status: string
}

defineProps<{ page: PageResult<RuntimeDeployment> | null; loading: boolean }>()
const emit = defineEmits<{ load: [query: { status: string; page: number; pageSize: number }] }>()
const query = reactive({ status: 'ACTIVE', page: 1, pageSize: 15 })
const drawerVisible = ref(false)
const selected = ref<KnowledgeUnitSummary | null>(null)
const selection = ref<RuntimeDeployment[]>([])
const actingKey = ref('')
const batchLoading = ref(false)

function load(reset = false) {
  if (reset) query.page = 1
  emit('load', { ...query })
}

function openDetail(row: RuntimeDeployment) {
  selected.value = {
    unit_id: row.unit_id,
    unit_key: row.unit_key,
    title: row.unit_title,
    domain: row.unit_domain,
    revision_id: row.revision_id,
    revision: row.revision,
    lifecycle_status: row.lifecycle_status || 'PUBLISHED',
    validation_status: 'PASS',
    binding_status: row.binding_status as KnowledgeUnitSummary['binding_status'],
    deployment_status: row.status,
    confidence: 1,
    next_step: row.binding_status === 'STALE' ? 'REVALIDATE' : 'VIEW_RUNTIME',
    update_time: row.update_time,
  }
  drawerVisible.value = true
}

function rowKey(row: RuntimeDeployment) {
  return `${row.unit_id}:${row.revision}`
}

function runtimeActions(row: RuntimeDeployment): { action: UnitAction; label: string }[] {
  if (row.status === 'ACTIVE') return [{ action: 'unpublish', label: '撤销发布' }]
  if (row.status === 'RETIRED' || row.status === 'ERROR') {
    return [{ action: 'publish', label: '重新发布' }]
  }
  return []
}

async function runRowAction(row: RuntimeDeployment, action: UnitAction) {
  actingKey.value = rowKey(row)
  try {
    const ok = await runUnitAction(row.unit_id, row.revision, action)
    if (ok) load()
  } finally {
    actingKey.value = ''
  }
}

function onSelectionChange(rows: RuntimeDeployment[]) {
  selection.value = rows
}

function onRowClick(row: RuntimeDeployment, column: { type?: string }) {
  if (column.type === 'selection') return
  openDetail(row)
}

async function runBatch(action: UnitAction) {
  const applicable = selection.value.filter((row) =>
    runtimeActions(row).some((item) => item.action === action)
  )
  if (!applicable.length) {
    ElMessage.warning('所选部署当前状态均不支持该操作')
    return
  }
  if (action === 'unpublish') {
    try {
      await ElMessageBox.confirm(
        '撤销发布后，选中的 ' + applicable.length + ' 个部署将不再被问数召回。',
        '批量撤销发布',
        { type: 'warning', confirmButtonText: '撤销发布', cancelButtonText: '取消' }
      )
    } catch {
      return
    }
  }
  batchLoading.value = true
  let success = 0
  let failed = 0
  try {
    for (const row of applicable) {
      try {
        await executeUnitAction(row.unit_id, row.revision, action)
        success += 1
      } catch {
        failed += 1
      }
    }
  } finally {
    batchLoading.value = false
  }
  const label = action === 'publish' ? '重新发布' : '撤销发布'
  if (failed) {
    ElMessage.warning('批量' + label + '：成功 ' + success + ' 项，失败 ' + failed + ' 项')
  } else {
    ElMessage.success('批量' + label + '完成：' + success + ' 项')
  }
  if (success) {
    selection.value = []
    load()
  }
}
</script>

<template>
  <section class="runtime-list">
    <header class="hero">
      <div>
        <h3>运行时知识</h3>
        <p>这里只展示已发布的知识单元部署。过期绑定仍可被问数召回，页面会标出 STALE。</p>
      </div>
      <el-tag type="success" round>{{ page?.total || 0 }} 个部署</el-tag>
    </header>

    <div class="toolbar">
      <el-select v-model="query.status" clearable placeholder="部署状态" @change="load(true)">
        <el-option label="已激活" value="ACTIVE" />
        <el-option label="构建失败" value="ERROR" />
        <el-option label="已退役" value="RETIRED" />
      </el-select>
    </div>

    <div v-if="selection.length" class="batch-bar">
      <span class="batch-count">已选 {{ selection.length }} 项</span>
      <el-button
        type="warning"
        plain
        size="small"
        :loading="batchLoading"
        @click="runBatch('unpublish')"
      >
        批量撤销发布
      </el-button>
      <el-button type="primary" size="small" :loading="batchLoading" @click="runBatch('publish')">
        批量重新发布
      </el-button>
      <el-button size="small" :disabled="batchLoading" @click="selection = []">清除选择</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="page?.items || []"
      :row-key="rowKey"
      @row-click="onRowClick"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="46" />
      <el-table-column label="知识单元" min-width="320">
        <template #default="{ row }">
          <div class="unit-cell">
            <strong>{{ row.unit_title }}</strong>
            <span>{{ row.unit_domain }} · {{ row.unit_key }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Revision" width="100" prop="revision" />
      <el-table-column label="数据源" width="100" prop="datasource_id" />
      <el-table-column label="绑定" width="130">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.binding_status)">{{
            statusLabel(row.binding_status)
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="部署状态" width="120">
        <template #default="{ row }"
          ><el-tag :type="statusTagType(row.status)">{{
            statusLabel(row.status)
          }}</el-tag></template
        >
      </el-table-column>
      <el-table-column label="运行时投影" min-width="240">
        <template #default="{ row }">
          <div class="projection-tags">
            <el-tag
              v-for="(ids, key) in row.projection_manifest"
              :key="key"
              size="small"
              type="info"
            >
              {{ key }} · {{ Array.isArray(ids) ? ids.length : 1 }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="错误" min-width="220" show-overflow-tooltip prop="error" />
      <el-table-column label="操作" min-width="200" fixed="right">
        <template #default="{ row }">
          <div class="row-actions">
            <el-button
              v-for="item in runtimeActions(row)"
              :key="item.action"
              size="small"
              :type="item.action === 'publish' ? 'primary' : 'warning'"
              plain
              :loading="actingKey === rowKey(row)"
              @click.stop="runRowAction(row, item.action)"
            >
              {{ item.label }}
            </el-button>
            <el-button size="small" @click.stop="openDetail(row)">详情</el-button>
          </div>
        </template>
      </el-table-column>
      <template #empty><el-empty description="暂无运行时知识部署" :image-size="72" /></template>
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

    <KnowledgeUnitDrawer
      v-model="drawerVisible"
      mode="runtime"
      :item="selected"
      @changed="load()"
    />
  </section>
</template>

<style scoped>
.runtime-list {
  padding-bottom: 24px;
}
.hero {
  display: flex;
  padding: 18px;
  margin-bottom: 14px;
  align-items: flex-start;
  justify-content: space-between;
  background: linear-gradient(135deg, var(--el-color-success-light-9), var(--el-bg-color));
  border: 1px solid var(--el-color-success-light-8);
  border-radius: 10px;
}
.hero h3 {
  margin: 0;
}
.hero p {
  margin: 7px 0 0;
  color: var(--el-text-color-secondary);
}
.toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}
.toolbar .el-select {
  width: 180px;
}
.batch-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
  background: var(--el-color-success-light-9);
  border: 1px solid var(--el-color-success-light-8);
  border-radius: 8px;
  flex-wrap: wrap;
}
.batch-count {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-color-success);
  margin-right: 4px;
}
.row-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.unit-cell {
  display: grid;
  gap: 5px;
}
.unit-cell span {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.projection-tags {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}
.pagination {
  justify-content: flex-end;
  margin-top: 14px;
}
.deployment-detail pre {
  padding: 12px;
  overflow: auto;
  line-height: 1.55;
  white-space: pre-wrap;
  background: var(--el-fill-color-extra-light);
  border-radius: 7px;
}
</style>
