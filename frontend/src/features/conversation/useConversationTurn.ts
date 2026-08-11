import {
  runApi,
  type ChatRecord,
  type ConversationInterrupt,
  type ConversationRunSnapshot,
  type ResumeAnswer,
} from '@/api/chat'
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

  const applySnapshot = (record: ChatRecord, snapshot: ConversationRunSnapshot) => {
    if (snapshot.record && typeof snapshot.record === 'object') {
      Object.assign(record, snapshot.record)
    }
    record.id = snapshot.chat_record_id
    record.run_id = snapshot.run_id
    record.run_status = snapshot.status
    record.run_event_cursor = snapshot.event_cursor
    record.active_interrupt = snapshot.active_interrupt
    record.interrupts = snapshot.interrupts || []
  }

  const fetchSnapshot = async (runId: string, record: ChatRecord) => {
    const response = await runApi.snapshot(runId)
    const snapshot = ((response as any)?.data || response) as ConversationRunSnapshot
    applySnapshot(record, snapshot)
    return snapshot
  }

  const observe = async (
    initial: ConversationRunSnapshot,
    record: ChatRecord,
    handlers: ConversationTurnHandlers = {},
    startCursor = initial.event_cursor || 0
  ) => {
    let finishDelivered = false
    let observeDone = false
    const failTurn = (message: string, terminal: boolean) => {
      record.error = message
      if (terminal && record.id) {
        record.finish = true
      }
      handlers.onError?.(record)
    }

    applySnapshot(record, initial)

    let cursor = startCursor
    while (!observeDone) {
      let latestStatus = record.run_status || initial.status
      let httpFailure = false
      await stream.run((controller) => runApi.events(initial.run_id, cursor, controller), {
        onEvent: async (event) => {
          if (event.cursor != null) {
            record.run_event_cursor = Number(event.cursor)
            cursor = record.run_event_cursor
          }
          if (event.type === 'id') {
            record.id = Number(event.id)
            return
          }
          if (event.type === 'error') {
            failTurn(String(event.content ?? event.msg ?? ''), false)
            const snapshot = await fetchSnapshot(initial.run_id, record)
            latestStatus = snapshot.status
            if (snapshot.status === 'failed') {
              failTurn(snapshot.error_summary || String(event.content ?? event.msg ?? ''), true)
              return true
            }
            return false
          }
          if (event.type === 'finish') {
            // The persisted record, not this transport event, is the final
            // read model. onDone reconciles it before notifying the page.
            return true
          }
          if (event.type === 'clarification') {
            const snapshot = await fetchSnapshot(initial.run_id, record)
            latestStatus = snapshot.status
            await handlers.onEvent?.(event)
            return true
          }
          return handlers.onEvent?.(event)
        },
        onHttpError: (event) => {
          httpFailure = true
          failTurn(String(event.msg ?? event.content ?? `HTTP ${event.code ?? 'error'}`), false)
        },
        onTransportError: async () => {
          // Transport is only a subscription. Reconcile from the durable run
          // instead of turning an SSE disconnect into a business failure.
          const snapshot = await fetchSnapshot(initial.run_id, record)
          latestStatus = snapshot.status
          if (snapshot.status === 'failed') {
            failTurn(snapshot.error_summary || 'Conversation failed', true)
          }
        },
        onDone: async () => {
          const snapshot = await fetchSnapshot(initial.run_id, record)
          latestStatus = snapshot.status
          if (['succeeded', 'degraded', 'failed', 'cancelled'].includes(snapshot.status)) {
            record.finish = true
          }
          if (
            !finishDelivered &&
            ['awaiting_input', 'succeeded', 'degraded', 'failed', 'cancelled'].includes(
              snapshot.status
            )
          ) {
            finishDelivered = true
            await handlers.onFinish?.(record)
          }
        },
      })
      if (stream.stopFlag.value || httpFailure) {
        observeDone = true
        break
      }
      if (
        ['awaiting_input', 'succeeded', 'degraded', 'failed', 'cancelled'].includes(latestStatus)
      ) {
        observeDone = true
        break
      }
      // SSE is a resumable subscription. A clean or broken transport close
      // while the durable run is still active reconnects from the last cursor.
      await new Promise((resolve) => window.setTimeout(resolve, 400))
      if (stream.stopFlag.value) break
      cursor = record.run_event_cursor || cursor
    }
    handlers.onDone?.()
  }

  const run = async (
    chatId: number,
    record: ChatRecord,
    handlers: ConversationTurnHandlers = {}
  ) => {
    const created = await runApi.create({
      question: record.question || '',
      chat_id: chatId,
      regenerate_record_id: record.regenerate_record_id,
    })
    const snapshot = ((created as any)?.data || created) as ConversationRunSnapshot
    // A run may start emitting before POST /runs returns.  Subscribe from zero
    // so the first live view sees the same durable history as a refresh.
    await observe(snapshot, record, handlers, 0)
  }

  const resume = async (
    record: ChatRecord,
    pending: ConversationInterrupt,
    answers: ResumeAnswer[],
    handlers: ConversationTurnHandlers = {}
  ) => {
    if (!record.run_id) throw new Error('Conversation run is missing')
    const runId = record.run_id
    const previousCursor = record.run_event_cursor || 0
    const localInterrupt = record.interrupts.find(
      (item) => item.interrupt_id === pending.interrupt_id
    )
    if (localInterrupt) {
      localInterrupt.status = 'consumed'
      localInterrupt.answers = answers
    }
    record.active_interrupt = undefined
    record.run_status = 'running'
    try {
      const response = await runApi.resume(runId, pending.interrupt_id, {
        version: pending.version,
        idempotency_key: crypto.randomUUID(),
        answers,
      })
      const snapshot = ((response as any)?.data || response) as ConversationRunSnapshot
      await observe(snapshot, record, handlers, previousCursor)
    } catch (error) {
      await fetchSnapshot(runId, record)
      throw error
    }
  }

  const correct = async (
    record: ChatRecord,
    source: ConversationInterrupt,
    answer: ResumeAnswer,
    supersedesEvidenceId: string,
    handlers: ConversationTurnHandlers = {}
  ) => {
    if (!record.run_id) throw new Error('Conversation run is missing')
    const runId = record.run_id
    const previousCursor = record.run_event_cursor || 0
    record.active_interrupt = undefined
    record.run_status = 'running'
    try {
      const response = await runApi.correct(runId, source.interrupt_id, {
        version: source.version,
        idempotency_key: crypto.randomUUID(),
        supersedes_evidence_id: supersedesEvidenceId,
        answer,
      })
      const snapshot = ((response as any)?.data || response) as ConversationRunSnapshot
      await observe(snapshot, record, handlers, previousCursor)
    } catch (error) {
      await fetchSnapshot(runId, record)
      throw error
    }
  }

  const detach = () => {
    stream.stop()
  }

  const cancel = async (record: ChatRecord) => {
    detach()
    if (!record.run_id) return
    const response = await runApi.cancel(record.run_id)
    const snapshot = ((response as any)?.data || response) as ConversationRunSnapshot
    applySnapshot(record, snapshot)
  }

  return {
    run,
    resume,
    correct,
    detach,
    cancel,
    running: stream.running,
  }
}
