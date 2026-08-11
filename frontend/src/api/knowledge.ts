import { request } from '@/utils/request'

export const knowledgeApi = {
  getStaging: () => request.get('/knowledge/staging'),
  certify: (stagingId: string) => request.post(`/knowledge/staging/${stagingId}/certify`),
  reject: (stagingId: string, reason: string) =>
    request.post(`/knowledge/staging/${stagingId}/reject`, { reason }),
  getAssets: (params?: { kind?: string; trust_tier?: string; enabled?: boolean }) =>
    request.get('/knowledge/assets', { params }),
  getSuggestions: () => request.get('/knowledge/suggestions'),
  promote: (caliberId: string) => request.post(`/knowledge/caliber/${caliberId}/promote-trusted`),
  demote: (caliberId: string, to_tier: string, reason: string) =>
    request.post(`/knowledge/caliber/${caliberId}/demote`, { to_tier, reason }),
  disable: (caliberId: string) => request.post(`/knowledge/caliber/${caliberId}/disable`),
  getRules: () => request.get('/knowledge/rules'),
  createRule: (data: { label: string; content: string; ds_id?: string }) =>
    request.post('/knowledge/rule', data),
  disableRule: (ruleId: string) => request.post(`/knowledge/rule/${ruleId}/disable`),
  enableRule: (ruleId: string) => request.post(`/knowledge/rule/${ruleId}/enable`),
  getLineage: (kind: string, assetId: string) =>
    request.get(`/knowledge/assets/${kind}/${assetId}/lineage`),
}
