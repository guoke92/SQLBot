<script lang="ts" setup>
import { computed } from 'vue'
import type { KnowledgeImportItemResult } from '@/api/knowledge'
import {
  asRecord,
  asText,
  fieldRefLabel,
  knowledgeItemSummary,
  knowledgeItemTitle,
  knowledgeIssueText,
  knowledgePayload,
  issueTranslationKey,
  prettyJson,
} from '../presentation'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ item: KnowledgeImportItemResult }>()
const { t, te } = useI18n()

const payload = computed(() => knowledgePayload(props.item))
const title = computed(() => knowledgeItemTitle(props.item))
const summary = computed(() => knowledgeItemSummary(props.item))
const aliases = computed(() =>
  Array.isArray(payload.value.aliases) ? payload.value.aliases.map(asText).filter(Boolean) : []
)
const evidenceRefs = computed(() =>
  Array.isArray(payload.value.evidence_refs)
    ? payload.value.evidence_refs.map(asText).filter(Boolean)
    : []
)
const fieldTargets = computed(() =>
  Array.isArray(payload.value.field_targets) ? payload.value.field_targets : []
)
const confidence = computed(() => {
  const value = Number(payload.value.confidence)
  return Number.isFinite(value) ? `${Math.round(value * 100)}%` : '-'
})

function issueText(code: string, detail: string) {
  const issue = { code, detail, severity: 'info' as const, params: {} }
  const key = issueTranslationKey(issue)
  return knowledgeIssueText(issue, te(key) ? t(key) : '')
}
</script>

<template>
  <div class="knowledge-detail">
    <div class="detail-heading">
      <div>
        <div class="detail-title">{{ title }}</div>
        <div v-if="summary && summary !== title" class="detail-summary">{{ summary }}</div>
      </div>
      <div class="detail-tags">
        <el-tag>{{ t(`knowledge.kind_${item.kind}`) }}</el-tag>
        <el-tag type="info">{{ item.item_id }}</el-tag>
      </div>
    </div>

    <div v-if="item.issues?.length" class="issue-list">
      <el-alert
        v-for="issue in item.issues"
        :key="`${issue.code}-${issue.detail}`"
        :title="issueText(issue.code, issue.detail)"
        :type="issue.severity"
        :closable="false"
        show-icon
      />
    </div>

    <el-descriptions :column="2" border size="small">
      <el-descriptions-item :label="t('knowledge.source_status')">
        {{ asText(payload.status) || '-' }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('knowledge.confidence')">
        {{ confidence }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('knowledge.datasource_scope')">
        {{ asText(payload.datasource_name) || asText(payload.datasource_id) || '-' }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('knowledge.runtime_target')">
        {{ item.target_id || '-' }}
      </el-descriptions-item>
    </el-descriptions>

    <section v-if="item.kind === 'terminology'" class="detail-section">
      <div class="section-label">{{ t('knowledge.aliases') }}</div>
      <div class="tag-list">
        <el-tag v-for="alias in aliases" :key="alias" type="info">{{ alias }}</el-tag>
        <span v-if="!aliases.length">-</span>
      </div>
      <div class="section-label">{{ t('knowledge.definition') }}</div>
      <div class="text-content">{{ asText(payload.description) || '-' }}</div>
    </section>

    <section v-else-if="item.kind === 'caliber'" class="detail-section">
      <div class="section-label">{{ t('knowledge.field_targets') }}</div>
      <div class="tag-list">
        <el-tag v-for="target in fieldTargets" :key="fieldRefLabel(target)" type="info">
          {{ fieldRefLabel(target) }}
        </el-tag>
        <span v-if="!fieldTargets.length">-</span>
      </div>
      <div class="section-label">{{ t('knowledge.contract_fragment') }}</div>
      <pre class="code-block">{{ prettyJson(payload.contract_fragment) }}</pre>
    </section>

    <section v-else-if="item.kind === 'relation'" class="detail-section">
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item :label="t('knowledge.left_field')">
          {{ fieldRefLabel(payload.left) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('knowledge.right_field')">
          {{ fieldRefLabel(payload.right) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('knowledge.relation_type')">
          {{ asText(payload.relation_kind) || '-' }} · {{ asText(payload.cardinality) || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      <div class="section-label">{{ t('knowledge.relation_evidence') }}</div>
      <pre class="code-block">{{ prettyJson(payload.evidence) }}</pre>
    </section>

    <section v-else-if="item.kind === 'example'" class="detail-section">
      <div class="section-label">{{ t('knowledge.business_question') }}</div>
      <div class="text-content">{{ asText(payload.question) || '-' }}</div>
      <div class="section-label">{{ t('knowledge.query_statement') }}</div>
      <pre class="code-block">{{ asText(payload.query) || '-' }}</pre>
      <div class="section-label">{{ t('knowledge.expected_specification') }}</div>
      <pre class="code-block">{{ prettyJson(payload.intended_specification) }}</pre>
      <div class="section-label">{{ t('knowledge.verification') }}</div>
      <pre class="code-block">{{ prettyJson(payload.verification) }}</pre>
    </section>

    <section v-else-if="item.kind === 'rule'" class="detail-section">
      <div class="section-label">{{ t('knowledge.rule_content') }}</div>
      <div class="text-content preserve-lines">{{ asText(payload.content) || '-' }}</div>
    </section>

    <section v-else-if="item.kind === 'evidence'" class="detail-section">
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item :label="t('knowledge.subject')">
          {{ asText(payload.subject) || '-' }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('knowledge.predicate')">
          {{ asText(payload.predicate) || '-' }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('knowledge.fact_value')">
          <span class="preserve-lines">{{ asText(payload.value) || '-' }}</span>
        </el-descriptions-item>
      </el-descriptions>
      <div class="section-label">{{ t('knowledge.fact_evidence') }}</div>
      <pre class="code-block">{{ prettyJson(payload.evidence) }}</pre>
    </section>

    <section class="detail-section">
      <div class="section-label">{{ t('knowledge.evidence_refs') }}</div>
      <div class="tag-list">
        <el-tag v-for="reference in evidenceRefs" :key="reference" type="info">
          {{ reference }}
        </el-tag>
        <span v-if="!evidenceRefs.length">-</span>
      </div>
    </section>

    <el-collapse class="technical-details">
      <el-collapse-item :title="t('knowledge.technical_details')" name="technical">
        <div class="section-label">{{ t('knowledge.provenance') }}</div>
        <pre class="code-block">{{ prettyJson(asRecord(payload.provenance)) }}</pre>
        <div class="section-label">{{ t('knowledge.raw_payload') }}</div>
        <pre class="code-block">{{ prettyJson(payload) }}</pre>
      </el-collapse-item>
    </el-collapse>

    <div v-if="$slots.actions" class="detail-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.knowledge-detail {
  padding: 0 4px 24px;
}

.detail-heading {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.detail-title {
  color: var(--el-text-color-primary);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.5;
}

.detail-summary {
  margin-top: 8px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}

.detail-tags,
.tag-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-tags {
  flex-shrink: 0;
}

.issue-list {
  display: grid;
  gap: 8px;
  margin-bottom: 18px;
}

.detail-section {
  margin-top: 22px;
}

.section-label {
  margin: 14px 0 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  font-weight: 500;
}

.text-content {
  padding: 12px 14px;
  color: var(--el-text-color-primary);
  line-height: 1.7;
  background: var(--el-fill-color-lighter);
  border-radius: 6px;
}

.preserve-lines {
  white-space: pre-wrap;
}

.code-block {
  max-height: 360px;
  padding: 12px 14px;
  margin: 0;
  overflow: auto;
  color: var(--el-text-color-primary);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  background: var(--el-fill-color-lighter);
  border-radius: 6px;
}

.technical-details {
  margin-top: 22px;
}

.detail-actions {
  position: sticky;
  bottom: 0;
  display: flex;
  padding: 16px 0 4px;
  margin-top: 20px;
  justify-content: flex-end;
  gap: 10px;
  background: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>
