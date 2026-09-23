export type ProcessKind =
  | 'thought'
  | 'tool'
  | 'artifact'
  | 'clarification'
  | 'answer'

export type ProcessStatus = 'running' | 'completed' | 'failed' | 'interrupted'

export interface ProcessTool {
  call_id: string
  name: string
  args?: Record<string, unknown>
}

export interface ProcessThought {
  content?: string
  source?: 'model_reasoning' | 'scratchpad' | string
  truncated?: boolean
}

export interface ProcessArtifact {
  dataset_id?: string
  sql?: string
  fields?: string[]
  row_count?: number
  truncated?: boolean
  limit?: number
  preview_rows?: Array<Record<string, unknown>>
}

export interface ProcessAnswer {
  content?: string
}

export interface ProcessItem {
  id: number | string
  sequence?: number
  run_id?: string | null
  record_id?: number | null
  attempt_index?: number
  kind: ProcessKind
  status: ProcessStatus
  title_key?: string
  title_params?: Record<string, unknown>
  title?: string
  summary_key?: string | null
  summary_params?: Record<string, unknown>
  summary?: string
  started_at?: string | null
  finished_at?: string | null
  duration_ms?: number | null
  parent_id?: number | string | null
  tool?: ProcessTool
  thought?: ProcessThought
  artifact?: ProcessArtifact
  answer?: ProcessAnswer
  meta?: Record<string, unknown>
  detail?: Record<string, unknown>
}

export interface ProcessTimeline {
  record_id: number
  run_id?: string | null
  attempt_index?: number
  view?: 'compact' | 'detail'
  items: ProcessItem[]
  total_tokens?: number
  duration?: number | null
  waiting_duration?: number | null
  elapsed_duration?: number | null
  run?: {
    run_id: string
    status?: string
    current_node?: string
    started_at?: string | null
    completed_at?: string | null
  } | null
  attempts?: Array<{
    run_id: string
    status?: string
    current_node?: string
    attempt_index?: number
    started_at?: string | null
    completed_at?: string | null
  }>
}

export type TimelineMap = Map<string, ProcessItem>

export function itemKey(item: Pick<ProcessItem, 'id'> | number | string): string {
  if (typeof item === 'object') return String(item.id)
  return String(item)
}

/** Live process items belong to one ConversationRun attempt. */
export function belongsToRun(item: ProcessItem, runId?: string | null): boolean {
  if (!runId || !item.run_id) return true
  return item.run_id === runId
}

export function itemsForRun(items: ProcessItem[], runId?: string | null): ProcessItem[] {
  if (!runId) return items
  return items.filter((item) => belongsToRun(item, runId))
}

export function upsertItem(map: TimelineMap, item: ProcessItem): TimelineMap {
  const next = new Map(map)
  next.set(itemKey(item), item)
  return next
}

export function removeItem(map: TimelineMap, id: number | string): TimelineMap {
  const next = new Map(map)
  next.delete(String(id))
  return next
}

export function applyDelta(map: TimelineMap, item: ProcessItem): TimelineMap {
  const key = itemKey(item)
  const current = map.get(key)
  if (!current) {
    return upsertItem(map, item)
  }
  const merged: ProcessItem = {
    ...current,
    ...item,
    title: item.title || current.title,
    summary: item.summary || current.summary,
    tool: item.tool ? { ...current.tool, ...item.tool } : current.tool,
    thought: item.thought
      ? {
          ...current.thought,
          ...item.thought,
          // Prefer latest streamed payload; empty string clears intentionally.
          content:
            item.thought.content !== undefined
              ? item.thought.content
              : current.thought?.content,
        }
      : current.thought,
    artifact: item.artifact ? { ...current.artifact, ...item.artifact } : current.artifact,
    answer: item.answer
      ? {
          ...current.answer,
          ...item.answer,
          content: item.answer.content ?? current.answer?.content,
        }
      : current.answer,
    meta: item.meta ? { ...current.meta, ...item.meta } : current.meta,
  }
  return upsertItem(map, merged)
}

export function extractProcessItem(event: Record<string, unknown>): ProcessItem | undefined {
  const nested = event.item
  const raw = nested && typeof nested === 'object' ? nested : event
  const candidate = raw as Partial<ProcessItem>
  if (candidate.id == null || !candidate.kind) return undefined
  return candidate as ProcessItem
}

export function sortedItems(map: TimelineMap): ProcessItem[] {
  return foldClarificationFlow(
    [...map.values()].sort((a, b) => {
      const left = Number(a.sequence ?? a.id)
      const right = Number(b.sequence ?? b.id)
      return left - right
    })
  )
}

/**
 * Anchor clarification interrupts onto the ``request_clarification`` tool row
 * (or an existing clarification span). Cards render inline in the thought
 * chain — never as a detached footer list.
 */
export function bindClarificationInterrupts(
  items: ProcessItem[],
  interrupts: Array<{
    interrupt_id: string
    version: number
    status: string
    payload?: unknown
  }> = []
): ProcessItem[] {
  const active = interrupts.filter((item) => item.status !== 'cancelled')
  if (!active.length) return items

  const owned = new Set<string>()
  for (const item of items) {
    if (item.kind !== 'clarification') continue
    const id = item.meta?.interrupt_id
    if (typeof id === 'string' && id) owned.add(id)
  }

  const unbound = active.filter((item) => !owned.has(item.interrupt_id))
  if (!unbound.length) return items

  const next = items.map((item) => ({ ...item }))
  const claimedTools = new Set<number>()

  for (const interrupt of unbound) {
    const toolIdx = next.findIndex(
      (item, index) =>
        !claimedTools.has(index) &&
        item.kind === 'tool' &&
        item.tool?.name === 'request_clarification'
    )
    if (toolIdx >= 0) {
      claimedTools.add(toolIdx)
      const tool = next[toolIdx]
      next[toolIdx] = {
        ...tool,
        kind: 'clarification',
        status: interrupt.status === 'open' ? 'running' : 'completed',
        title_key: 'chat.timeline.clarification',
        summary_key:
          interrupt.status === 'open'
            ? 'chat.summary.clarification_waiting'
            : 'chat.summary.clarification_confirmed',
        meta: {
          ...(tool.meta || {}),
          interrupt_id: interrupt.interrupt_id,
          version: interrupt.version,
          clarification_card: interrupt.payload,
        },
      }
      delete next[toolIdx].tool
      continue
    }

    const bareIdx = next.findIndex(
      (item) =>
        item.kind === 'clarification' &&
        !(typeof item.meta?.interrupt_id === 'string' && item.meta.interrupt_id)
    )
    if (bareIdx >= 0) {
      const bare = next[bareIdx]
      next[bareIdx] = {
        ...bare,
        status:
          interrupt.status === 'open'
            ? 'running'
            : bare.status === 'running'
              ? 'completed'
              : bare.status,
        summary_key:
          interrupt.status === 'open'
            ? 'chat.summary.clarification_waiting'
            : bare.summary_key || 'chat.summary.clarification_confirmed',
        meta: {
          ...(bare.meta || {}),
          interrupt_id: interrupt.interrupt_id,
          version: interrupt.version,
          clarification_card: interrupt.payload ?? bare.meta?.clarification_card,
        },
      }
      continue
    }

    // No tool/span anchor left.
    // Do not invent a card-only chain while the timeline is still empty
    // (chat switch / history hydrate) — that flashes every interrupt at the
    // bottom before the real thought chain arrives. Only append an *open*
    // interrupt once some process rows already exist (live pause fallback).
    if (next.length === 0 || interrupt.status !== 'open') {
      continue
    }
    next.push({
      id: `interrupt:${interrupt.interrupt_id}`,
      sequence: Number(next[next.length - 1]?.sequence ?? next.length) + 1,
      kind: 'clarification',
      status: 'running',
      title_key: 'chat.timeline.clarification',
      summary_key: 'chat.summary.clarification_waiting',
      meta: {
        interrupt_id: interrupt.interrupt_id,
        version: interrupt.version,
        clarification_card: interrupt.payload,
      },
    })
  }

  // fold merges consecutive tool + clarification for the same interrupt_id;
  // do not blanket-drop leftover clarify tools (multi-round may still be open).
  return foldClarificationFlow(next)
}

export type NarrativeBlock =
  | { type: 'thought'; key: string; item: ProcessItem }
  | { type: 'tool'; key: string; item: ProcessItem; artifacts: ProcessItem[] }
  | { type: 'clarification'; key: string; item: ProcessItem }

/** Project audit items into Cursor-style narrative blocks for inline chat. */
export function projectNarrative(items: ProcessItem[]): NarrativeBlock[] {
  const used = new Set<string>()
  const out: NarrativeBlock[] = []
  for (const item of items) {
    const key = itemKey(item)
    if (used.has(key)) continue
    if (item.kind === 'answer') continue
    if (item.kind === 'thought') {
      const body = String(item.thought?.content || '').trim()
      // Hide completed empty thoughts (final-answer rounds without reasoning).
      if (item.status !== 'running' && !body) continue
      out.push({ type: 'thought', key, item })
      continue
    }
    if (item.kind === 'clarification') {
      out.push({ type: 'clarification', key, item })
      continue
    }
    if (item.kind === 'tool') {
      const artifacts = items.filter(
        (candidate) =>
          candidate.kind === 'artifact' && String(candidate.parent_id ?? '') === String(item.id)
      )
      for (const artifact of artifacts) used.add(itemKey(artifact))
      out.push({ type: 'tool', key, item, artifacts })
      continue
    }
    if (item.kind === 'artifact') {
      out.push({ type: 'tool', key, item, artifacts: [] })
    }
  }
  return out
}

export function narrativeDurationMs(blocks: NarrativeBlock[]): number {
  return blocks.reduce((sum, block) => {
    const own = Number(block.item.duration_ms || 0)
    if (block.type !== 'tool') return sum + own
    const child = block.artifacts.reduce((acc, item) => acc + Number(item.duration_ms || 0), 0)
    return sum + own + child
  }, 0)
}

/** Processing time only: skip clarification waits; include in-flight thought/tool spans. */
export function processingDurationMs(blocks: NarrativeBlock[], nowMs: number): number {
  let ms = 0
  const addItem = (item: ProcessItem) => {
    if (item.duration_ms != null && item.status !== 'running') {
      ms += Number(item.duration_ms) || 0
      return
    }
    if (!item.started_at) return
    const start = Date.parse(item.started_at)
    if (Number.isNaN(start)) return
    const end = item.finished_at ? Date.parse(item.finished_at) : nowMs
    if (Number.isNaN(end)) return
    ms += Math.max(0, end - start)
  }
  for (const block of blocks) {
    if (block.type === 'clarification') continue
    addItem(block.item)
    if (block.type === 'tool') {
      for (const artifact of block.artifacts) addItem(artifact)
    }
  }
  return ms
}

export const THOUGHT_SNIPPET_CHARS = 80

export function thoughtSnippet(content: string, limit = THOUGHT_SNIPPET_CHARS): string {
  const plain = String(content || '').replace(/\s+/g, ' ').trim()
  if (!plain) return ''
  const sentence = plain.split(/[。！？.!?]/)[0]?.trim() || plain
  if (sentence.length <= limit) return sentence
  return sentence.slice(0, limit)
}

/** Collapse tool + wait/confirm for the same interrupt_id into one card.
 * Different rounds stay separate. A lone request_clarification tool is left as a tool.
 */
export function foldClarificationFlow(items: ProcessItem[]): ProcessItem[] {
  const isClarifyTool = (item: ProcessItem) =>
    item.kind === 'tool' && item.tool?.name === 'request_clarification'

  const interruptIdOf = (item: ProcessItem): string | undefined => {
    const id = item.meta?.interrupt_id
    return typeof id === 'string' && id.trim() ? id.trim() : undefined
  }

  const mergeGroup = (group: ProcessItem[]): ProcessItem => {
    let preferred: ProcessItem | undefined
    for (const status of ['completed', 'running', 'interrupted', 'failed'] as ProcessStatus[]) {
      for (let i = group.length - 1; i >= 0; i -= 1) {
        const item = group[i]
        if (item.kind === 'clarification' && item.status === status) {
          preferred = { ...item }
          break
        }
      }
      if (preferred) break
    }
    if (!preferred) {
      preferred = { ...(group.find((item) => item.kind === 'clarification') || group[group.length - 1]) }
      preferred.kind = 'clarification'
    }
    const starts = group.map((item) => item.started_at).filter(Boolean) as string[]
    const finishes = group.map((item) => item.finished_at).filter(Boolean) as string[]
    if (starts.length) preferred.started_at = starts[0]
    if (finishes.length) preferred.finished_at = finishes[finishes.length - 1]
    if (preferred.started_at && preferred.finished_at) {
      const a = Date.parse(preferred.started_at)
      const b = Date.parse(preferred.finished_at)
      if (!Number.isNaN(a) && !Number.isNaN(b)) {
        preferred.duration_ms = Math.max(0, b - a)
      }
    }
    if (preferred.status === 'interrupted') {
      preferred.status = 'completed'
      preferred.summary_key = 'chat.summary.clarification_confirmed'
      preferred.summary = preferred.summary || undefined
    }
    if (preferred.status === 'running') {
      preferred.summary_key = 'chat.summary.clarification_waiting'
    } else if (
      preferred.status === 'completed' &&
      (!preferred.summary_key ||
        ['chat.audit.processing', 'chat.audit.step_interrupted', 'chat.summary.tool_ok'].includes(
          preferred.summary_key
        ))
    ) {
      preferred.summary_key = 'chat.summary.clarification_confirmed'
    }
    delete preferred.tool
    let bestMeta: ProcessItem['meta'] | undefined
    for (let i = group.length - 1; i >= 0; i -= 1) {
      const meta = group[i].meta
      if (!meta || typeof meta.interrupt_id !== 'string') continue
      if (!bestMeta || meta.clarification_card) {
        bestMeta = { ...meta }
        if (meta.clarification_card) break
      }
    }
    if (bestMeta) preferred.meta = bestMeta
    return preferred
  }

  const out: ProcessItem[] = []
  let pendingTools: ProcessItem[] = []
  let index = 0

  const flushTools = () => {
    out.push(...pendingTools)
    pendingTools = []
  }

  while (index < items.length) {
    const item = items[index]
    if (isClarifyTool(item)) {
      pendingTools.push(item)
      index += 1
      continue
    }
    if (item.kind === 'clarification') {
      let groupKey = interruptIdOf(item)
      const group: ProcessItem[] = [...pendingTools, item]
      pendingTools = []
      index += 1
      while (index < items.length) {
        const next = items[index]
        if (isClarifyTool(next)) {
          let look = index + 1
          while (look < items.length && isClarifyTool(items[look])) look += 1
          if (look < items.length && items[look].kind === 'clarification') {
            const nextKey = interruptIdOf(items[look])
            if (groupKey && nextKey && nextKey !== groupKey) break
            while (index < look) {
              group.push(items[index])
              index += 1
            }
            continue
          }
          break
        }
        if (next.kind === 'clarification') {
          const nextKey = interruptIdOf(next)
          if (groupKey && nextKey && nextKey !== groupKey) break
          if (nextKey && !groupKey) groupKey = nextKey
          group.push(next)
          index += 1
          continue
        }
        break
      }
      out.push(mergeGroup(group))
      continue
    }
    flushTools()
    out.push(item)
    index += 1
  }
  flushTools()
  return out
}

export function replaceItems(items: ProcessItem[]): TimelineMap {
  const map: TimelineMap = new Map()
  for (const item of items) {
    map.set(itemKey(item), item)
  }
  return map
}
