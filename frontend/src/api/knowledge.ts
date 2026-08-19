import { request } from '@/utils/request'
import { packageUploadForm } from '@/api/knowledgePackageDocuments'

export type KnowledgeLifecycle =
  'DRAFT' | 'IN_REVIEW' | 'APPROVED' | 'PUBLISHED' | 'REJECTED' | 'RETIRED'
export type KnowledgeValidation = 'NOT_RUN' | 'PASS' | 'WARNING' | 'FAIL'
export type KnowledgeBindingStatus = 'UNBOUND' | 'BOUND' | 'STALE'
export type KnowledgeDeploymentStatus =
  'NOT_PUBLISHED' | 'BUILDING' | 'ACTIVE' | 'ERROR' | 'RETIRED'

export interface KnowledgePackageSummary {
  id: number
  package_id: string
  revision: number
  schema_version: string
  namespace: string
  title: string
  description: string
  status: string
  unit_count: number
  update_time: string
}

export interface KnowledgeUnitSummary {
  unit_id: number
  unit_key: string
  title: string
  domain: string
  revision_id: number
  revision: number
  lifecycle_status: KnowledgeLifecycle
  validation_status: KnowledgeValidation
  binding_status: KnowledgeBindingStatus
  deployment_status: KnowledgeDeploymentStatus
  confidence: number
  datasource_id?: number | null
  next_step: string
  update_time: string
  validation_summary_text?: string
  validation_error_count?: number
  validation_warning_count?: number
  validation_issue_count?: number
  validation_issues?: Array<Record<string, unknown>>
}

export interface KnowledgePackageUnitSummary {
  unit_id: number
  unit_key: string
  title: string
  domain: string
  revision_id: number
  revision: number
  lifecycle_status: KnowledgeLifecycle
  validation_status: KnowledgeValidation
  binding_status?: KnowledgeBindingStatus
  datasource_id?: number | null
  next_step?: string
  validation_summary_text?: string
  validation_error_count?: number
  validation_warning_count?: number
  validation_issue_count?: number
  validation_issues?: Array<Record<string, unknown>>
}

export interface KnowledgeUnitPage {
  items: KnowledgeUnitSummary[]
  total: number
  page: number
  page_size: number
  lifecycle_counts: Record<string, number>
}

export interface KnowledgeUnitContent {
  unit_id: string
  revision: number
  title: string
  aliases: string[]
  domain: string
  applicability: string
  description: string
  content: {
    concepts: Array<Record<string, unknown>>
    processes: Array<Record<string, unknown>>
    datasets: Array<Record<string, unknown>>
    relationships: Array<Record<string, unknown>>
    metrics: Array<Record<string, unknown>>
    calibers: Array<Record<string, unknown>>
    domain_rules: Array<Record<string, unknown>>
    verified_query_patterns: Array<Record<string, unknown>>
  }
  evidence_refs: string[]
  assumptions: string[]
  conflicts: Array<Record<string, unknown>>
  confidence: number
}

export interface KnowledgeBinding {
  id: number
  datasource_id: number
  status: KnowledgeBindingStatus
  validation_result: {
    status: KnowledgeValidation
    summary?: string
    issues?: Array<Record<string, unknown>>
  }
  mapping: Record<string, unknown>
  catalog_fingerprint: string
}

export interface KnowledgeDeployment {
  id: number
  revision_id: number
  binding_id: number
  status: KnowledgeDeploymentStatus
  projection_manifest: Record<string, unknown>
  error?: string
  activated_at?: string
  update_time: string
}

export interface KnowledgeUnitDetail {
  unit: { id: number; unit_key: string; namespace: string; domain: string; title: string }
  revision: {
    id: number
    revision: number
    lifecycle_status: KnowledgeLifecycle
    validation_status: KnowledgeValidation
    validation_summary: Record<string, unknown>
    confidence: number
    content: KnowledgeUnitContent
  }
  evidence: Array<{
    id: number
    evidence_key: string
    reference_id: string
    source_id: string
    evidence_kind: string
    locator: string
    content_hash: string
    payload: Record<string, unknown>
    active: boolean
    create_time: string
  }>
  bindings: KnowledgeBinding[]
  deployments: KnowledgeDeployment[]
}

export interface KnowledgePackageDetail {
  package: KnowledgePackageSummary
  sources: Array<Record<string, unknown>>
  evidence_count: number
  units: KnowledgePackageUnitSummary[]
}

export interface DatasourceBindingCandidate {
  datasource_id: number
  datasource_name: string
  required_count: number
  matched_count: number
  coverage: number
  missing: string[]
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export const knowledgeApi = {
  importFiles: (files: File[]) =>
    request.post('/knowledge/packages/upload', packageUploadForm(files), {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getPackages: (params?: { page?: number; page_size?: number }) =>
    request.get('/knowledge/packages', { params }),
  getPackage: (packageId: string, revision?: number) =>
    request.get(`/knowledge/packages/${encodeURIComponent(packageId)}`, {
      params: { revision },
    }),
  getBindingCandidates: (packageId: string, revision?: number) =>
    request.get(`/knowledge/packages/${encodeURIComponent(packageId)}/binding-candidates`, {
      params: { revision },
    }),
  bindPackage: (packageId: string, revision: number, datasourceId: number) =>
    request.post(
      `/knowledge/packages/${encodeURIComponent(packageId)}/bind`,
      { datasource_id: datasourceId },
      { params: { revision } }
    ),
  validatePackage: (packageId: string, revision?: number) =>
    request.post(
      `/knowledge/packages/${encodeURIComponent(packageId)}/validate`,
      {},
      { params: { revision } }
    ),
  submitPackageReview: (packageId: string, revision?: number) =>
    request.post(
      `/knowledge/packages/${encodeURIComponent(packageId)}/submit-review`,
      {},
      { params: { revision } }
    ),
  publishPackage: (packageId: string, revision?: number) =>
    request.post(
      `/knowledge/packages/${encodeURIComponent(packageId)}/publish`,
      {},
      { params: { revision } }
    ),
  unpublishPackage: (packageId: string, revision?: number) =>
    request.post(
      `/knowledge/packages/${encodeURIComponent(packageId)}/unpublish`,
      {},
      { params: { revision } }
    ),
  deletePackage: (packageId: string, revision?: number) =>
    request.delete(`/knowledge/packages/${encodeURIComponent(packageId)}`, {
      params: { revision },
    }),
  getUnits: (params?: {
    keyword?: string
    lifecycle?: string
    validation?: string
    page?: number
    page_size?: number
  }) => request.get('/knowledge/units', { params }),
  getUnit: (unitId: number, revision: number) =>
    request.get(`/knowledge/units/${unitId}/revisions/${revision}`),
  editUnit: (
    unitId: number,
    revision: number,
    content: KnowledgeUnitContent,
    fork = false
  ) =>
    request.patch(`/knowledge/units/${unitId}/revisions/${revision}`, { content, fork }),
  deleteUnit: (unitId: number) => request.delete(`/knowledge/units/${unitId}`),
  approve: (unitId: number, revision: number, reason = '') =>
    request.post(`/knowledge/units/${unitId}/revisions/${revision}/approve`, { reason }),
  reject: (unitId: number, revision: number, reason: string) =>
    request.post(`/knowledge/units/${unitId}/revisions/${revision}/reject`, { reason }),
  requestChanges: (unitId: number, revision: number, reason: string) =>
    request.post(`/knowledge/units/${unitId}/revisions/${revision}/request-changes`, {
      reason,
    }),
  publish: (unitId: number, revision: number) =>
    request.post(`/knowledge/units/${unitId}/revisions/${revision}/publish`),
  unpublish: (unitId: number, revision: number) =>
    request.post(`/knowledge/units/${unitId}/revisions/${revision}/unpublish`),
  getDeployments: (params?: { status?: string; page?: number; page_size?: number }) =>
    request.get('/knowledge/deployments', { params }),
  getDeployment: (deploymentId: number) => request.get(`/knowledge/deployments/${deploymentId}`),
}
