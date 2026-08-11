/**
 * Single SSE frame reader for chat scenarios.
 *
 * Replaces duplicated getReader + data:{} split scaffolding
 * in Chart/Analysis/Predict/Recommend/Config answer components.
 * Domain handlers remain scenario-specific; only network/parse lives here.
 */
import { ref, type Ref } from 'vue'
import JSONBig from 'json-bigint'

export type ChatStreamEvent = {
  type?: string
  code?: number
  msg?: string
  content?: any
  reasoning_content?: any
  id?: any
  [key: string]: any
}

export type ChatStreamHandlers = {
  /** Return true to stop reading after this event. */
  onEvent?: (data: ChatStreamEvent) => boolean | void | Promise<boolean | void>
  onHttpError?: (data: ChatStreamEvent) => void
  onTransportError?: (error: unknown) => void | Promise<void>
  onDone?: () => void | Promise<void>
}

export type UseChatStreamOptions = {
  /** Use json-bigint parse (chart data SSE/REST paths). Default JSON.parse. */
  bigInt?: boolean
}

function parseFrame(raw: string, bigInt: boolean): ChatStreamEvent {
  const body = raw
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trimStart())
    .join('\n')
    .trim()
  if (!body) {
    throw new Error('SSE frame has no data payload')
  }
  if (bigInt) {
    return JSONBig.parse(body) as ChatStreamEvent
  }
  return JSON.parse(body) as ChatStreamEvent
}

function parseHttpError(response: Response, text: string): ChatStreamEvent {
  try {
    const parsed = JSON.parse(text)
    if (parsed && typeof parsed === 'object') {
      const detail = parsed.msg || parsed.message || parsed.detail
      return {
        ...parsed,
        code: parsed.code || response.status,
        msg:
          typeof detail === 'string'
            ? detail
            : detail
              ? JSON.stringify(detail)
              : response.statusText,
      }
    }
  } catch {
    // Fall through to the normalized text response.
  }
  return {
    code: response.status,
    msg: text.trim() || response.statusText || `HTTP ${response.status}`,
  }
}

/**
 * Shared AbortController + reader loop.
 */
export function useChatStream(options: UseChatStreamOptions = {}) {
  const stopFlag: Ref<boolean> = ref(false)
  const running: Ref<boolean> = ref(false)
  let controller: AbortController | undefined

  function stop() {
    stopFlag.value = true
    controller?.abort()
    running.value = false
  }

  function createController(): AbortController {
    controller = new AbortController()
    return controller
  }

  /**
   * @param fetchResponse factory that should cancel via the AbortController
   *   returned by createController() (or pass controller into API).
   */
  async function run(
    fetchResponse: (controller: AbortController) => Promise<Response>,
    handlers: ChatStreamHandlers = {}
  ): Promise<void> {
    stopFlag.value = false
    running.value = true
    if (!controller || controller.signal.aborted) {
      controller = new AbortController()
    }
    const active = controller

    const dispatchHttpError = (data: ChatStreamEvent) => {
      if (handlers.onHttpError) {
        handlers.onHttpError(data)
        return
      }
      ElMessage({
        message: data.msg,
        type: 'error',
        showClose: true,
      })
    }

    try {
      const response = await fetchResponse(active)
      if (!response.ok) {
        dispatchHttpError(parseHttpError(response, await response.text()))
        return
      }

      const contentType = response.headers.get('content-type') || ''
      if (contentType.includes('application/json')) {
        dispatchHttpError(parseHttpError(response, await response.text()))
        return
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Response body is not readable')
      }
      const decoder = new TextDecoder('utf-8')
      let tempResult = ''

      const dispatchFrame = async (frame: string): Promise<boolean> => {
        if (!frame.trim() || frame.trimStart().startsWith(':')) {
          return false
        }
        let data: ChatStreamEvent
        try {
          data = parseFrame(frame, !!options.bigInt)
        } catch (err) {
          console.error('SSE frame:', frame)
          throw err
        }

        if (data.code && data.code !== 200) {
          dispatchHttpError(data)
          return true
        }
        return !!(await handlers.onEvent?.(data))
      }

      while (true) {
        if (stopFlag.value) {
          active.abort()
          try {
            await reader.cancel()
          } catch {
            /* ignore */
          }
          break
        }

        const { done, value } = await reader.read()
        if (done) {
          break
        }

        tempResult += decoder.decode(value, { stream: true })
        tempResult = tempResult.replace(/\r\n/g, '\n')
        let separator = tempResult.indexOf('\n\n')
        while (separator >= 0) {
          const frame = tempResult.slice(0, separator)
          tempResult = tempResult.slice(separator + 2)
          if (await dispatchFrame(frame)) {
            return
          }
          separator = tempResult.indexOf('\n\n')
        }
      }

      tempResult += decoder.decode()
      if (tempResult.trim() && (await dispatchFrame(tempResult))) {
        return
      }
    } catch (error) {
      if (!stopFlag.value) {
        await handlers.onTransportError?.(error)
      }
    } finally {
      running.value = false
      await handlers.onDone?.()
    }
  }

  return {
    stopFlag,
    running,
    stop,
    run,
    createController,
    get controller() {
      return controller
    },
  }
}

export default useChatStream
