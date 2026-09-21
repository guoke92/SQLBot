import { request } from '@/utils/request'

export interface CatalogIndexJob {
  status: string
  kind?: string
  ds_ids?: number[] | null
  phase?: string
  message?: string
  started_at?: string | null
  finished_at?: string | null
  error?: string | null
  tables?: number
  pages?: number
  value_rows?: number
}

export interface CatalogIndexRow {
  ds_id: number
  name: string
  state: string
  tables: number
  checked_tables: number
  value_rows: number
  corpus_key: string
  wiki_pages: number
  wiki_status: string
  wiki_generation: number
}

export const catalogIndexApi = {
  status: (dsId?: number) =>
    request.get('/datasource/catalog-index/status', {
      params: dsId != null ? { ds_id: dsId } : {},
    }) as Promise<{ job: CatalogIndexJob; items: CatalogIndexRow[] }>,
  job: () => request.get('/datasource/catalog-index/job') as Promise<CatalogIndexJob>,
  extractValues: (dsId?: number) =>
    request.post(
      '/datasource/catalog-index/extract-values',
      dsId != null ? { ds_id: dsId } : {},
    ) as Promise<CatalogIndexJob>,
  generateWiki: (dsId: number) =>
    request.post('/datasource/catalog-index/generate-wiki', {
      ds_id: dsId,
    }) as Promise<CatalogIndexJob>,
}
