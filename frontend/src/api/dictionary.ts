import { request } from '@/utils/request'

interface DictionaryFieldConfigData {
  ds_id: number
  table_id: number
  field_id: number
  enabled: boolean
  max_values: number
  status: 'EMPTY' | 'STALE' | 'READY' | 'DISABLED'
  value_count: number
  last_synced_at?: string | null
  last_error?: string | null
  table_name: string
  field_name: string
  field_type?: string
}

export type DictionaryFieldConfig = DictionaryFieldConfigData &
  ({ id: number; configured: true } | { id: null; configured: false })

export const dictionaryApi = {
  list: (dsId: number, tableId: number) =>
    request.get<DictionaryFieldConfig[]>(`/dictionary/datasource/${dsId}?table_id=${tableId}`),
  create: (dsId: number, data: { field_id: number; enabled?: boolean; max_values?: number }) =>
    request.post<DictionaryFieldConfig>(`/dictionary/datasource/${dsId}`, data),
  update: (configId: number, data: { enabled?: boolean; max_values?: number }) =>
    request.put<DictionaryFieldConfig>(`/dictionary/${configId}`, data),
  refresh: (configIds: number[]) =>
    request.post<
      Array<{
        id: number
        status: DictionaryFieldConfig['status']
        value_count: number
        error?: string | null
      }>
    >('/dictionary/refresh', configIds),
}
