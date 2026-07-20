<script setup lang="ts">
/**
 * Config-assistant answer stream.
 * SSE types: id / tool-call / tool-result / message / finish / error
 * Process display: structured tool steps (same shape as ChatLog TOOL_CALL) via LogToolCall;
 * final answer is pure assistant text on sql_answer. ExecutionDetails drawer reads ChatLog.
 * Network/parse: useChatStream only (no local getReader).
 */
import { ChatInfo, type ChatMessage, ChatRecord, questionApi } from '@/api/chat.ts'
import { computed, onBeforeUnmount, ref } from 'vue'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import LogToolCall from '@/views/chat/execution-component/LogToolCall.vue'
import { useChatStream, type ChatStreamEvent } from '@/hooks/useChatStream'

type LiveToolStep = {
  name: string
  args?: Record<string, any> | any
  result?: string
  ok?: boolean
  tool_call_id?: string
  status: 'pending' | 'done'
}

const props = withDefaults(
  defineProps<{
    chatList?: Array<ChatInfo>
    currentChatId?: number
    currentChat?: ChatInfo
    message?: ChatMessage
    loading?: boolean
  }>(),
  {
    chatList: () => [],
    currentChatId: undefined,
    currentChat: () => new ChatInfo(),
    message: undefined,
    loading: false,
  }
)

const emits = defineEmits([
  'finish',
  'error',
  'stop',
  'update:loading',
  'update:chatList',
  'update:currentChat',
  'update:currentChatId',
])

const index = computed(() => {
  if (props.message?.index) {
    return props.message.index
  }
  if (props.message?.index === 0) {
    return 0
  }
  return -1
})

const _currentChatId = computed({
  get() {
    return props.currentChatId
  },
  set(v) {
    emits('update:currentChatId', v)
  },
})

const _currentChat = computed({
  get() {
    return props.currentChat
  },
  set(v) {
    emits('update:currentChat', v)
  },
})

const _loading = computed({
  get() {
    return props.loading
  },
  set(v) {
    emits('update:loading', v)
  },
})

/** Live tool steps for the in-flight turn (ChatLog is duplicated on the BE). */
const liveSteps = ref<LiveToolStep[]>([])
const stream = useChatStream()

/**
 * Strip legacy tool-markdown prefixes that older configs may still have on
 * sql_answer. New writes store pure assistant text only.
 */
function stripLegacyToolTrace(raw: string): string {
  const text = (raw || '').trim()
  if (!text) {
    return ''
  }
  if (!text.includes('**tool-call**') && !text.includes('**tool-result')) {
    return text
  }
  const parts = text
    .split(/\n\n+/)
    .map((p) => p.trim())
    .filter(Boolean)
  for (let i = parts.length - 1; i >= 0; i--) {
    if (!parts[i].startsWith('**tool-')) {
      return parts[i]
    }
  }
  return ''
}

const displayBody = computed(() => {
  const record = props.message?.record as ChatRecord | undefined
  if (!record) {
    return ''
  }
  // Live session writes pure assistant text on `message`.
  const live = (record as any).message
  if (typeof live === 'string' && live.length > 0) {
    return live
  }
  // History / persisted: pure text on sql_answer (legacy tool-prefix stripped).
  return stripLegacyToolTrace(record.sql_answer || '')
})

/** Shape each live step like ChatLogHistoryItem for the shared LogToolCall body. */
const liveLogItems = computed(() =>
  liveSteps.value.map((step) => ({
    operate_key: 'TOOL_CALL',
    operate: step.name,
    error: step.ok === false,
    message: {
      name: step.name,
      args: step.args ?? {},
      result: step.result,
      ok: step.status === 'done' ? step.ok !== false : true,
      tool_call_id: step.tool_call_id,
    },
  }))
)

function parseToolCalls(data: ChatStreamEvent): Array<{ id?: string; name?: string; args?: any }> {
  if (Array.isArray(data.tool_calls) && data.tool_calls.length) {
    return data.tool_calls as Array<{ id?: string; name?: string; args?: any }>
  }
  const raw = data.content
  if (typeof raw === 'string' && raw.trim()) {
    try {
      const parsed = JSON.parse(raw)
      return Array.isArray(parsed) ? parsed : []
    } catch {
      return []
    }
  }
  if (Array.isArray(raw)) {
    return raw
  }
  return []
}

const sendMessage = async () => {
  _loading.value = true
  liveSteps.value = []

  if (index.value < 0) {
    _loading.value = false
    return
  }

  const currentRecord: ChatRecord = _currentChat.value.records[index.value]
  if (_currentChatId.value === undefined) {
    _loading.value = false
    return
  }

  // Finished history row: parent only mounts to render; never re-call /question.
  if (currentRecord.id && currentRecord.finish) {
    _loading.value = false
    return
  }

  // Fresh turn placeholder until SSE arrives.
  ;(currentRecord as any).message = ''
  currentRecord.sql_answer = ''

  try {
    stream.createController()
    const param = {
      question: currentRecord.question,
      chat_id: _currentChatId.value,
    }
    await stream.run(
      (controller) => questionApi.add(param, controller) as Promise<Response>,
      {
        onEvent: (data: ChatStreamEvent) => {
          switch (data.type) {
            case 'id':
              currentRecord.id = data.id
              _currentChat.value.records[index.value].id = data.id
              break
            case 'tool-call': {
              const calls = parseToolCalls(data)
              for (const call of calls) {
                liveSteps.value.push({
                  name: call.name || 'tool',
                  args: call.args || {},
                  tool_call_id: call.id,
                  status: 'pending',
                  ok: true,
                })
              }
              break
            }
            case 'tool-result': {
              const name = (data.name as string) || ''
              const callId = (data as any).tool_call_id as string | undefined
              const body =
                typeof data.content === 'string'
                  ? data.content
                  : JSON.stringify(data.content ?? '')
              let ok = true
              try {
                const parsed = JSON.parse(body)
                if (parsed && typeof parsed === 'object' && (parsed as any).error) {
                  ok = false
                }
              } catch {
                /* plain text result */
              }
              // Match by tool_call_id first, then first pending with same name.
              let target = liveSteps.value.find(
                (s) => callId && s.tool_call_id === callId && s.status === 'pending'
              )
              if (!target && name) {
                target = liveSteps.value.find((s) => s.name === name && s.status === 'pending')
              }
              if (!target) {
                target = liveSteps.value.find((s) => s.status === 'pending')
              }
              if (target) {
                target.result = body
                target.ok = ok
                target.status = 'done'
                if (name && !target.name) {
                  target.name = name
                }
              } else {
                liveSteps.value.push({
                  name: name || 'tool',
                  args: {},
                  result: body,
                  ok,
                  tool_call_id: callId,
                  status: 'done',
                })
              }
              // Trigger reactivity for in-place mutations.
              liveSteps.value = [...liveSteps.value]
              break
            }
            case 'message':
              ;(currentRecord as any).message =
                ((currentRecord as any).message || '') + (data.content || '')
              // Final answer only — process lives in liveSteps / ChatLog.
              currentRecord.sql_answer = (currentRecord as any).message
              _currentChat.value.records[index.value] = currentRecord
              break
            case 'error':
              currentRecord.error = data.content
              emits('error', currentRecord.id)
              break
            case 'finish':
              currentRecord.finish = true
              if ((currentRecord as any).message) {
                currentRecord.sql_answer = (currentRecord as any).message
              }
              _currentChat.value.records[index.value] = currentRecord
              emits('finish', currentRecord.id)
              return true
          }
        },
        onTransportError: (error) => {
          if (!currentRecord.error) {
            currentRecord.error = ''
          }
          if (currentRecord.error.trim().length !== 0) {
            currentRecord.error = currentRecord.error + '\n'
          }
          currentRecord.error = currentRecord.error + 'Error:' + error
          console.error('Error:', error)
          emits('error')
        },
        onDone: () => {
          _loading.value = false
        },
      }
    )
  } finally {
    _loading.value = false
  }
}

function stop() {
  stream.stop()
  _loading.value = false
  emits('stop')
}

onBeforeUnmount(() => {
  stop()
})

defineExpose({ sendMessage, index: () => index.value, stop })
</script>

<template>
  <div v-if="message" class="config-answer-block">
    <div v-if="liveLogItems.length" class="config-live-steps">
      <LogToolCall v-for="(step, i) in liveLogItems" :key="i" :item="step" />
    </div>
    <MdComponent v-if="displayBody" :message="displayBody" style="margin-top: 12px" />
    <slot></slot>
    <div v-if="$slots.tool" class="config-tool">
      <slot name="tool"></slot>
    </div>
    <div v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<style scoped lang="less">
.config-answer-block {
  width: 100%;
}
.config-live-steps {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
}
</style>
