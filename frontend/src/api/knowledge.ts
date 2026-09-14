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
  unbindDatasource: (datasourceId: number) =>
    request.delete(`/wiki/bindings/${datasourceId}`),
  retryEmbed: (corpusKey: string) =>
    request.post(`/wiki/corpora/${encodeURIComponent(corpusKey)}/retry-embed`),
}
