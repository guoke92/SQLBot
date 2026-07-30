<script setup lang="ts">
import BaseContent from './BaseContent.vue'
import { type ChatLogHistoryItem } from '@/api/chat.ts'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import SQLComponent from '@/views/chat/component/SQLComponent.vue'

const props = withDefaults(
  defineProps<{
    item?: ChatLogHistoryItem | Record<string, any>
    error?: string
  }>(),
  {
    item: undefined,
    error: '',
  }
)

const { t } = useI18n()

const message = computed<Record<string, any>>(() => {
  const raw = props.item?.message
  if (raw == null) {
    return {}
  }
  if (typeof raw === 'string') {
    try {
      const parsed = JSON.parse(raw)
      return typeof parsed === 'object' && parsed !== null ? parsed : { result: raw }
    } catch {
      return { result: raw }
    }
  }
  if (typeof raw === 'object') {
    return raw as Record<string, any>
  }
  return { result: String(raw) }
})

const details = computed<Record<string, any>>(() => {
  if (message.value.sqlbot_span && typeof message.value.payload === 'object') {
    return message.value.payload || {}
  }
  return message.value
})

const name = computed(() => {
  if (details.value.kind === 'agent' || details.value.role === 'agent') {
    return t('chat.log.AGENT_STEP')
  }
  return details.value.name || details.value.tool || t('chat.log.TOOL_CALL')
})

const ok = computed(() => {
  if (typeof details.value.ok === 'boolean') {
    return details.value.ok
  }
  return true
})

const argsText = computed(() => formatJson(details.value.args ?? details.value.arguments))
const resultText = computed(() => formatJson(details.value.result ?? details.value.content))
const errorText = computed(() => {
  if (!props.item?.error) {
    return ''
  }
  const result = details.value.result
  if (result && typeof result === 'object' && result.error) {
    return String(result.error)
  }
  return props.error || t('chat.error')
})
const contentText = computed(() => {
  if (details.value.kind === 'agent' || details.value.role === 'agent') {
    return formatJson(details.value.content ?? details.value.preview ?? '')
  }
  return ''
})

function formatJson(value: unknown): string {
  if (value == null || value === '') {
    return ''
  }
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (
      (trimmed.startsWith('{') && trimmed.endsWith('}')) ||
      (trimmed.startsWith('[') && trimmed.endsWith(']'))
    ) {
      try {
        return JSON.stringify(JSON.parse(trimmed), null, 2)
      } catch {
        return value
      }
    }
    return value
  }
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}
</script>

<template>
  <BaseContent class="base-container">
    <div class="item-list flex-gap-fallback flex-col">
      <div class="inner-title">
        {{ name }}
        <span v-if="details.kind === 'agent'" class="muted"> · agent</span>
        <span v-else-if="ok" class="ok"> · ok</span>
        <span v-else class="fail"> · fail</span>
      </div>
      <div v-if="errorText" class="error-text">{{ errorText }}</div>
      <div v-if="contentText" class="inner-item flex-gap-fallback flex-col">
        <div class="inner-item-title">content</div>
        <div class="inner-item-description">
          <SQLComponent :sql="contentText" />
        </div>
      </div>
      <div v-if="argsText" class="inner-item flex-gap-fallback flex-col">
        <div class="inner-item-title">args</div>
        <div class="inner-item-description">
          <SQLComponent :sql="argsText" />
        </div>
      </div>
      <div v-if="resultText" class="inner-item flex-gap-fallback flex-col">
        <div class="inner-item-title">result</div>
        <div class="inner-item-description">
          <SQLComponent :sql="resultText" />
        </div>
      </div>
    </div>
  </BaseContent>
</template>

<style scoped lang="less">
.inner-title {
  color: #646a73;
  font-size: 12px;
  line-height: 20px;
  font-weight: 500;
  vertical-align: middle;
  .ok {
    color: #34c759;
  }
  .fail {
    color: #f54a45;
  }
  .muted {
    color: #8f959e;
  }
}
.error-text {
  color: #f54a45;
  font-size: 12px;
  line-height: 20px;
}
.item-list {
  display: flex;
  flex-direction: column;
  --gap-size: 8px;
  gap: 8px;
  align-items: stretch;
  flex-wrap: nowrap;
  .inner-item {
    border: 1px solid #dee0e3;
    display: flex;
    flex-direction: column;
    --gap-size: 8px;
    gap: 8px;
    border-radius: 12px;
    padding: 16px;
    background: #ffffff;

    .inner-item-title {
      color: #1f2329;
      font-weight: 500;
      line-height: 22px;
      font-size: 14px;
      vertical-align: middle;
    }
    .inner-item-description {
      color: #646a73;
      font-weight: 400;
      line-height: 22px;
      font-size: 14px;
      vertical-align: middle;

      .hljs {
        padding: 0 1rem;
      }
    }
  }
}
</style>
