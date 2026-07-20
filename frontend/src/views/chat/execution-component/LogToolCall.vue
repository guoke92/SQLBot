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

const name = computed(() => {
  return message.value.name || message.value.tool || t('chat.log.TOOL_CALL')
})

const ok = computed(() => {
  if (typeof message.value.ok === 'boolean') {
    return message.value.ok
  }
  return true
})

const argsText = computed(() => formatJson(message.value.args ?? message.value.arguments))
const resultText = computed(() => formatJson(message.value.result ?? message.value.content))
const contentText = computed(() => {
  // CONFIG_AGENT rounds may only carry a brief content preview.
  if (message.value.kind === 'agent' || message.value.role === 'agent') {
    return formatJson(message.value.content ?? message.value.preview ?? '')
  }
  return ''
})

function formatJson(value: unknown): string {
  if (value == null || value === '') {
    return ''
  }
  if (typeof value === 'string') {
    // ChatLog may store truncated tool results as "...(truncated)"; strip and retry parse.
    let trimmed = value.trim()
    const truncSuffix = '…(truncated)'
    const wasTruncated = trimmed.endsWith(truncSuffix)
    if (wasTruncated) {
      trimmed = trimmed.slice(0, -truncSuffix.length).trim()
    }
    if ((trimmed.startsWith('{') && (trimmed.endsWith('}') || wasTruncated)) ||
        (trimmed.startsWith('[') && (trimmed.endsWith(']') || wasTruncated))) {
      try {
        const pretty = JSON.stringify(JSON.parse(trimmed), null, 2)
        return wasTruncated ? `${pretty}\n…(truncated)` : pretty
      } catch {
        // partial truncated JSON often fails parse — fall through to raw
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
    <template v-if="item?.error">
      {{ error || t('chat.error') }}
    </template>
    <div v-else class="item-list flex-gap-fallback flex-col">
      <div class="inner-title">
        {{ name }}
        <span v-if="message.kind === 'agent'" class="muted"> · agent</span>
        <span v-else-if="ok" class="ok"> · ok</span>
        <span v-else class="fail"> · fail</span>
      </div>
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
