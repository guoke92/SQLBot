<script setup lang="ts">
import { computed } from 'vue'
import 'highlight.js/styles/github.min.css'
import 'github-markdown-css/github-markdown-light.css'
import hljs from 'highlight.js'

const props = defineProps<{
  sql: string
}>()

// API datasources surface "METHOD /path\nparams: {...}" — not SQL. Prefer auto language.
const language = computed(() => {
  const text = (props.sql || '').trim()
  if (!text) return 'sql'
  if (/^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+\S+/i.test(text)) return 'http'
  if (text.startsWith('{') || text.startsWith('[')) return 'json'
  return 'sql'
})

const highlighted = computed(() => {
  const code = props.sql || ''
  try {
    return hljs.highlight(code, { language: language.value, ignoreIllegals: true }).value
  } catch {
    return hljs.highlightAuto(code).value
  }
})
</script>

<template>
  <pre class="hljs">
    <div v-dompurify-html="highlighted"></div>
  </pre>
</template>

<style lang="less">
.hljs {
  overflow: auto;
  padding: 1rem;
  display: block;

  background: rgba(245, 246, 247, 1);
  border: 1px solid rgba(222, 224, 227, 1);
  border-radius: 6px;
}
</style>
