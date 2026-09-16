import type { InjectionKey, Ref } from 'vue'
import type { ProcessTimeline } from '@/features/conversation/processTimeline'

export interface ChatDatasetPage {
  dataset_id: string
  fields: string[]
  rows: Array<Record<string, any>>
  row_count: number
  truncated: boolean
  offset: number
  limit: number
}

export interface ChatDataSource {
  readOnly: boolean
  getTimeline: (
    recordId: number,
    view: 'compact' | 'detail',
    runId?: string
  ) => Promise<ProcessTimeline | undefined>
  getDatasetRows: (
    recordId: number,
    datasetId: string,
    options?: { offset?: number; limit?: number }
  ) => Promise<ChatDatasetPage>
}

export const CHAT_DATA_SOURCE_KEY: InjectionKey<Ref<ChatDataSource | null>> = Symbol(
  'chatDataSource'
)
