import type {
  RouteMeta,
  RouteRecordNormalized,
  RouteRecordRaw,
  RouteRecordRedirectOption,
  Router,
} from 'vue-router'

export interface NavigationAccess {
  isSpaceAdmin: boolean
}

export interface NavigationRoute {
  path: string
  meta: RouteMeta
  hidden?: boolean
  redirect?: RouteRecordRedirectOption
  children: NavigationRoute[]
}

const normalizeChildren = (
  routes: readonly RouteRecordRaw[] = [],
  parentPath = ''
): NavigationRoute[] =>
  routes.map((route) => {
    const path = route.path.startsWith('/')
      ? route.path
      : `${parentPath.replace(/\/$/, '')}/${route.path}`
    return {
      ...route,
      path,
      meta: route.meta ?? {},
      children: normalizeChildren(route.children ?? [], path),
    } as NavigationRoute
  })

const canAccess = (route: RouteRecordNormalized, access: NavigationAccess) =>
  !route.meta.requiresSpaceAdmin || access.isSpaceAdmin

export const getMainNavigation = (router: Router, access: NavigationAccess): NavigationRoute[] => {
  const routes = router
    .getRoutes()
    .filter((route) => route.meta.navigation === true && canAccess(route, access))
    .sort(
      (left, right) =>
        Number(left.meta.navigationOrder ?? Number.MAX_SAFE_INTEGER) -
        Number(right.meta.navigationOrder ?? Number.MAX_SAFE_INTEGER)
    )
  return routes.map(
    (route) =>
      ({
        ...route,
        children: normalizeChildren(route.children ?? [], route.path),
      }) as NavigationRoute
  )
}

export const getSystemNavigation = (router: Router): NavigationRoute[] => {
  const systemRoute = router.getRoutes().find((route) => route.name === 'system')
  return systemRoute ? normalizeChildren(systemRoute.children, systemRoute.path) : []
}
