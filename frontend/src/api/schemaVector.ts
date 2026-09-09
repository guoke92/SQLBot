import { request } from '@/utils/request'

export interface SchemaVectorJob {
  status: 'idle' | 'running' | 'succeeded' | 'failed' | string
  ds_ids?: number[] | null
  phase?: string
  message?: string
  started_at?: string | null
  finished_at?: string | null
  table_docs?: number
  field_docs?: number
  relation_docs?: number
  embedded_docs?: number
  skipped_docs?: number
  error?: string | null
  accepted?: boolean
  reason?: string | null
}

export interface SchemaVectorRow {
  ds_id: number
  name: string
  enabled: boolean
  state: 'ready' | 'missing' | 'partial' | 'indexing' | 'empty' | 'disabled' | string
  checked_tables: number
  table_embeddings: number
  schema_docs: number
  schema_embedded: number
  schema_tables: number
  schema_fields: number
  schema_relations: number
  update_time?: string | null
}

export interface SchemaVectorStatus {
  job: SchemaVectorJob
  items: SchemaVectorRow[]
}

export const schemaVectorApi = {
  status: (dsId?: number) =>
    request.get('/datasource/schema-vector/status', {
      params: dsId != null ? { ds_id: dsId } : undefined,
    }) as Promise<SchemaVectorStatus>,
  job: () => request.get('/datasource/schema-vector/job') as Promise<SchemaVectorJob>,
  sync: (dsId?: number) =>
    request.post('/datasource/schema-vector/sync', dsId != null ? { ds_id: dsId } : {}) as Promise<SchemaVectorJob>,
}
