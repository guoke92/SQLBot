import { questionApi, type ChatRecord } from '@/api/chat'
import {
  useChatStream,
  type ChatStreamEvent,
  type UseChatStreamOptions,
} from '@/hooks/useChatStream'

type ConversationTurnHandlers = {
  onEvent?: (event: ChatStreamEvent) => boolean | void | Promise<boolean | void>
  onFinish?: (record: ChatRecord) => void | Promise<void>
  onError?: (record: ChatRecord) => void
  onDone?: () => void
}

export const useConversationTurn = (options: UseChatStreamOptions = {}) => {
  const stream = useChatStream(options)

  const run = async (
    chatId: number,
    record: ChatRecord,
    handlers: ConversationTurnHandlers = {}
  ) => {
    const failTurn = (message: string, terminal: boolean) => {
      record.error = message
      if (terminal && record.id) {
        record.finish = true
      }
      handlers.onError?.(record)
    }

    await stream.run(
      (controller) =>
        questionApi.add(
          {
            question: record.question,
            chat_id: chatId,
            clarification_for_record_id: record.clarification_parent_id,
            clarification_answers: record.clarification_answers ?? [],
          },
          controller
        ) as Promise<Response>,
      {
        onEvent: async (event) => {
          if (event.type === 'id') {
            record.id = Number(event.id)
            return
          }
          if (event.type === 'error') {
            failTurn(String(event.content ?? event.msg ?? ''), true)
            return true
          }
          if (event.type === 'finish') {
            record.finish = true
            await handlers.onFinish?.(record)
            return true
          }
          return handlers.onEvent?.(event)
        },
        onHttpError: (event) => {
          failTurn(String(event.msg ?? event.content ?? `HTTP ${event.code ?? 'error'}`), true)
        },
        onTransportError: (error) => {
          const prefix = record.error?.trim() ? `${record.error}\n` : ''
          failTurn(`${prefix}Error:${String(error)}`, false)
        },
        onDone: handlers.onDone,
      }
    )
  }

  return {
    run,
    stop: stream.stop,
    running: stream.running,
  }
}
