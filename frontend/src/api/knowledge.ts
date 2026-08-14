import { request } from '@/utils/request'

export interface KnowledgeSuggestion {
  id: number
  lineage_id: string
  label: string
  trust_tier: string
  reproduce_count: number
  successful_apply_count: number
  positive_feedback_count: number
  negative_feedback_count: number
  requires_review: boolean
  recommended_action: 'promote' | 'review'
}

export type KnowledgeImportReadiness = 'ready' | 'review_required' | 'invalid' | 'retained_only'

export interface KnowledgeIssue {
  code: string
  severity: 'info' | 'warning' | 'error'
  detail: string
  params: Record<string, unknown>
}

export interface KnowledgeImportItemResult {
  item_id: string
  kind: string
  readiness: KnowledgeImportReadiness
  action: string
  target_id?: number
  messages: string[]
  issues: KnowledgeIssue[]
  normalized?: Record<string, unknown>
}

export interface KnowledgeImportReport {
  package_id: string
  package_fingerprint: string
  dry_run: boolean
  total: number
  kind_counts: Record<string, number>
  readiness_counts: Record<string, number>
  action_counts: Record<string, number>
  registry_id?: number
  registry_revision?: number
  registry_action?: string
  warnings: string[]
  items: KnowledgeImportItemResult[]
}

export interface KnowledgeImportRequest {
  package?: Record<string, unknown> | unknown[] | string
  documents?: Array<{ name: string; content: string }>
  package_id?: string
  default_datasource_id?: number
  default_datasource_name?: string
  include_kinds?: string[]
  expected_preview_fingerprint?: string
}

export interface KnowledgePackageSummary {
  package_id: string
  schema_version: string
  title: string
  description: string
  revision: number
  item_count: number
  source_count: number
  update_time: string
}

export interface KnowledgePackageItem {
  registry_item_id: number
  item_id: string
  kind: string
  source_status: string
  readiness: KnowledgeImportReadiness
  present: boolean
  payload: Record<string, unknown>
  messages: string[]
  issues: KnowledgeIssue[]
  runtime_action?: string
  runtime_target_id?: number
}

export interface KnowledgePackageDetail {
  package: KnowledgePackageSummary
  sources: Array<Record<string, unknown>>
  items: KnowledgePackageItem[]
  total: number
  page: number
  page_size: number
  kind_counts: Record<string, number>
  readiness_counts: Record<string, number>
  action_counts: Record<string, number>
}

export interface KnowledgeStagingItem {
  id: number
  kind: string
  status: string
  natural_key: string
  trigger_id: string
  lineage_id: string
  source_record_id?: number
  payload: Record<string, unknown>
  scope: Record<string, unknown>
  provenance: Record<string, unknown>
  quality_snapshot: Record<string, unknown>
  suggested_trust_tier?: string
  create_time: string
  update_time: string
}

export interface KnowledgeReviewItem {
  review_key: string
  source: 'staging' | 'relation' | 'package'
  id: number
  kind: string
  status: string
  trigger_id: string
  package_id?: string
  item_id?: string
  payload: Record<string, unknown>
  scope: Record<string, unknown>
  provenance: Record<string, unknown>
  quality_snapshot: Record<string, unknown>
  issues: KnowledgeIssue[]
  actions: Array<'approve' | 'reject' | 'approve_publish'>
  create_time: string
}

export interface KnowledgeReviewPage {
  items: KnowledgeReviewItem[]
  total: number
  page: number
  page_size: number
  kind_counts: Record<string, number>
}

export interface RuntimeKnowledgeItem {
  id: number
  kind: string
  label: string
  summary: string
  trust_tier: string
  enabled: boolean
  datasource_id?: number
  source: string
  create_time?: string
  payload: Record<string, unknown>
}

export interface RuntimeKnowledgePage {
  items: RuntimeKnowledgeItem[]
  total: number
  page: number
  page_size: number
  kind_counts: Record<string, number>
}

export const knowledgeApi = {
  getStaging: () => request.get('/knowledge/staging'),
  certify: (stagingId: number) => request.post(`/knowledge/staging/${stagingId}/certify`),
  reject: (stagingId: number, reason: string) =>
    request.post(`/knowledge/staging/${stagingId}/reject`, { reason }),
  getAssets: (params?: { kind?: string; trust_tier?: string; enabled?: boolean }) =>
    request.get('/knowledge/assets', { params }),
  getRuntimeAssets: (params?: {
    keyword?: string
    kind?: string
    enabled?: boolean
    page?: number
    page_size?: number
  }) => request.get('/knowledge/runtime-assets', { params }),
  getReviews: (params?: { keyword?: string; kind?: string; page?: number; page_size?: number }) =>
    request.get('/knowledge/reviews', { params }),
  getSuggestions: () => request.get('/knowledge/suggestions'),
  promote: (caliberId: number) => request.post(`/knowledge/caliber/${caliberId}/promote-trusted`),
  demote: (caliberId: number, to_tier: string, reason: string) =>
    request.post(`/knowledge/caliber/${caliberId}/demote`, { to_tier, reason }),
  disable: (caliberId: number) => request.post(`/knowledge/caliber/${caliberId}/disable`),
  getRules: () => request.get('/knowledge/rules'),
  createRule: (data: { label: string; content: string; ds_id?: number }) =>
    request.post('/knowledge/rule', data),
  disableRule: (ruleId: number) => request.post(`/knowledge/rule/${ruleId}/disable`),
  enableRule: (ruleId: number) => request.post(`/knowledge/rule/${ruleId}/enable`),
  getLineage: (kind: string, assetId: number) =>
    request.get(`/knowledge/assets/${kind}/${assetId}/lineage`),
  previewImport: (data: KnowledgeImportRequest) => request.post('/knowledge/import/preview', data),
  applyImport: (data: KnowledgeImportRequest) => request.post('/knowledge/import/apply', data),
  getPackages: () => request.get('/knowledge/packages'),
  getPackageDetail: (
    packageId: string,
    params?: {
      keyword?: string
      kind?: string
      readiness?: string
      page?: number
      page_size?: number
    }
  ) => request.get(`/knowledge/packages/${encodeURIComponent(packageId)}`, { params }),
  getPackageItems: (packageId: string) =>
    request.get(`/knowledge/packages/${encodeURIComponent(packageId)}/items`),
  advancePackageItem: (
    packageId: string,
    itemId: string,
    data: {
      action: 'publish' | 'approve_publish'
      default_datasource_id?: number
    }
  ) =>
    request.post(
      `/knowledge/packages/${encodeURIComponent(packageId)}/items/${encodeURIComponent(itemId)}/advance`,
      data
    ),
  rejectPackageItem: (packageId: string, itemId: string) =>
    request.post(
      `/knowledge/packages/${encodeURIComponent(packageId)}/items/${encodeURIComponent(itemId)}/reject`
    ),
  decideRelation: (relationId: number, status: 'CONFIRMED' | 'REJECTED') =>
    request.post(`/datasource/profiling/relations/${relationId}/decision`, { status }),
}
