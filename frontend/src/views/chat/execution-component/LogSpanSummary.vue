<script setup lang="ts">
import BaseContent from './BaseContent.vue'
import { type ChatLogHistoryItem } from '@/api/chat.ts'
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    item?: ChatLogHistoryItem
    error?: string
  }>(),
  {
    item: undefined,
    error: '',
  }
)

function asSpan(msg: any): Record<string, any> | null {
  if (!msg || typeof msg !== 'object') return null
  if (msg.sqlbot_span) return msg
  return null
}

const span = computed(() => asSpan(props.item?.message))
const payload = computed(() => {
  const s = span.value
  if (!s) return {}
  const p = s.payload
  return p && typeof p === 'object' ? p : {}
})

const lines = computed(() => {
  const out: string[] = []
  const s = span.value || {}
  const p = payload.value as Record<string, any>
  if (s.graph_node) out.push(`node: ${s.graph_node}`)
  if (s.brief) out.push(String(s.brief))
  if (p.decision) out.push(`decision: ${p.decision}`)
  if (p.path) out.push(`path: ${p.path}`)
  if (p.used_llm !== undefined) out.push(`llm: ${p.used_llm ? 'yes' : 'no'}`)
  if (p.chars !== undefined) out.push(`chars: ${p.chars}`)
  if (p.empty) out.push('empty analysis')
  const resolved = p.resolved
  if (resolved && typeof resolved === 'object') {
    const keys = Object.keys(resolved)
    out.push(`resolved: ${keys.length ? keys.join(', ') : '—'}`)
  }
  const cands = p.candidates
  if (Array.isArray(cands) && cands.length) {
    out.push(`candidates: ${cands.slice(0, 8).join('、')}`)
  }
  // bindings public keys
  const bindKeys = Object.keys(p).filter(
    (k) => !['resolved', 'candidates', 'decision', 'path', 'used_llm', 'chars', 'empty', 'source', 'has_analysis', 'repair', 'step_index'].includes(k)
  )
  for (const k of bindKeys.slice(0, 12)) {
    const v = p[k]
    if (v !== undefined && typeof v !== 'object') out.push(`${k}: ${v}`)
  }
  if (Array.isArray(p._notes)) {
    for (const n of p._notes.slice(0, 6)) out.push(String(n))
  }
  return out
})
</script>

<template>
  <BaseContent class="base-container">
    <template v-if="item?.error">
      {{ error || 'error' }}
    </template>
    <template v-else>
      <div class="span-lines">
        <div v-for="(line, i) in lines" :key="i" class="span-line">{{ line }}</div>
        <div v-if="!lines.length" class="span-line muted">—</div>
      </div>
    </template>
  </BaseContent>
</template>

<style scoped lang="less">
.span-lines {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.span-line {
  color: #646a73;
  font-size: 13px;
  line-height: 20px;
  font-weight: 400;
  word-break: break-all;
  &.muted {
    color: #bbbfc4;
  }
}
</style>
