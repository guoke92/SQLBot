import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    navigation?: boolean
    navigationOrder?: number
    requiresSpaceAdmin?: boolean
    requiresAdmin?: boolean
  }
}
