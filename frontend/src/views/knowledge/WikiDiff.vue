<script lang="ts" setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  diff: string
  path?: string
}>()

const { t } = useI18n()
const mode = ref<'unified' | 'split'>('unified')

type DiffLine = { kind: 'add' | 'del' | 'context' | 'hunk'; text: string }
type SplitRow = {
  left: string
  right: string
  leftKind: 'del' | 'context' | 'empty' | 'hunk'
  rightKind: 'add' | 'context' | 'empty' | 'hunk'
}

const lines = computed<DiffLine[]>(() => {
  const parsed: DiffLine[] = []
  for (const line of (props.diff || '').split('\n')) {
    if (!line || line.startsWith('+++') || line.startsWith('---') || line.startsWith('diff ')) {
      continue
    }
    if (line.startsWith('@@')) {
      parsed.push({ kind: 'hunk', text: line })
      continue
    }
    if (line.startsWith('+')) parsed.push({ kind: 'add', text: line.slice(1) })
    else if (line.startsWith('-')) parsed.push({ kind: 'del', text: line.slice(1) })
    else if (!line.startsWith('\\')) {
      parsed.push({ kind: 'context', text: line.startsWith(' ') ? line.slice(1) : line })
    }
  }
  return parsed
})

const splitRows = computed<SplitRow[]>(() => {
  const rows: SplitRow[] = []
  let index = 0
  const source = lines.value
  while (index < source.length) {
    const line = source[index]
    if (line.kind === 'hunk' || line.kind === 'context') {
      rows.push({
        left: line.text,
        right: line.text,
        leftKind: line.kind,
        rightKind: line.kind,
      })
      index += 1
      continue
    }
    const removed: string[] = []
    const added: string[] = []
    while (index < source.length && source[index].kind === 'del') {
      removed.push(source[index].text)
      index += 1
    }
    while (index < source.length && source[index].kind === 'add') {
      added.push(source[index].text)
      index += 1
    }
    const count = Math.max(removed.length, added.length)
    for (let row = 0; row < count; row += 1) {
      rows.push({
        left: removed[row] ?? '',
        right: added[row] ?? '',
        leftKind: removed[row] !== undefined ? 'del' : 'empty',
        rightKind: added[row] !== undefined ? 'add' : 'empty',
      })
    }
  }
  return rows
})
</script>

<template>
  <section v-if="lines.length" class="wiki-diff">
    <header class="wiki-diff-bar">
      <span v-if="path" class="wiki-diff-path">{{ path }}</span>
      <span class="modes">
        <button type="button" :class="{ on: mode === 'unified' }" @click="mode = 'unified'">
          {{ t('knowledge.wiki_diff_unified') }}
        </button>
        <button type="button" :class="{ on: mode === 'split' }" @click="mode = 'split'">
          {{ t('knowledge.wiki_diff_split') }}
        </button>
      </span>
    </header>
    <ol v-if="mode === 'unified'">
      <li v-for="(line, index) in lines" :key="index" :class="line.kind">
        <span class="mark">{{ line.kind === 'add' ? '+' : line.kind === 'del' ? '−' : ' ' }}</span>
        <span class="text">{{ line.text || ' ' }}</span>
      </li>
    </ol>
    <div v-else class="split">
      <div class="col-head">{{ t('knowledge.wiki_diff_before') }}</div>
      <div class="col-head">{{ t('knowledge.wiki_diff_after') }}</div>
      <template v-for="(row, index) in splitRows" :key="index">
        <div class="cell" :class="row.leftKind">{{ row.left || ' ' }}</div>
        <div class="cell" :class="row.rightKind">{{ row.right || ' ' }}</div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.wiki-diff {
  overflow: auto;
  border: 1px solid var(--ed-border-color);
  border-radius: 8px;
  background: var(--ed-color-neutral-light-9, #f7f8fa);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 18px;
}

.wiki-diff-bar {
  position: sticky;
  top: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 10px;
  border-bottom: 1px solid var(--ed-border-color);
  background: var(--ed-bg-color, #fff);
  font-family: inherit;
}

.wiki-diff-path {
  font-weight: 600;
}

.modes {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.modes button {
  border: 1px solid var(--ed-border-color);
  border-radius: 6px;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font: inherit;
  padding: 2px 8px;
}

.modes button.on {
  border-color: var(--ed-color-primary);
  color: var(--ed-color-primary);
}

ol {
  margin: 0;
  padding: 4px 0;
  list-style: none;
}

li {
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr);
  padding: 0 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.mark {
  color: var(--ed-text-color-secondary);
}

.add {
  background: color-mix(in srgb, var(--ed-color-success, #00b42a) 16%, transparent);
}

.del {
  background: color-mix(in srgb, var(--ed-color-danger, #f53f3f) 16%, transparent);
}

.hunk {
  color: var(--ed-text-color-secondary);
  background: color-mix(in srgb, var(--ed-color-primary) 8%, transparent);
}

.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.col-head,
.cell {
  padding: 0 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.col-head {
  padding: 4px 8px;
  color: var(--ed-text-color-secondary);
  background: var(--ed-bg-color, #fff);
  font-weight: 600;
}

.cell:nth-child(odd),
.col-head:first-child {
  border-right: 1px solid var(--ed-border-color);
}

.empty {
  background: color-mix(in srgb, var(--ed-text-color-secondary) 6%, transparent);
}
</style>
