import { request } from '@/utils/request'
import { encryptWithXpack } from '@/platform/xpack'

export const AuthApi = {
  login: async (credentials: { username: string; password: string }) => {
    const [username, password] = await Promise.all([
      encryptWithXpack(credentials.username),
      encryptWithXpack(credentials.password),
    ])
    const entryCredentials = {
      username,
      password,
    }
    return request.post<{
      data: any
      token: string
    }>('/login/access-token', entryCredentials, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },
  logout: (data: any) => request.post('/login/logout', data),
  info: () =>
    request.get('/user/info', {
      requestOptions: { silent: true },
    }),
}
