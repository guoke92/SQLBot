import type { KnowledgeImportItemResult, KnowledgeIssue } from '@/api/knowledge'

export type KnowledgePayload = Record<string, unknown>
export type KnowledgeDisplayItem = Pick<KnowledgeImportItemResult, 'item_id' | 'kind'> & {
  normalized?: KnowledgePayload
}

export function knowledgePayload(item: KnowledgeDisplayItem): KnowledgePayload {
  return item.normalized || {}
}

export function asRecord(value: unknown): KnowledgePayload {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as KnowledgePayload)
    : {}
}

export function asText(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return JSON.stringify(value, null, 2)
}

export function fieldRefLabel(value: unknown): string {
  const field = asRecord(value)
  const table = asText(field.table_name)
  const name = asText(field.field_name)
  return [table, name].filter(Boolean).join('.') || '-'
}

export function knowledgeItemTitle(item: KnowledgeDisplayItem): string {
  const payload = knowledgePayload(item)
  if (item.kind === 'relation') {
    return `${fieldRefLabel(payload.left)} ↔ ${fieldRefLabel(payload.right)}`
  }
  if (item.kind === 'evidence') {
    return [asText(payload.subject), asText(payload.predicate)].filter(Boolean).join(' · ')
  }
  return asText(payload.word) || asText(payload.label) || asText(payload.question) || item.item_id
}

export function knowledgeItemSummary(item: KnowledgeDisplayItem): string {
  const payload = knowledgePayload(item)
  if (item.kind === 'relation') {
    const kind = asText(payload.relation_kind)
    const cardinality = asText(payload.cardinality)
    return [kind, cardinality].filter(Boolean).join(' · ')
  }
  if (item.kind === 'evidence') return asText(payload.value)
  return (
    asText(payload.description) ||
    asText(payload.summary) ||
    asText(payload.content) ||
    asText(payload.query)
  )
}

export function issueTranslationKey(issue: KnowledgeIssue): string {
  return `knowledge.issue_${issue.code.toLowerCase()}`
}

export function knowledgeIssueText(issue: KnowledgeIssue, translated = ''): string {
  if (!translated) return issue.detail || issue.code
  if (issue.code === 'VALIDATION_FAILED' && issue.detail && issue.detail !== translated) {
    return `${translated}：${issue.detail}`
  }
  return translated
}

export function prettyJson(value: unknown): string {
  if (value === null || value === undefined || value === '') return '-'
  return typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}
