<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { knowledgeApi } from '@/api/knowledge'
import { statusLabel } from '../presentation'

interface ConflictRow {
  id: number
  node_id: number
  node_kind: string | null
  natural_key: string | null
  claim: Record<string, any>
  status: string
  create_time: string
}

interface NodeRow {
  id: number
  node_kind: string
  natural_key: string
  namespace: string
  status: string
  stub: boolean
  version: number | null
  update_time: string
}

interface InboxRow {
  id: number
  kind: string
  trigger_id: string
  source_record_id: number | null
  suggested_trust_tier: string | null
  payload: Record<string, any>
  create_time: string
  promotable: boolean
}

const conflictQuery = reactive({ status: 'open', page: 1, pageSize: 20 })
const nodeQuery = reactive({ keyword: '', node_kind: '', page: 1, pageSize: 20 })
const conflicts = ref<ConflictRow[]>([])
const conflictTotal = ref(0)
const nodes = ref<NodeRow[]>([])
const nodeTotal = ref(0)
const loadingConflicts = ref(false)
const loadingNodes = ref(false)

const nodeDetail = ref<Record<string, any> | null>(null)
const nodeImpact = ref<Record<string, any> | null>(null)
const editingPayload = ref('')
const nodeDrawerVisible = ref(false)

const inbox = ref<InboxRow[]>([])
const loadingInbox = ref(false)

async function loadInbox() {
  loadingInbox.value = true
  try {
    const res: any = await knowledgeApi.getInbox({ limit: 100 })
    inbox.value = res?.items || []
  } finally {
    loadingInbox.value = false
  }
}

async function rejectCandidate(row: InboxRow) {
  try {
    await knowledgeApi.rejectInbox(row.id, '运营否决')
    ElMessage.success('已拒绝候选')
    await loadInbox()
  } catch (error: any) {
    ElMessage.error(error?.message || '拒绝失败')
  }
}

async function promoteCandidate(row: InboxRow) {
  try {
    const res: any = await knowledgeApi.promoteInbox(row.id)
    ElMessage.success(`已晋升为节点 v${res?.node_version}：${res?.natural_key}`)
    await loadInbox()
  } catch (error: any) {
    ElMessage.error(error?.message || '晋升失败')
  }
}

async function loadConflicts() {
  loadingConflicts.value = true
  try {
    const res: any = await knowledgeApi.getMergeConflicts({ status: conflictQuery.status })
    conflicts.value = res?.items || []
    conflictTotal.value = conflicts.value.length
  } finally {
    loadingConflicts.value = false
  }
}

async function loadNodes() {
  loadingNodes.value = true
  try {
    const res: any = await knowledgeApi.listNodes({
      keyword: nodeQuery.keyword || undefined,
      node_kind: nodeQuery.node_kind || undefined,
      page: nodeQuery.page,
      page_size: nodeQuery.pageSize,
    })
    nodes.value = res?.items || []
    nodeTotal.value = res?.total || 0
  } finally {
    loadingNodes.value = false
  }
}

function searchNodes() {
  nodeQuery.page = 1
  void loadNodes()
}

async function resolve(conflict: ConflictRow, action: 'keep_existing' | 'accept_claim') {
  try {
    const res: any = await knowledgeApi.resolveMergeConflict(conflict.id, action)
    ElMessage.success(
      res?.node_changed
        ? `已按新声明更新节点，${(res?.affected_compositions || []).length} 个组合待复验`
        : '已保留既有声明'
    )
    await loadConflicts()
  } catch (error: any) {
    ElMessage.error(error?.message || '解决冲突失败')
  }
}

async function openNode(node: NodeRow) {
  nodeImpact.value = null
  try {
    const detail = (await knowledgeApi.getNode(node.id)) as any
    nodeDetail.value = detail
    editingPayload.value = JSON.stringify(detail.payload, null, 2)
    nodeImpact.value = (await knowledgeApi.getNodeImpact(node.id)) as any
    nodeDrawerVisible.value = true
  } catch (error: any) {
    ElMessage.error(error?.message || '加载节点失败')
  }
}

async function saveNode() {
  const detail = nodeDetail.value
  if (!detail) return
  try {
    const payload = JSON.parse(editingPayload.value)
    const res: any = await knowledgeApi.patchNode(detail.id, payload)
    if (!res?.changed) {
      ElMessage.info('内容未变化')
      return
    }
    const affected = res?.affected_compositions || []
    ElMessage.success(`已保存新版本 v${res.version}，${affected.length} 个组合待复验`)
    await Promise.all([loadNodes(), loadConflicts()])
    const fresh: any = await knowledgeApi.getNode(detail.id)
    nodeDetail.value = fresh
    nodeImpact.value = (await knowledgeApi.getNodeImpact(fresh.id)) as any
    editingPayload.value = JSON.stringify(fresh.payload, null, 2)
  } catch (error: any) {
    ElMessage.error(error?.message || '保存失败')
  }
}

onMounted(() => {
  void loadConflicts()
  void loadNodes()
  void loadInbox()
})
</script>

<template>
  <section class="graph-admin">
    <div class="panel">
      <header class="panel-head">
        <div>
          <h4>知识节点</h4>
          <p>节点化真相：跨单元共享的字段/字典在此单点维护，改动自动标记引用组合待复验。</p>
        </div>
      </header>
      <div class="toolbar">
        <el-input
          v-model="nodeQuery.keyword"
          clearable
          placeholder="按自然键搜索（如 t_company.id）"
          @keyup.enter="searchNodes"
          @clear="searchNodes"
        />
        <el-select
          v-model="nodeQuery.node_kind"
          clearable
          placeholder="节点类型"
          @change="searchNodes"
        >
          <el-option label="数据表" value="dataset" />
          <el-option label="字段" value="field" />
          <el-option label="概念" value="concept" />
          <el-option label="流程阶段" value="stage" />
          <el-option label="口径" value="caliber" />
          <el-option label="规则" value="rule" />
          <el-option label="指标" value="metric" />
          <el-option label="查询范例" value="pattern" />
        </el-select>
        <el-button
          type="primary"
          plain
          @click="searchNodes"
          >搜索</el-button
        >
      </div>
      <el-table v-loading="loadingNodes" :data="nodes" @row-click="openNode">
        <el-table-column prop="node_kind" label="类型" width="110" />
        <el-table-column prop="natural_key" label="自然键" min-width="260" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.stub" type="info" size="small">stub</el-tag>
            <el-tag v-else type="success" size="small">v{{ row.version }}</el-tag>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无节点" :image-size="72" /></template>
      </el-table>
    </div>

    <div class="panel">
      <header class="panel-head">
        <div>
          <h4>归并冲突队列</h4>
          <p>同一物理键的多份声明不一致时在此裁决，永不静默覆盖。</p>
        </div>
        <el-tag :type="conflicts.length ? 'warning' : 'success'"
          >{{ conflicts.length }} 待裁决</el-tag
        >
      </header>
      <el-table v-loading="loadingConflicts" :data="conflicts">
        <el-table-column prop="node_kind" label="类型" width="100" />
        <el-table-column prop="natural_key" label="节点" min-width="220" />
        <el-table-column label="分歧" min-width="200">
          <template #default="{ row }">
            <span class="muted">{{ Object.keys(row.claim?.new_payload || {}).join('、') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click.stop="resolve(row, 'keep_existing')">保留既有</el-button>
            <el-button size="small" type="primary" plain @click.stop="resolve(row, 'accept_claim')">
              采纳新声明
            </el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="没有待裁决的冲突" :image-size="72" /></template>
      </el-table>
    </div>

    <div class="panel inbox-panel">
      <header class="panel-head">
        <div>
          <h4>沉淀候选</h4>
          <p>对话捕获的口径/规则候选在此晋升为节点或否决（关闭只进不出的收件箱）。</p>
        </div>
        <el-tag :type="inbox.length ? 'info' : 'success'">{{ inbox.length }} 待处理</el-tag>
      </header>
      <el-table v-loading="loadingInbox" :data="inbox">
        <el-table-column prop="kind" label="类型" width="100" />
        <el-table-column label="候选" min-width="200">
          <template #default="{ row }">
            <strong>{{ row.payload?.label || '-' }}</strong>
            <div class="muted">{{ row.trigger_id }}</div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              v-if="row.promotable"
              size="small"
              type="primary"
              plain
              @click="promoteCandidate(row)"
            >
              晋升为节点
            </el-button>
            <el-button size="small" @click="rejectCandidate(row)">否决</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="没有待处理的沉淀候选" :image-size="72" /></template>
      </el-table>
    </div>

    <el-drawer
      v-model="nodeDrawerVisible"
      size="560px"
      :title="nodeDetail?.natural_key || '节点详情'"
    >
      <template v-if="nodeDetail">
        <div class="node-meta">
          <el-tag>{{ nodeDetail.node_kind }}</el-tag>
          <el-tag type="info">版本 v{{ nodeDetail.version }}</el-tag>
          <el-tag v-if="nodeDetail.stub" type="info">stub</el-tag>
        </div>
        <p class="muted">payload 编辑（保存即生成新版本）</p>
        <el-input v-model="editingPayload" type="textarea" :rows="14" class="payload-editor" />
        <el-button type="primary" class="save-btn" @click="saveNode">保存新版本</el-button>

        <h5 class="impact-head">影响面（反向引用）</h5>
        <div v-if="nodeImpact?.compositions?.length" class="impact-list">
          <div v-for="item in nodeImpact.compositions" :key="item.id" class="impact-item">
            <strong>{{ item.title }}</strong>
            <span class="muted"
              >{{ item.unit_key }} · {{ statusLabel(item.lifecycle_status) }}</span
            >
            <el-tag
              v-if="item.validation_status === 'NEEDS_REVALIDATE'"
              type="warning"
              size="small"
            >
              待复验
            </el-tag>
          </div>
        </div>
        <el-empty v-else description="该节点暂未被任何组合引用" :image-size="64" />
        <div v-if="nodeImpact?.edge_counts" class="edge-counts">
          <span v-for="(count, kind) in nodeImpact.edge_counts" :key="kind" class="muted">
            {{ kind }} × {{ count }}
          </span>
        </div>
      </template>
    </el-drawer>
  </section>
</template>

<style scoped>
.graph-admin {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  gap: 16px;
  align-items: start;
}
.panel {
  padding: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
}
.panel-head {
  display: flex;
  margin-bottom: 14px;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.panel-head h4 {
  margin: 0;
}
.panel-head p {
  margin: 6px 0 0;
  color: var(--el-text-color-secondary);
}
.toolbar {
  display: grid;
  grid-template-columns: minmax(200px, 1fr) 150px auto;
  gap: 8px;
  margin-bottom: 12px;
}
.node-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.payload-editor {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
}
.save-btn {
  margin-top: 10px;
}
.impact-head {
  margin: 20px 0 10px;
}
.impact-list {
  display: grid;
  gap: 8px;
}
.impact-item {
  display: flex;
  padding: 8px 10px;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: var(--el-fill-color-extra-light);
  border-radius: 6px;
}
.edge-counts {
  display: flex;
  margin-top: 10px;
  gap: 10px;
  flex-wrap: wrap;
}
.muted {
  color: var(--el-text-color-secondary);
}
.inbox-panel {
  grid-column: 1 / -1;
}
@media (max-width: 900px) {
  .graph-admin {
    grid-template-columns: 1fr;
  }
  .toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
