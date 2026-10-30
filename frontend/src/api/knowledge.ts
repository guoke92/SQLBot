import { request } from '@/utils/request'

export interface WikiBindingBrief {
  datasource_id: number
  datasource_name?: string | null
  remap_databases?: Record<string, string>
}

export interface WikiCorpusRow {
  id: number
  oid: number
  corpus_key: string
  name?: string | null
  generation: number
  page_count: number
  published_count: number
  draft_count: number
  status: string
  embedded_chunks: number
  failed_chunks?: number
  embed_error?: string | null
  source_path?: string | null
  update_time?: string | null
  bindings: WikiBindingBrief[]
}

export interface WikiImportResult {
  corpus_id: number
  corpus_key: string
  generation: number
  total: number
  published: number
  draft: number
  failed: number
  failed_files: { path: string; error: string }[]
  status: string
  replaced: boolean
}

export interface WikiPageSummary {
  belong: string
  page_key: string
  title: string
  page_type: string
  status: string
  aliases: string[]
  links?: string[]
}

export interface WikiPageCatalog {
  corpus_key: string
  counts: { belong: string; count: number }[]
  pages: WikiPageSummary[]
}

export interface WikiPageDetail {
  belong: string
  page_key: string
  title: string
  page_type: string
  status: string
  domain: string
  aliases: string[]
  anchors: string[]
  maps_to: string
  field_targets: string[]
  related: string[]
  also_confused_with: string[]
  adjudication: string
  databases: string[]
  recall: boolean
  inactive: boolean
  body: string
  ground: { kind: string; label: string }[]
  reviews: { type: string; title: string; body: string }[]
  links: { target: string; alias: string }[]
  findings: { code: string; message: string }[]
  parse_error: string | null
  page_disabled: boolean
  update_time: string | null
}

export const knowledgeApi = {
  listCorpora: () => request.get('/wiki/corpora') as Promise<WikiCorpusRow[]>,
  importCorpus: (data: {
    corpus_key: string
    pages_dir: string
    replace?: boolean
    name?: string
  }) => request.post('/wiki/corpora/import', data) as Promise<WikiImportResult>,
  corpusStatus: (corpusKey: string) =>
    request.get(`/wiki/corpora/${encodeURIComponent(corpusKey)}/status`) as Promise<
      Pick<
        WikiCorpusRow,
        | 'corpus_key'
        | 'generation'
        | 'page_count'
        | 'published_count'
        | 'draft_count'
        | 'status'
        | 'embedded_chunks'
        | 'failed_chunks'
        | 'embed_error'
        | 'source_path'
        | 'update_time'
      >
    >,
  deleteCorpus: (corpusKey: string) =>
    request.delete(`/wiki/corpora/${encodeURIComponent(corpusKey)}`),
  listBindings: (params?: { datasource_id?: number; corpus_key?: string }) =>
    request.get('/wiki/bindings', { params }),
  suggestRemap: (corpusKey: string, datasourceId: number) =>
    request.get('/wiki/bindings/suggest', {
      params: { corpus_key: corpusKey, datasource_id: datasourceId },
    }) as Promise<{ remap_databases: Record<string, string> }>,
  bindCorpus: (data: {
    corpus_key: string
    datasource_id?: number
    datasource_ids?: number[]
    remap_databases?: Record<string, string>
    remaps_by_datasource?: Record<string, Record<string, string>>
  }) => request.put('/wiki/bindings', data),
  unbindDatasource: (datasourceId: number) => request.delete(`/wiki/bindings/${datasourceId}`),
  retryEmbed: (corpusKey: string) =>
    request.post(`/wiki/corpora/${encodeURIComponent(corpusKey)}/retry-embed`),
  listPages: (corpusKey: string, params?: { q?: string; belong?: string; status?: string }) =>
    request.get(`/wiki/corpora/${encodeURIComponent(corpusKey)}/pages`, {
      params,
    }) as Promise<WikiPageCatalog>,
  readPage: (corpusKey: string, belong: string, pageKey: string) =>
    request.get(
      `/wiki/corpora/${encodeURIComponent(corpusKey)}/pages/${encodeURIComponent(belong)}/${encodeURIComponent(pageKey)}`
    ) as Promise<WikiPageDetail>,
  openMaintainChat: (
    corpusKey: string,
    data: {
      belong?: string
      page_key?: string
      pages?: { belong: string; page_key: string }[]
      source_ids?: number[]
      brief?: string
    }
  ) =>
    request.post(`/wiki/corpora/${encodeURIComponent(corpusKey)}/maintain/chats`, data) as Promise<{
      chat_id: number
      corpus_key: string
      pages?: { belong: string; page_key: string }[]
      source_ids?: number[]
    }>,
  updateMaintainFocus: (
    chatId: number,
    data: {
      pages?: { belong: string; page_key: string }[]
      source_ids?: number[]
      replace?: boolean
    }
  ) => request.post(`/wiki/maintain/chats/${chatId}/focus`, data),
  previewMaterial: (
    corpusKey: string,
    params: {
      kind: 'page' | 'record' | 'source'
      belong?: string
      page_key?: string
      record_id?: number
      source_id?: number
    }
  ) =>
    request.get(`/wiki/corpora/${encodeURIComponent(corpusKey)}/maintain/preview`, {
      params,
    }) as Promise<WikiMaterialPreview>,
  maintainFocus: (chatId: number) =>
    request.get(`/wiki/maintain/chats/${chatId}/focus`) as Promise<{
      corpus_key: string
      pages: { belong: string; page_key: string; title: string }[]
      sources: { source_id: number; title: string; locator: string }[]
    }>,
  pasteSource: (corpusKey: string, data: { title?: string; body: string }) =>
    request.post(
      `/wiki/corpora/${encodeURIComponent(corpusKey)}/maintain/sources`,
      data
    ) as Promise<{
      corpus_key: string
      source_id: number
      locator: string
    }>,
  maintainRecords: (corpusKey: string) =>
    request.get(`/wiki/corpora/${encodeURIComponent(corpusKey)}/maintain/records`) as Promise<
      WikiMaintainRecord[]
    >,
  dialogues: (corpusKey: string) =>
    request.get(`/wiki/corpora/${encodeURIComponent(corpusKey)}/dialogues`) as Promise<{
      processing: number
      pending: number
      items: WikiDialogueItem[]
    }>,
  dialogueGroups: () => request.get('/wiki/dialogues') as Promise<WikiDialogueGroup[]>,
  conversations: (corpusKey: string) =>
    request.get(`/wiki/corpora/${encodeURIComponent(corpusKey)}/maintain/conversations`) as Promise<
      WikiConversationGroup[]
    >,
  captureMaterials: (recordIds: number[]) =>
    request.post('/wiki/maintain/materials', { record_ids: recordIds }) as Promise<
      { source_id: number; locator: string; corpus_key: string }[]
    >,
  sediment: (recordId: number) =>
    request.post('/wiki/maintain/sediment', { record_id: recordId }) as Promise<{
      corpus_key: string
      source_id: number
      locator: string
      feedback?: string | null
      comment?: string | null
    }>,
  pageHistory: (corpusKey: string, belong: string, pageKey: string) =>
    request.get(
      `/wiki/corpora/${encodeURIComponent(corpusKey)}/pages/${encodeURIComponent(belong)}/${encodeURIComponent(pageKey)}/history`
    ) as Promise<WikiRevision[]>,
  pageRevision: (corpusKey: string, belong: string, pageKey: string, revisionNo: number) =>
    request.get(
      `/wiki/corpora/${encodeURIComponent(corpusKey)}/pages/${encodeURIComponent(belong)}/${encodeURIComponent(pageKey)}/revisions/${revisionNo}`
    ) as Promise<{ revision_no: number; body_md: string; content_sha: string }>,
  pageDiff: (corpusKey: string, belong: string, pageKey: string, left: number, right: number) =>
    request.get(
      `/wiki/corpora/${encodeURIComponent(corpusKey)}/pages/${encodeURIComponent(belong)}/${encodeURIComponent(pageKey)}/diff`,
      { params: { left, right } }
    ) as Promise<{ diff: string; patches: WikiProposal[] }>,
  revertPage: (
    corpusKey: string,
    belong: string,
    pageKey: string,
    revisionNo: number,
    confirm: boolean
  ) =>
    request.post(
      `/wiki/corpora/${encodeURIComponent(corpusKey)}/pages/${encodeURIComponent(belong)}/${encodeURIComponent(pageKey)}/revert`,
      { revision_no: revisionNo, confirm }
    ) as Promise<Record<string, unknown>>,
  proposals: (runId: string) =>
    request.get(`/wiki/maintain/runs/${encodeURIComponent(runId)}/proposals`) as Promise<
      WikiProposal[]
    >,
  chatProposals: (chatId: number) =>
    request.get(`/wiki/maintain/chats/${chatId}/proposals`) as Promise<WikiProposal[]>,
  decideProposal: (patchId: number, decision: 'accept' | 'reject') =>
    request.post(`/wiki/maintain/patches/${patchId}/decision`, { decision }),
  promotePage: (corpusKey: string, belong: string, pageKey: string) =>
    request.post(
      `/wiki/corpora/${encodeURIComponent(corpusKey)}/pages/${encodeURIComponent(belong)}/${encodeURIComponent(pageKey)}/promote`
    ),
}

export interface WikiProposal {
  id: number
  op: string
  claim_path: string
  payload: Record<string, unknown>
  origin: string
  status: string
  belong: string
  page_key: string
  scope?: string
  tool_name?: string
  trust?: string
  aspect?: string
  source_ref?: string
  detail?: string
  reason?: string
  basis?: string
  diff?: string
}

export interface WikiMaterialPreview {
  kind: string
  chat_id?: number
  record_id?: number
  title: string
  subtitle: string
  question: string
  body: string
  feedback: string
  comment: string
}

export interface WikiDialogueGroup {
  corpus_key: string
  name: string
  processing: number
  pending: number
  items: WikiDialogueItem[]
}

export interface WikiDialogueItem {
  kind: 'chat' | 'source'
  chat_id?: number
  source_id?: number
  title: string
  status: 'processing' | 'pending' | 'done'
  run_status?: string
  run_id?: string
  locator?: string
  update_time: string
}

export interface WikiConversationGroup {
  chat_id: number
  title: string
  records: WikiMaintainRecord[]
}

export interface WikiMaintainRecord {
  record_id: number
  chat_id: number
  question: string
  feedback?: string | null
  comment?: string | null
  source_id?: number | null
  locator: string
}

export interface WikiRevision {
  revision_no: number
  create_time: string
  actor: string
  tool_name: string
  source_ref: string
  content_sha: string
  status: string
}
