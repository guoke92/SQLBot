import { request } from '@/utils/request'
import { encryptWithXpack } from '@/platform/xpack'

export const modelApi = {
  queryAll: (keyword?: string) =>
    request.get('/system/aimodel', { params: keyword ? { keyword } : {} }),
  add: async (data: any) => {
    const param = { ...data }
    if (param.api_key) {
      param.api_key = await encryptWithXpack(data.api_key)
    }
    if (param.api_domain) {
      param.api_domain = await encryptWithXpack(data.api_domain)
    }
    return request.post('/system/aimodel', param)
  },
  edit: async (data: any) => {
    const param = { ...data }
    if (param.api_key) {
      param.api_key = await encryptWithXpack(data.api_key)
    }
    if (param.api_domain) {
      param.api_domain = await encryptWithXpack(data.api_domain)
    }
    return request.put('/system/aimodel', param)
  },
  delete: (id: number) => request.delete(`/system/aimodel/${id}`),
  query: (id: number) => request.get(`/system/aimodel/${id}`),
  setDefault: (id: number) => request.put(`/system/aimodel/default/${id}`),
  check: (data: any) => request.fetchStream('/system/aimodel/status', data),
  platform: (id: number, lazy?: number, pid?: string) =>
    request.post(`/system/platform/org/${id}`, { lazy, pid }),
  userSync: (data: any) => request.post(`/system/platform/user/sync`, data),
  list_by_ws: () => request.get(`/system/aimodel/list/by_ws`),
}
