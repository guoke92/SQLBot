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
  onTransportError?: (error: unknown) => void
  onDone?: () => void
}

export type UseChatStreamOptions = {
  /** Use json-bigint parse (chart data SSE/REST paths). Default JSON.parse. */
  bigInt?: boolean
}

function parseFrame(raw: string, bigInt: boolean): ChatStreamEvent {
  // Match label used historically: data:{...}\n\n
  const body = raw.replace(/^data:/, '').trim()
  if (bigInt) {
    return JSONBig.parse(body) as ChatStreamEvent
  }
  return JSON.parse(body) as ChatStreamEvent
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

    try {
      const response = await fetchResponse(active)
      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Response body is not readable')
      }
      const decoder = new TextDecoder('utf-8')
      let tempResult = ''

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

        let chunk = decoder.decode(value, { stream: true })
        tempResult += chunk
        const split = tempResult.match(/data:.*}\n\n/g)
        if (split) {
          chunk = split.join('')
          tempResult = tempResult.replace(chunk, '')
        } else {
          continue
        }

        if (!chunk || !chunk.startsWith('data:{')) {
          continue
        }

        for (const str of split) {
          let data: ChatStreamEvent
          try {
            data = parseFrame(str, !!options.bigInt)
          } catch (err) {
            console.error('JSON string:', str)
            throw err
          }

          if (data.code && data.code !== 200) {
            if (handlers.onHttpError) {
              handlers.onHttpError(data)
            } else {
              ElMessage({
                message: data.msg,
                type: 'error',
                showClose: true,
              })
            }
            return
          }

          const shouldStop = await handlers.onEvent?.(data)
          if (shouldStop) {
            return
          }
        }
      }
    } catch (error) {
      if (!stopFlag.value) {
        handlers.onTransportError?.(error)
      }
    } finally {
      running.value = false
      handlers.onDone?.()
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
