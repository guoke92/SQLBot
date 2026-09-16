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

/** Collapse request_clarification tool + wait/confirm into one clarification card. */
export function foldClarificationFlow(items: ProcessItem[]): ProcessItem[] {
  const isClarifyTool = (item: ProcessItem) =>
    item.kind === 'tool' && item.tool?.name === 'request_clarification'

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
    for (let i = group.length - 1; i >= 0; i -= 1) {
      const meta = group[i].meta
      if (meta && typeof meta.interrupt_id === 'string') {
        preferred.meta = { ...meta }
        break
      }
    }
    return preferred
  }

  const out: ProcessItem[] = []
  let group: ProcessItem[] = []
  const flush = () => {
    if (group.length) {
      out.push(mergeGroup(group))
      group = []
    }
  }
  for (const item of items) {
    if (isClarifyTool(item) || item.kind === 'clarification') {
      group.push(item)
      continue
    }
    flush()
    out.push(item)
  }
  flush()
  return out
}

export function replaceItems(items: ProcessItem[]): TimelineMap {
  const map: TimelineMap = new Map()
  for (const item of items) {
    map.set(itemKey(item), item)
  }
  return map
}
