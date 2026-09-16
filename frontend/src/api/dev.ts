import { chatApi } from '@/api/chat'
import { request } from '@/utils/request'

export interface DevWorkspace {
  id: string | number
  name: string
}

export interface DevOperator {
  id: string | number
  account?: string
  name?: string
}

export interface DevDatasource {
  id: string | number
  name: string
}

export interface DevChatRow {
  id: string | number
  brief?: string
  chat_type?: string
  datasource?: string | number | null
  datasource_name?: string | null
  engine_type?: string
  create_by?: string | number
  user_account?: string
  user_name?: string
  create_time?: string
  last_time?: string
  record_count: number
  feedback_up: number
  feedback_down: number
  has_error: boolean
}

export interface DevChatFilters {
  oid: string | number
  create_by?: string | number | null
  q?: string
  feedback?: string
  datasource?: string | number | null
  created_from?: string
  created_to?: string
  chat_ids?: Array<string | number>
}

export interface ExtractKeyInfo {
  key_prefix?: string
  created_at?: string
  created_by?: number
  key?: string
}

const queryOf = (filters: DevChatFilters) => {
  const params = new URLSearchParams()
  params.set('oid', String(filters.oid))
  if (filters.create_by != null && filters.create_by !== '') {
    params.set('create_by', String(filters.create_by))
  }
  if (filters.q) params.set('q', filters.q)
  if (filters.feedback && filters.feedback !== 'all') params.set('feedback', filters.feedback)
  if (filters.datasource != null && filters.datasource !== '') {
    params.set('datasource', String(filters.datasource))
  }
  if (filters.created_from) params.set('created_from', filters.created_from)
  if (filters.created_to) params.set('created_to', filters.created_to)
  if (filters.chat_ids?.length) params.set('chat_ids', filters.chat_ids.join(','))
  return params.toString()
}

const downloadBlob = async (url: string, filename: string) => {
  const blob = (await request.get(url, {
    responseType: 'blob',
    timeout: 300000,
    requestOptions: { customError: true },
  })) as Blob
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}

export const qaAdminApi = {
  workspaces: () => request.get('/dev/qa-admin/workspaces') as Promise<DevWorkspace[]>,
  operators: (oid: string | number) =>
    request.get(`/dev/qa-admin/operators?oid=${oid}`) as Promise<DevOperator[]>,
  datasources: (oid: string | number) =>
    request.get(`/dev/qa-admin/datasources?oid=${oid}`) as Promise<DevDatasource[]>,
  chats: (filters: DevChatFilters) =>
    request.get(`/dev/qa-admin/chats?${queryOf(filters)}`) as Promise<DevChatRow[]>,
  getChat: (chatId: string | number) =>
    request.get(`/dev/qa-admin/chats/${chatId}`).then(chatApi.toChatInfo),
  getTimeline: (
    recordId: number,
    options?: { view?: 'compact' | 'detail'; runId?: string }
  ) => {
    const params = new URLSearchParams()
    params.set('view', options?.view || 'compact')
    if (options?.runId) params.set('run_id', options.runId)
    return request.get(
      `/dev/qa-admin/records/${recordId}/timeline?${params.toString()}`,
      { requestOptions: { silent: true } }
    )
  },
  getDatasetRows: (
    recordId: number,
    datasetId: string,
    options?: { offset?: number; limit?: number }
  ) => {
    const params = new URLSearchParams()
    if (options?.offset != null) params.set('offset', String(options.offset))
    if (options?.limit != null) params.set('limit', String(options.limit))
    const query = params.toString()
    return request.get(
      `/dev/qa-admin/records/${recordId}/datasets/${encodeURIComponent(datasetId)}/rows${
        query ? `?${query}` : ''
      }`
    )
  },
  downloadFeedbackCsv: (filters: DevChatFilters) =>
    downloadBlob(
      `/dev/qa-admin/feedback.csv?${queryOf(filters)}`,
      `workspace-${filters.oid}-feedback.csv`
    ),
}

export const extractKeyApi = {
  get: () =>
    request.get('/dev/extract-key', {
      requestOptions: { silent: true, customError: true },
    }) as Promise<ExtractKeyInfo | null>,
  rotate: () => request.post('/dev/extract-key', {}) as Promise<ExtractKeyInfo>,
  revoke: () => request.delete('/dev/extract-key'),
}
