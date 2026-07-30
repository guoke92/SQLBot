import { useCache } from '@/utils/useCache'
import { useAppearanceStoreWithOut } from '@/stores/appearance'
import { useUserStore } from '@/stores/user'
import type { Router } from 'vue-router'
import { toLoginPage } from '@/utils/utils'
import { installXpackRoutes, loadXpackRuntime } from '@/platform/xpack'

const appearanceStore = useAppearanceStoreWithOut()
const userStore = useUserStore()
const { wsCache } = useCache()
const whiteList = ['/login', '/admin-login']
const assistantWhiteList = ['/assistant', '/embeddedPage', '/embeddedCommon', '/401']

export const watchRouter = (router: Router) => {
  let appearanceRuntimeApplied = false

  const prepareXpack = async () => {
    const runtime = await loadXpackRuntime()
    if (!runtime) return
    installXpackRoutes(router)
    if (!appearanceRuntimeApplied) {
      appearanceRuntimeApplied = true
      appearanceStore.setLoaded(false)
    }
  }

  router.beforeEach(async (to: any, from: any, next: any) => {
    const token = wsCache.get('user.token')
    const shouldPrepareXpack = whiteList.includes(to.path) || Boolean(token)
    const wasUnmatched = !to.matched?.length
    if (shouldPrepareXpack) {
      await prepareXpack()
      if (wasUnmatched) {
        if (router.resolve(to.fullPath).matched.length) {
          next({
            path: to.path,
            query: to.query,
            hash: to.hash,
            replace: true,
          })
        } else {
          next('/chat')
        }
        return
      }
    }
    try {
      await appearanceStore.setAppearance()
    } catch (error) {
      console.error('Failed to load appearance settings:', error)
    }
    if (to.path.startsWith('/login') && userStore.getUid) {
      next(to?.query?.redirect || '/')
      return
    }
    if (assistantWhiteList.includes(to.path)) {
      next()
      return
    }
    if (whiteList.includes(to.path)) {
      next()
      return
    }
    if (!token) {
      // ElMessage.error('Please login first')
      next(toLoginPage(to.fullPath))
      return
    }
    if (!userStore.getUid) {
      try {
        await userStore.info()
      } catch {
        userStore.clear()
        next(toLoginPage(to.fullPath))
        return
      }
    }
    if (to.path === '/docs') {
      location.href = to.fullPath
      return
    }
    if (to.path === '/' || accessCrossPermission(to)) {
      next('/chat')
      return
    }
    if (to.path === '/login' || to.path === '/admin-login') {
      console.info(from)
      next('/chat')
    } else {
      next()
    }
  })
}

const accessCrossPermission = (to: any) => {
  if (!to?.path) return false
  return (
    (to.path.startsWith('/system') && !userStore.isAdmin) ||
    (to.path.startsWith('/set') && !userStore.isSpaceAdmin) ||
    (to.matched.some((route: any) => route.meta?.requiresSpaceAdmin) && !userStore.isSpaceAdmin)
  )
}
