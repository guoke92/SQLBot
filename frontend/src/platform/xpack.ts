import type { Router } from 'vue-router'

interface LicenseInfo {
  status?: string
  [key: string]: unknown
}

interface XpackRuntime {
  init(apiBaseUrl: string): Promise<unknown>
  getLicense(): LicenseInfo | null
  generateRouters(router: Router): void
  sqlbotEncrypt(value: string): string
}

declare global {
  interface Window {
    LicenseGenerator?: XpackRuntime
  }
}

const SCRIPT_ID = 'sqlbot_xpack_static'
const SCRIPT_PATH = '/xpack_static/license-generator.umd.js'
const SCRIPT_TIMEOUT_MS = 2000
const RETRY_BACKOFF_MS = 60_000

let runtimePromise: Promise<XpackRuntime | undefined> | undefined
let nextRetryAt = 0
const initializedRouters = new WeakSet<Router>()

const apiOrigin = () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL
  if (!baseUrl || baseUrl.startsWith('/') || baseUrl.startsWith('.')) {
    return ''
  }
  return baseUrl.replace(/\/api\/v1\/?$/, '')
}

const currentRuntime = () => window.LicenseGenerator

const appendRuntimeScript = () =>
  new Promise<void>((resolve, reject) => {
    const existing = document.getElementById(SCRIPT_ID) as HTMLScriptElement | null
    if (existing) {
      if (currentRuntime()) {
        resolve()
        return
      }
      existing.remove()
    }

    const script = document.createElement('script')
    script.id = SCRIPT_ID
    script.src = `${apiOrigin()}${SCRIPT_PATH}?t=${Date.now()}`

    const timer = window.setTimeout(() => {
      script.remove()
      reject(new Error(`Timed out loading ${SCRIPT_PATH}`))
    }, SCRIPT_TIMEOUT_MS)

    script.onload = () => {
      window.clearTimeout(timer)
      resolve()
    }
    script.onerror = () => {
      window.clearTimeout(timer)
      script.remove()
      reject(new Error(`Failed to load ${SCRIPT_PATH}`))
    }
    document.head.appendChild(script)
  })

/**
 * Loads and initializes the optional xpack runtime once.
 *
 * Community features remain available when xpack is unavailable. Callers that
 * require encryption use encryptWithXpack(), which fails explicitly.
 */
export const loadXpackRuntime = async (): Promise<XpackRuntime | undefined> => {
  if (!currentRuntime() && Date.now() < nextRetryAt) {
    return undefined
  }
  if (!runtimePromise) {
    runtimePromise = (async () => {
      try {
        if (!currentRuntime()) {
          await appendRuntimeScript()
        }
        const runtime = currentRuntime()
        if (!runtime) {
          throw new Error('Xpack script loaded without registering its runtime')
        }
        await runtime.init(import.meta.env.VITE_API_BASE_URL)
        return runtime
      } catch (error) {
        console.warn('Xpack runtime is unavailable; continuing in community mode.', error)
        nextRetryAt = Date.now() + RETRY_BACKOFF_MS
        runtimePromise = undefined
        return undefined
      }
    })()
  }
  return runtimePromise
}

export const isXpackLicenseValid = () => currentRuntime()?.getLicense()?.status === 'valid'

export const installXpackRoutes = (router: Router) => {
  const runtime = currentRuntime()
  if (!runtime || initializedRouters.has(router)) {
    return
  }
  runtime.generateRouters(router)
  initializedRouters.add(router)
}

export const encryptWithXpack = async (value: string) => {
  const runtime = currentRuntime() ?? (await loadXpackRuntime())
  if (!runtime) {
    throw new Error('Security runtime is unavailable. Please verify that the backend is running.')
  }
  return runtime.sqlbotEncrypt(value)
}
