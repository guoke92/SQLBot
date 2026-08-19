<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import {
  knowledgeApi,
  type KnowledgePackageUnitSummary,
  type KnowledgeUnitDetail,
  type KnowledgeUnitSummary,
} from '@/api/knowledge'
import { statusLabel, statusTagType } from '../presentation'
import ValidationIssueList from './ValidationIssueList.vue'
import IconOpeDelete from '@/assets/svg/icon_delete.svg'
import IconOpeEdit from '@/assets/svg/icon_edit_outlined.svg'

const props = defineProps<{
  modelValue: boolean
  item: KnowledgeUnitSummary | KnowledgePackageUnitSummary | null
  mode?: 'package' | 'review' | 'runtime'
}>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; changed: [] }>()

const loading = ref(false)
const acting = ref(false)
const detail = ref<KnowledgeUnitDetail | null>(null)
const editMode = ref(false)
const draftJson = ref('')

const content = computed(() => detail.value?.revision.content)
const sectionCounts = computed(() => {
  const value = content.value?.content
  return value
    ? {
        concepts: value.concepts.length,
        processes: value.processes.length,
        datasets: value.datasets.length,
        relationships: value.relationships.length,
        metrics: value.metrics.length,
        calibers: value.calibers.length,
        rules: value.domain_rules.length,
        queries: value.verified_query_patterns.length,
      }
    : {}
})
const referencedEvidence = computed(() => {
  const refs = new Set<string>()
  collectEvidenceRefs(content.value, refs)
  return (detail.value?.evidence || []).filter((item) => refs.has(item.reference_id))
})

const operationLabels: Record<string, string> = {
  read: '读取',
  insert: '新增',
  update: '更新',
  delete: '删除',
  upsert: '新增或更新',
}

function collectEvidenceRefs(value: unknown, refs: Set<string>) {
  if (Array.isArray(value)) {
    value.forEach((item) => collectEvidenceRefs(item, refs))
    return
  }
  if (!value || typeof value !== 'object') return
  Object.entries(value as Record<string, unknown>).forEach(([key, child]) => {
    if (key === 'evidence_refs' && Array.isArray(child)) {
      child.forEach((item) => typeof item === 'string' && refs.add(item))
      return
    }
    collectEvidenceRefs(child, refs)
  })
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {}
}

function records(value: unknown) {
  return Array.isArray(value) ? value.map(asRecord) : []
}

function texts(value: unknown) {
  return Array.isArray(value) ? value.map(String) : []
}

function fieldRefLabel(value: unknown) {
  const ref = asRecord(value)
  const dataset = String(ref.dataset || '')
  const field = String(ref.field || '')
  return [dataset, field].filter(Boolean).join('.') || '-'
}

function fieldTargets(value: unknown) {
  return records(value).map(fieldRefLabel).join('、')
}

function dictionaryEntries(value: unknown) {
  return Object.entries(asRecord(value))
}

function itemId(value: Record<string, unknown>) {
  return String(
    value.concept_id ||
      value.stage_id ||
      value.dataset_id ||
      value.relationship_id ||
      value.metric_id ||
      value.caliber_id ||
      value.rule_id ||
      value.pattern_id ||
      labelOf(value)
  )
}

async function load() {
  if (!props.item || !props.modelValue) return
  loading.value = true
  try {
    detail.value = (await knowledgeApi.getUnit(
      props.item.unit_id,
      props.item.revision
    )) as KnowledgeUnitDetail
    draftJson.value = JSON.stringify(detail.value.revision.content, null, 2)
    editMode.value = false
  } finally {
    loading.value = false
  }
}

watch(() => [props.modelValue, props.item?.revision_id], load, { immediate: true })

function close() {
  emit('update:modelValue', false)
}

async function askReason(title: string) {
  try {
    const result = await ElMessageBox.prompt(
      '请说明处理原因，内容会写入该版本的审核记录。',
      title,
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputValidator: (value) => Boolean(value.trim()) || '请填写原因',
      }
    )
    return result.value.trim()
  } catch {
    return null
  }
}

const currentBinding = computed(() => detail.value?.bindings?.[0] || null)
const lifecycle = computed(
  () => detail.value?.revision.lifecycle_status || props.item?.lifecycle_status || ''
)
const validationStatus = computed(
  () => detail.value?.revision.validation_status || props.item?.validation_status || ''
)
const canEditInPlace = computed(() => lifecycle.value === 'DRAFT' || lifecycle.value === 'REJECTED')
const packageMode = computed(() => (props.mode || 'package') === 'package')
const reviewMode = computed(() => props.mode === 'review')
const validationIssues = computed(() => {
  const summary = detail.value?.revision.validation_summary || {}
  const fromSummary = Array.isArray(summary.issues) ? summary.issues : []
  const fromBinding = currentBinding.value?.validation_result?.issues || []
  return (fromSummary.length ? fromSummary : fromBinding) as Array<Record<string, unknown>>
})
const validationSummaryText = computed(() => {
  const summary = detail.value?.revision.validation_summary || {}
  return String(summary.summary || summary.message || currentBinding.value?.validation_result?.summary || '')
})

async function run(action: 'approve' | 'request' | 'reject' | 'publish' | 'unpublish') {
  if (!props.item) return
  if (action === 'unpublish') {
    try {
      await ElMessageBox.confirm(
        '撤销发布后，该知识单元将不再被问数召回。绑定和内容会保留，可以重新发布。',
        '撤销发布知识单元',
        { type: 'warning', confirmButtonText: '撤销发布', cancelButtonText: '取消' }
      )
    } catch {
      return
    }
  }
  acting.value = true
  try {
    if (action === 'approve') await knowledgeApi.approve(props.item.unit_id, props.item.revision)
    if (action === 'request') {
      const reason = await askReason('请求补充')
      if (!reason) return
      await knowledgeApi.requestChanges(props.item.unit_id, props.item.revision, reason)
    }
    if (action === 'reject') {
      const reason = await askReason('拒绝知识单元')
      if (!reason) return
      await knowledgeApi.reject(props.item.unit_id, props.item.revision, reason)
    }
    if (action === 'publish') await knowledgeApi.publish(props.item.unit_id, props.item.revision)
    if (action === 'unpublish') {
      await knowledgeApi.unpublish(props.item.unit_id, props.item.revision)
    }
    ElMessage.success(action === 'unpublish' ? '已撤销发布' : '操作成功')
    emit('changed')
    close()
  } finally {
    acting.value = false
  }
}

async function saveRevision(fork = false) {
  if (!props.item) return
  try {
    const parsed = JSON.parse(draftJson.value)
    acting.value = true
    const result = (await knowledgeApi.editUnit(
      props.item.unit_id,
      props.item.revision,
      parsed,
      fork || !canEditInPlace.value
    )) as { forked?: boolean; revision?: number }
    ElMessage.success(result.forked ? '已创建新版本，旧版本已废弃。请在知识包上重新绑定并校验。' : '已保存当前版本，请在知识包上重新校验')
    emit('changed')
    if (result.forked) close()
    else {
      editMode.value = false
      await load()
    }
  } catch (error) {
    if (error instanceof SyntaxError) ElMessage.error('知识内容不是有效 JSON')
    else throw error
  } finally {
    acting.value = false
  }
}

async function deleteCurrent() {
  if (!props.item) return
  try {
    await ElMessageBox.confirm(
      '删除后该知识单元的全部版本将被删除，且无法恢复。',
      '删除知识单元',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  acting.value = true
  try {
    await knowledgeApi.deleteUnit(props.item.unit_id)
    ElMessage.success('知识单元已删除')
    emit('changed')
    close()
  } finally {
    acting.value = false
  }
}

function labelOf(value: Record<string, unknown>) {
  return String(
    value.name || value.title || value.label || value.business_meaning || value.description || '-'
  )
}

function aliasesOf(value: Record<string, unknown>) {
  return Array.isArray(value.aliases) ? value.aliases.join('、') : ''
}

function fieldCount(value: Record<string, unknown>) {
  return Array.isArray(value.fields) ? value.fields.length : 0
}
</script>

<template>
  <el-drawer :model-value="modelValue" size="min(920px, 96vw)" destroy-on-close @close="close">
    <template #header>
      <div class="drawer-title">
        <div>
          <h3>{{ detail?.unit.title || item?.title }}</h3>
          <span>{{ detail?.unit.unit_key || item?.unit_key }} · Revision {{ item?.revision }}</span>
        </div>
        <div class="status-tags">
          <el-tag
            :type="statusTagType(detail?.revision.lifecycle_status || item?.lifecycle_status)"
          >
            {{ statusLabel(detail?.revision.lifecycle_status || item?.lifecycle_status) }}
          </el-tag>
          <el-tag :type="statusTagType(detail?.revision.validation_status || item?.validation_status)">
            {{ statusLabel(detail?.revision.validation_status || item?.validation_status) }}
          </el-tag>
          <el-tag v-if="currentBinding" :type="statusTagType(currentBinding.status)">
            {{ statusLabel(currentBinding.status) }}
          </el-tag>
        </div>
      </div>
    </template>

    <div v-loading="loading" class="unit-detail">
      <template v-if="content && !editMode">
        <section
          v-if="validationStatus && validationStatus !== 'NOT_RUN'"
          class="overview-card"
        >
          <h2>校验结果</h2>
          <ValidationIssueList
            :status="validationStatus"
            :summary="validationSummaryText"
            :issues="validationIssues"
          />
        </section>

        <section class="overview-card">
          <h2>{{ content.title }}</h2>
          <p>{{ content.description }}</p>
          <div class="meta-line">
            <span>领域：{{ content.domain }}</span>
            <span>适用范围：{{ content.applicability || '未限定' }}</span>
            <span>置信度：{{ Math.round(content.confidence * 100) }}%</span>
          </div>
        </section>

        <div class="section-counts">
          <span v-for="(count, name) in sectionCounts" :key="name">
            <strong>{{ count }}</strong
            >{{ name }}
          </span>
        </div>

        <el-collapse>
          <el-collapse-item title="业务概念、别名与字典" name="concepts">
            <div class="item-grid">
              <article
                v-for="itemValue in content.content.concepts"
                :key="String(itemValue.concept_id)"
              >
                <strong>{{ labelOf(itemValue) }}</strong>
                <p>{{ itemValue.definition || '-' }}</p>
                <small v-if="aliasesOf(itemValue)">别名：{{ aliasesOf(itemValue) }}</small>
                <div v-if="dictionaryEntries(itemValue.dictionary).length" class="dictionary-list">
                  <el-tag
                    v-for="([key, value], index) in dictionaryEntries(itemValue.dictionary)"
                    :key="`${key}:${index}`"
                    size="small"
                    type="info"
                  >
                    {{ key }} = {{ value }}
                  </el-tag>
                </div>
              </article>
            </div>
          </el-collapse-item>
          <el-collapse-item title="业务流程、状态与数据变化" name="processes">
            <div class="timeline-list">
              <article v-for="stage in content.content.processes" :key="itemId(stage)">
                <strong>{{ labelOf(stage) }}</strong>
                <p>{{ stage.description || '-' }}</p>
                <div class="stage-meta">
                  <span v-if="stage.trigger">触发：{{ stage.trigger }}</span>
                  <span v-if="texts(stage.enter_conditions).length"
                    >进入：{{ texts(stage.enter_conditions).join('；') }}</span
                  >
                  <span v-if="texts(stage.exit_conditions).length"
                    >完成：{{ texts(stage.exit_conditions).join('；') }}</span
                  >
                  <span v-if="texts(stage.next_stages).length"
                    >下一阶段：{{ texts(stage.next_stages).join('、') }}</span
                  >
                </div>
                <div v-if="records(stage.data_effects).length" class="effect-list">
                  <div
                    v-for="effect in records(stage.data_effects)"
                    :key="`${effect.operation}:${effect.dataset}:${texts(effect.fields).join(',')}`"
                  >
                    <el-tag size="small" type="primary">
                      {{ operationLabels[String(effect.operation)] || effect.operation }}
                    </el-tag>
                    <strong>{{ effect.dataset }}</strong>
                    <span v-if="texts(effect.fields).length"
                      >字段：{{ texts(effect.fields).join('、') }}</span
                    >
                    <span v-if="effect.condition">条件：{{ effect.condition }}</span>
                    <span v-if="effect.description">{{ effect.description }}</span>
                  </div>
                </div>
              </article>
            </div>
          </el-collapse-item>
          <el-collapse-item title="数据对象、表与字段" name="datasets">
            <div class="item-grid">
              <article
                v-for="dataset in content.content.datasets"
                :key="String(dataset.dataset_id)"
              >
                <strong>{{ labelOf(dataset) }}</strong>
                <p>{{ dataset.database ? `${dataset.database}.` : '' }}{{ dataset.name }}</p>
                <p class="subtle-text">{{ dataset.description || '-' }}</p>
                <div v-if="records(dataset.fields).length" class="field-list">
                  <span v-for="field in records(dataset.fields)" :key="String(field.field_id)">
                    <strong>{{ field.name }}</strong>
                    <small>{{ field.description || field.data_type || '' }}</small>
                  </span>
                </div>
                <small v-else>{{ fieldCount(dataset) }} 个字段</small>
              </article>
            </div>
          </el-collapse-item>
          <el-collapse-item title="关系、指标和查询口径" name="semantics">
            <div class="semantic-groups">
              <section>
                <h4>数据关系</h4>
                <article v-for="relation in content.content.relationships" :key="itemId(relation)">
                  <strong>{{ relation.business_meaning || relation.relationship_id }}</strong>
                  <p>{{ fieldRefLabel(relation.left) }} ↔ {{ fieldRefLabel(relation.right) }}</p>
                  <small>
                    {{ relation.relationship_type || '关联' }}
                    <template v-if="relation.cardinality"> · {{ relation.cardinality }}</template>
                    · 置信度 {{ Math.round(Number(relation.confidence || 0) * 100) }}%
                  </small>
                </article>
                <el-empty
                  v-if="!content.content.relationships.length"
                  description="未定义关系"
                  :image-size="48"
                />
              </section>
              <section>
                <h4>指标</h4>
                <article v-for="metric in content.content.metrics" :key="itemId(metric)">
                  <strong>{{ labelOf(metric) }}</strong>
                  <p>{{ metric.description || '-' }}</p>
                  <small>
                    {{ metric.aggregation }}({{ fieldRefLabel(metric.field) }})
                    <template v-if="records(metric.grain).length">
                      · 粒度 {{ records(metric.grain).map(fieldRefLabel).join('、') }}
                    </template>
                  </small>
                </article>
                <el-empty
                  v-if="!content.content.metrics.length"
                  description="未定义指标"
                  :image-size="48"
                />
              </section>
              <section>
                <h4>查询口径</h4>
                <article v-for="caliber in content.content.calibers" :key="itemId(caliber)">
                  <strong>{{ labelOf(caliber) }}</strong>
                  <p>{{ caliber.description || '-' }}</p>
                  <small>影响字段：{{ fieldTargets(caliber.field_targets) || '-' }}</small>
                  <details v-if="caliber.contract_fragment">
                    <summary>查看契约片段</summary>
                    <pre>{{ JSON.stringify(caliber.contract_fragment, null, 2) }}</pre>
                  </details>
                </article>
                <el-empty
                  v-if="!content.content.calibers.length"
                  description="未定义口径"
                  :image-size="48"
                />
              </section>
              <section>
                <h4>业务数据规则</h4>
                <article v-for="rule in content.content.domain_rules" :key="itemId(rule)">
                  <strong>{{ labelOf(rule) }}</strong>
                  <p>{{ rule.content }}</p>
                  <small>适用：{{ rule.applicability || '-' }}</small>
                  <small>查询影响：{{ rule.query_impact || '-' }}</small>
                  <small>影响字段：{{ fieldTargets(rule.field_targets) || '-' }}</small>
                </article>
                <el-empty
                  v-if="!content.content.domain_rules.length"
                  description="未定义规则"
                  :image-size="48"
                />
              </section>
            </div>
          </el-collapse-item>
          <el-collapse-item title="已验证查询模式" name="queries">
            <div
              v-for="query in content.content.verified_query_patterns"
              :key="String(query.pattern_id)"
              class="query-card"
            >
              <strong>{{ query.question }}</strong>
              <pre>{{ query.query }}</pre>
              <small>
                已执行：{{ asRecord(query.verification).executed ? '是' : '否' }} · 通过：{{
                  asRecord(query.verification).passed ? '是' : '否'
                }}
              </small>
            </div>
          </el-collapse-item>
          <el-collapse-item title="证据、冲突与校验" name="governance">
            <ValidationIssueList
              :status="validationStatus"
              :summary="validationSummaryText"
              :issues="validationIssues"
            />
            <details class="raw-structure">
              <summary>查看原始校验结构</summary>
              <pre>{{ JSON.stringify(detail?.revision.validation_summary, null, 2) }}</pre>
            </details>
            <h4>来源证据（{{ referencedEvidence.length }}）</h4>
            <div v-if="referencedEvidence.length" class="evidence-list">
              <article v-for="evidence in referencedEvidence" :key="evidence.evidence_key">
                <div class="evidence-heading">
                  <strong>{{ evidence.reference_id }}</strong>
                  <el-tag size="small" type="info">{{ evidence.evidence_kind }}</el-tag>
                </div>
                <p>{{ evidence.source_id }} · {{ evidence.locator || '未提供定位' }}</p>
                <pre v-if="Object.keys(evidence.payload || {}).length">{{
                  JSON.stringify(evidence.payload, null, 2)
                }}</pre>
              </article>
            </div>
            <el-empty v-else description="该知识单元未关联可用证据" :image-size="56" />
            <h4>假设</h4>
            <p>{{ content.assumptions.join('；') || '-' }}</p>
            <h4>冲突</h4>
            <pre>{{ JSON.stringify(content.conflicts, null, 2) }}</pre>
            <details class="raw-structure">
              <summary>查看完整原始结构</summary>
              <pre>{{ JSON.stringify(content, null, 2) }}</pre>
            </details>
          </el-collapse-item>
        </el-collapse>
      </template>

      <el-input v-else-if="editMode" v-model="draftJson" type="textarea" :rows="30" />
    </div>

    <template #footer>
      <div class="drawer-actions">
        <el-button @click="close">关闭</el-button>
        <div class="drawer-actions-right">
          <el-tooltip v-if="packageMode && !editMode && lifecycle !== 'PUBLISHED' && lifecycle !== 'RETIRED'" content="编辑">
            <el-button :loading="acting" @click="editMode = true">
              <el-icon><IconOpeEdit /></el-icon>
              编辑
            </el-button>
          </el-tooltip>
          <el-button v-if="editMode" @click="editMode = false">取消</el-button>
          <el-button
            v-if="editMode && canEditInPlace"
            type="primary"
            :loading="acting"
            @click="saveRevision(false)"
          >
            保存
          </el-button>
          <el-button
            v-if="editMode"
            :type="canEditInPlace ? 'default' : 'primary'"
            :loading="acting"
            @click="saveRevision(true)"
          >
            保存为新版本
          </el-button>
          <el-tooltip v-if="packageMode && !editMode" content="删除知识单元">
            <el-button type="danger" plain :loading="acting" @click="deleteCurrent">
              <el-icon><IconOpeDelete /></el-icon>
            </el-button>
          </el-tooltip>
          <el-button
            v-if="reviewMode && !editMode && lifecycle === 'IN_REVIEW'"
            :loading="acting"
            @click="run('request')"
            >请求补充</el-button
          >
          <el-button
            v-if="reviewMode && !editMode && lifecycle === 'IN_REVIEW'"
            type="danger"
            plain
            :loading="acting"
            @click="run('reject')"
            >拒绝</el-button
          >
          <el-button
            v-if="reviewMode && !editMode && lifecycle === 'IN_REVIEW'"
            type="primary"
            :loading="acting"
            @click="run('approve')"
            >批准</el-button
          >
          <el-button
            v-if="!editMode && lifecycle === 'APPROVED'"
            type="primary"
            :loading="acting"
            @click="run('publish')"
            >发布</el-button
          >
          <el-button
            v-if="!editMode && lifecycle === 'RETIRED'"
            type="primary"
            :loading="acting"
            @click="run('publish')"
            >重新发布</el-button
          >
          <el-button
            v-if="!editMode && lifecycle === 'PUBLISHED'"
            :loading="acting"
            @click="run('unpublish')"
            >撤销发布</el-button
          >
        </div>
      </div>
    </template>
  </el-drawer>
</template>

<style scoped>
.drawer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}
.drawer-actions-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.drawer-title,
.status-tags,
.meta-line,
.section-counts {
  display: flex;
  align-items: center;
  gap: 10px;
}
.drawer-title {
  width: 100%;
  justify-content: space-between;
}
.drawer-title h3 {
  margin: 0 0 4px;
}
.drawer-title span,
.meta-line {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.unit-detail {
  padding-bottom: 20px;
}
.overview-card {
  padding: 18px;
  margin-bottom: 14px;
  background: var(--el-fill-color-extra-light);
  border-radius: 10px;
}
.overview-card h2 {
  margin: 0 0 8px;
}
.overview-card p {
  line-height: 1.7;
}
.meta-line {
  flex-wrap: wrap;
}
.section-counts {
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.section-counts span {
  padding: 6px 10px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  font-size: 12px;
}
.section-counts strong {
  margin-right: 5px;
}
.item-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.item-grid article,
.timeline-list article,
.query-card,
.evidence-list article {
  padding: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
}
.item-grid p,
.timeline-list p {
  margin: 6px 0;
  line-height: 1.6;
}
.item-grid small {
  color: var(--el-text-color-secondary);
}
pre {
  max-height: 360px;
  padding: 12px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  background: var(--el-fill-color-extra-light);
  border-radius: 6px;
  font-size: 12px;
}
.timeline-list,
.semantic-groups,
.evidence-list {
  display: grid;
  gap: 10px;
}
.semantic-groups {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.semantic-groups h4 {
  margin: 0 0 6px;
}
.semantic-groups > section {
  display: grid;
  align-content: start;
  gap: 8px;
}
.semantic-groups article {
  padding: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
}
.semantic-groups article p {
  margin: 6px 0;
  line-height: 1.6;
}
.semantic-groups article small {
  display: block;
  margin-top: 4px;
  color: var(--el-text-color-secondary);
}
.dictionary-list,
.field-list,
.effect-list,
.stage-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.dictionary-list {
  margin-top: 8px;
}
.stage-meta {
  margin: 8px 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.stage-meta span {
  flex-basis: 100%;
}
.effect-list {
  display: grid;
}
.effect-list > div {
  display: flex;
  padding: 8px;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  background: var(--el-fill-color-extra-light);
  border-radius: 6px;
  font-size: 12px;
}
.field-list span {
  display: grid;
  padding: 5px 8px;
  background: var(--el-fill-color-light);
  border-radius: 5px;
}
.field-list small,
.subtle-text {
  color: var(--el-text-color-secondary);
}
.raw-structure {
  margin-top: 16px;
}
details summary {
  margin-top: 8px;
  cursor: pointer;
  color: var(--el-color-primary);
  font-size: 12px;
}
.evidence-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.evidence-list p {
  margin: 6px 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
@media (max-width: 720px) {
  .item-grid,
  .semantic-groups {
    grid-template-columns: 1fr;
  }
}
</style>
