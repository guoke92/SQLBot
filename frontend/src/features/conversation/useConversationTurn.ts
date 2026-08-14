import { ref, type Ref } from 'vue'
import {
  runApi,
  parseTurnAnswer,
  turnAnswerToPayload,
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
  // Covers the gap after applySnapshot sets run_id but before SSE running=true.
  const owned: Ref<boolean> = ref(false)

  const applySnapshot = (record: ChatRecord, snapshot: ConversationRunSnapshot) => {
    if (snapshot.record && typeof snapshot.record === 'object') {
      Object.assign(record, snapshot.record)
      const persistedAnswer = (snapshot.record as Record<string, unknown>).answer
      record.turn_answer = parseTurnAnswer(persistedAnswer)
      record.answer = turnAnswerToPayload(persistedAnswer) || record.answer
    }
    record.id = snapshot.chat_record_id
    record.run_id = snapshot.run_id
    record.run_status = snapshot.status
    record.run_event_cursor = snapshot.event_cursor
    record.run_current_node = snapshot.current_node
    record.run_dispatch_attempts = snapshot.dispatch_attempts
    record.run_update_time = snapshot.update_time
    record.run_started_at = snapshot.started_at
    record.run_completed_at = snapshot.completed_at
    record.active_interrupt = snapshot.active_interrupt
    record.interrupts = snapshot.interrupts || []
  }

  const fetchSnapshot = async (runId: string, record: ChatRecord) => {
    let lastError: unknown
    for (let attempt = 0; attempt < 5; attempt++) {
      try {
        const response = await runApi.snapshot(runId)
        const snapshot = ((response as any)?.data || response) as ConversationRunSnapshot
        applySnapshot(record, snapshot)
        return snapshot
      } catch (error) {
        lastError = error
        await new Promise((resolve) => window.setTimeout(resolve, 400 * (attempt + 1)))
      }
    }
    throw lastError
  }

  const observe = async (
    initial: ConversationRunSnapshot,
    record: ChatRecord,
    handlers: ConversationTurnHandlers = {},
    startCursor = initial.event_cursor || 0
  ) => {
    let finishDelivered = false
    let observeDone = false
    const snapshotError = (snapshot: ConversationRunSnapshot, fallback: string) => {
      const recordError = snapshot.record?.error
      return typeof recordError === 'string' ? recordError : snapshot.error_summary || fallback
    }
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
      const reconcileFromRun = async (failedMessage?: string) => {
        try {
          const snapshot = await fetchSnapshot(initial.run_id, record)
          latestStatus = snapshot.status
          if (snapshot.status === 'failed') {
            failTurn(snapshotError(snapshot, failedMessage || 'Conversation failed'), true)
          }
          return snapshot
        } catch {
          return null
        }
      }
      await stream.run((controller) => runApi.events(initial.run_id, cursor, controller), {
        onEvent: async (event) => {
          if (event.cursor != null) {
            record.run_event_cursor = Number(event.cursor)
            cursor = record.run_event_cursor
          }
          if (event.type === 'run_status') {
            latestStatus = event.status as ConversationRunSnapshot['status']
            record.run_status = latestStatus
            record.run_current_node = event.current_node as string | undefined
            record.run_dispatch_attempts = Number(event.dispatch_attempts || 0)
            return false
          }
          if (event.type === 'id') {
            record.id = Number(event.id)
            return
          }
          if (event.type === 'error') {
            const snapshot = await reconcileFromRun(String(event.content ?? event.msg ?? ''))
            return snapshot?.status === 'failed'
          }
          if (event.type === 'finish') {
            // The persisted record, not this transport event, is the final
            // read model. onDone reconciles it before notifying the page.
            return true
          }
          if (event.type === 'clarification') {
            await reconcileFromRun()
            await handlers.onEvent?.(event)
            return true
          }
          return handlers.onEvent?.(event)
        },
        onHttpError: async (event) => {
          const code = Number(event.code || 0)
          if (code === 401 || code === 403) {
            httpFailure = true
            failTurn(String(event.msg ?? event.content ?? `HTTP ${code}`), false)
            return
          }
          await reconcileFromRun()
        },
        onTransportError: async () => {
          await reconcileFromRun()
        },
        onDone: async () => {
          const snapshot = await reconcileFromRun()
          if (!snapshot) return
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

  const withOwnership = async (fn: () => Promise<void>) => {
    if (owned.value) return
    owned.value = true
    try {
      await fn()
    } finally {
      owned.value = false
    }
  }

  const attach = async (record: ChatRecord, handlers: ConversationTurnHandlers = {}) => {
    if (!record.run_id) return
    // Live send/resume/correct already owns the subscription (including the
    // window after applySnapshot but before SSE running flips true).
    if (owned.value || stream.running.value) return
    await withOwnership(async () => {
      const snapshot = await fetchSnapshot(record.run_id!, record)
      if (['queued', 'running'].includes(snapshot.status)) {
        // Replay from zero so a refresh sees the same durable history as first live.
        await observe(snapshot, record, handlers, 0)
      }
    })
  }

  const run = async (
    chatId: number,
    record: ChatRecord,
    handlers: ConversationTurnHandlers = {},
    options: { regenerate?: boolean } = {}
  ) => {
    await withOwnership(async () => {
      const created = await runApi.create({
        question: record.question || '',
        chat_id: chatId,
        regenerate_record_id: options.regenerate ? record.id : undefined,
        route_hint: record.turn_kind,
        reference_record_ids: record.reference_record_ids,
      })
      const snapshot = ((created as any)?.data || created) as ConversationRunSnapshot
      // A run may start emitting before POST /runs returns.  Subscribe from zero
      // so the first live view sees the same durable history as a refresh.
      await observe(snapshot, record, handlers, 0)
    })
  }

  const resume = async (
    record: ChatRecord,
    pending: ConversationInterrupt,
    answers: ResumeAnswer[],
    handlers: ConversationTurnHandlers = {},
    proceedWithAssumptions = false
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
    await withOwnership(async () => {
      try {
        const response = await runApi.resume(runId, pending.interrupt_id, {
          version: pending.version,
          idempotency_key: crypto.randomUUID(),
          answers,
          proceed_with_assumptions: proceedWithAssumptions,
        })
        const snapshot = ((response as any)?.data || response) as ConversationRunSnapshot
        await observe(snapshot, record, handlers, previousCursor)
      } catch (error) {
        await fetchSnapshot(runId, record)
        throw error
      }
    })
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
    await withOwnership(async () => {
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
    })
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
    attach,
    run,
    resume,
    correct,
    detach,
    cancel,
    running: stream.running,
    owned,
  }
}
