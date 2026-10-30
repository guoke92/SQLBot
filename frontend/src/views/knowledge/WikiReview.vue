<script lang="ts" setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WikiProposal } from '@/api/knowledge'
import WikiDiff from '@/views/knowledge/WikiDiff.vue'

const props = withDefaults(
  defineProps<{
    proposals: WikiProposal[]
    disabled?: boolean
    actions?: boolean
  }>(),
  { actions: true }
)

const emit = defineEmits<{
  accept: []
  reject: []
  supplement: [text: string]
}>()

const { t } = useI18n()

function term(group: string, code: string) {
  if (!code) return ''
  const key = `knowledge.${group}_${code}`
  const text = t(key)
  return text === key ? code : text
}

const note = ref('')
const closed = ref<Record<string, boolean>>({})

const files = computed(() => {
  const grouped = new Map<
    string,
    {
      path: string
      scope: string
      trust: string
      source: string
      diff: string
      claims: { label: string; basis: string; reason: string }[]
    }
  >()
  for (const item of props.proposals) {
    const path = [item.belong, item.page_key].filter(Boolean).join('/') || item.claim_path
    const current = grouped.get(path) || {
      path,
      scope: item.scope || '',
      trust: item.trust || '',
      source: item.source_ref || '',
      diff: '',
      claims: [],
    }
    if (!current.diff && item.diff) current.diff = item.diff
    if (!current.scope && item.scope) current.scope = item.scope
    if (!current.trust && item.trust) current.trust = item.trust
    if (!current.source && item.source_ref) current.source = item.source_ref
    current.claims.push({
      label: [term('wiki_op', item.op), item.detail || item.claim_path].filter(Boolean).join(' '),
      basis: item.basis || '',
      reason: item.reason || '',
    })
    grouped.set(path, current)
  }
  return [...grouped.values()]
})

function sendNote() {
  const text = note.value.trim()
  if (!text || props.disabled) return
  emit('supplement', text)
  note.value = ''
}
</script>

<template>
  <section class="wiki-review">
    <header class="wiki-review-head">
      <strong>{{ t('knowledge.wiki_review_title') }}</strong>
      <span>{{ files.length }}</span>
    </header>
    <article v-for="file in files" :key="file.path" class="wiki-review-file">
      <button type="button" class="file-head" @click="closed[file.path] = !closed[file.path]">
        <span class="chevron">{{ closed[file.path] ? '▸' : '▾' }}</span>
        <span class="path">{{ file.path }}</span>
        <small>
          {{
            [term('wiki_scope', file.scope), term('wiki_trust', file.trust), file.source]
              .filter(Boolean)
              .join(' ')
          }}
        </small>
      </button>
      <div v-show="!closed[file.path]" class="file-body">
        <article
          v-for="(claim, index) in file.claims"
          :key="`${claim.label}-${index}`"
          class="rationale"
        >
          <p class="claim">{{ claim.label }}</p>
          <p v-if="claim.basis">
            <span>{{ t('knowledge.wiki_change_basis') }}</span>
            {{ claim.basis }}
          </p>
          <p v-if="claim.reason">
            <span>{{ t('knowledge.wiki_change_why') }}</span>
            {{ claim.reason }}
          </p>
          <p v-else class="missing">{{ t('knowledge.wiki_change_why_missing') }}</p>
        </article>
        <WikiDiff :diff="file.diff" :path="file.path" />
      </div>
    </article>
    <footer v-if="actions" class="wiki-review-actions">
      <el-button type="primary" :disabled="disabled" @click="emit('accept')">
        {{ t('knowledge.wiki_accept') }}
      </el-button>
      <el-button :disabled="disabled" @click="emit('reject')">
        {{ t('knowledge.wiki_reject') }}
      </el-button>
      <el-input
        v-model="note"
        :disabled="disabled"
        :placeholder="t('knowledge.wiki_supplement')"
        @keydown.enter.exact.prevent="sendNote"
      />
      <el-button :disabled="disabled || !note.trim()" @click="sendNote">
        {{ t('knowledge.wiki_supplement_send') }}
      </el-button>
    </footer>
  </section>
</template>

<style scoped>
.wiki-review {
  margin-top: 12px;
  border: 1px solid var(--ed-border-color);
  border-radius: 10px;
  background: var(--ed-bg-color, #fff);
}

.wiki-review-head,
.file-head,
.wiki-review-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wiki-review-head {
  padding: 10px 12px;
  border-bottom: 1px solid var(--ed-border-color);
}

.wiki-review-file + .wiki-review-file {
  border-top: 1px solid var(--ed-border-color);
}

.file-head {
  width: 100%;
  padding: 8px 12px;
  border: 0;
  background: transparent;
  color: inherit;
  text-align: left;
  cursor: pointer;
}

.path {
  font-weight: 600;
}

.file-head small,
.claim {
  color: var(--ed-text-color-secondary);
  font-size: 12px;
}

.file-body {
  padding: 0 12px 12px;
}

.claim {
  margin: 0 0 6px;
}

.rationale {
  margin: 0 0 8px;
  padding: 8px 10px;
  border-left: 3px solid var(--ed-color-primary);
  border-radius: 6px;
  background: color-mix(in srgb, var(--ed-color-primary) 6%, #fff);
}

.rationale p {
  margin: 0 0 4px;
  white-space: pre-wrap;
}

.rationale span {
  display: inline-block;
  margin-right: 6px;
  color: var(--ed-text-color-secondary);
  font-size: 12px;
}

.missing {
  color: var(--ed-text-color-secondary);
}

.wiki-review-actions {
  padding: 10px 12px;
  border-top: 1px solid var(--ed-border-color);
}

.wiki-review-actions :deep(.el-input) {
  flex: 1;
}
</style>
