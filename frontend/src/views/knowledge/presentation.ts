export type StatusTagType = 'success' | 'warning' | 'danger' | 'info' | 'primary'

const labels: Record<string, string> = {
  DRAFT: '草稿',
  IN_REVIEW: '审核中',
  APPROVED: '已批准',
  PUBLISHED: '已发布',
  REJECTED: '已拒绝',
  RETIRED: '已退役',
  NOT_RUN: '未校验',
  PASS: '校验通过',
  WARNING: '存在警告',
  FAIL: '校验失败',
  NEEDS_REVALIDATE: '待复验',
  UNBOUND: '未绑定',
  BOUND: '已绑定',
  STALE: '绑定已过期',
  NOT_PUBLISHED: '未发布',
  BUILDING: '构建中',
  ACTIVE: '运行中',
  ERROR: '构建失败',
  REGISTERED: '已登记',
}

const nextSteps: Record<string, string> = {
  BIND_DATASOURCE: '绑定数据源',
  REVALIDATE: '重新校验',
  REVIEW_ISSUES: '查看校验问题',
  VALIDATE: '执行校验',
  SUBMIT_REVIEW: '提交审核',
  REVIEW: '处理审核',
  PUBLISH: '发布',
  REPUBLISH: '重新发布',
  VIEW_RUNTIME: '查看运行时',
}

const issueCodes: Record<string, string> = {
  DATASET_NOT_FOUND: '找不到数据表',
  FIELD_NOT_FOUND: '找不到字段',
  FIELD_TYPE_MISMATCH: '字段类型不匹配',
  RELATIONSHIP_NOT_BOUND: '关系未能绑定',
  RELATIONSHIP_TYPE_MISMATCH: '关系两端类型不同',
  RELATIONSHIP_PROPOSED: '关系待确认',
  QUERY_PROTOCOL_UNSUPPORTED: '数据源不支持该查询',
  QUERY_VALIDATION_FAILED: '查询示例无法通过校验',
  QUERY_EXECUTION_FAILED: '查询示例执行失败',
  DATASOURCE_CATALOG_MISMATCH: '数据源缺少声明的表',
}

const knowledgeKinds: Record<string, string> = {
  relationship: '关系',
  dataset: '数据表',
  field: '字段',
  query: '查询示例',
}

export function statusLabel(status?: string | null) {
  if (!status) return '-'
  return labels[status] || status
}

export function nextStepLabel(step?: string | null) {
  if (!step) return '查看详情'
  return nextSteps[step] || '查看详情'
}

export function issueSeverity(issue?: Record<string, unknown> | null) {
  return String(issue?.severity || '') === 'warning' ? 'warning' : 'danger'
}

export function issueHeading(issue?: Record<string, unknown> | null) {
  if (!issue) return '校验问题'
  const kind = knowledgeKinds[String(issue.knowledge_kind || '')] || ''
  const title = String(issue.title || '').trim()
  if (kind && title) return `${kind} · ${title}`
  if (title) return title
  const code = String(issue.code || '')
  return issueCodes[code] || code || '校验问题'
}

export function issueMessage(issue?: Record<string, unknown> | null) {
  if (!issue) return ''
  const left = String(issue.left_locator || issue.left || '').trim()
  const right = String(issue.right_locator || issue.right || '').trim()
  const join = left && right ? `${left} ↔ ${right}` : left || right
  const types =
    issue.left_type && issue.right_type
      ? `${issue.left_type} ↔ ${issue.right_type}`
      : issue.expected_type && issue.actual_type
        ? `${issue.expected_type} → ${issue.actual_type}`
        : ''
  const dataset = String(issue.dataset || '').trim()
  const field = String(issue.field || '').trim()
  const message = String(issue.message || '').trim()
  return [...new Set([join, types, dataset && field ? `${dataset}.${field}` : dataset || field, message])]
    .filter(Boolean)
    .join(' · ')
}

export function statusTagType(status?: string | null): StatusTagType {
  if (
    status === 'FAIL' ||
    status === 'ERROR' ||
    status === 'REJECTED'
  )
    return 'danger'
  if (status === 'PASS' || status === 'ACTIVE' || status === 'PUBLISHED') return 'success'
  if (
    status === 'WARNING' ||
    status === 'IN_REVIEW' ||
    status === 'BUILDING' ||
    status === 'STALE'
  )
    return 'warning'
  return 'info'
}
