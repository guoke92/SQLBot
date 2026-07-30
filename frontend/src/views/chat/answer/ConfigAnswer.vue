<script setup lang="ts">
import { chatApi, ChatInfo, type ChatMessage, ChatRecord } from '@/api/chat.ts'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import type { ChatStreamEvent } from '@/hooks/useChatStream'
import { useConversationTurn } from '@/features/conversation/useConversationTurn'
import { executionStepSummary } from '@/features/conversation/executionLog'
import BaseAnswer from './BaseAnswer.vue'

const props = withDefaults(
  defineProps<{
    currentChatId?: number
    currentChat?: ChatInfo
    message?: ChatMessage
  }>(),
  {
    currentChatId: undefined,
    currentChat: () => new ChatInfo(),
    message: undefined,
  }
)

const emits = defineEmits(['finish', 'error', 'stop'])

const index = computed(() => {
  if (props.message?.index) {
    return props.message.index
  }
  if (props.message?.index === 0) {
    return 0
  }
  return -1
})

const turn = useConversationTurn()
const executionSteps = ref<string[]>([])
const reasoningExpanded = ref(false)
let executionTimer: ReturnType<typeof setInterval> | undefined
let executionLoading = false

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
  return record.sql_answer || ''
})

async function refreshExecutionSteps() {
  const recordId = props.message?.record?.id
  if (!recordId || executionLoading) return

  executionLoading = true
  try {
    const history = await chatApi.get_chart_log_history(recordId, { silent: true })
    executionSteps.value = (history?.steps || []).map(executionStepSummary)
  } catch (error) {
    stopExecutionPolling()
    console.warn('Failed to load conversation execution steps', error)
  } finally {
    executionLoading = false
  }
}

function stopExecutionPolling() {
  if (executionTimer) {
    clearInterval(executionTimer)
    executionTimer = undefined
  }
}

function syncExecutionPolling() {
  stopExecutionPolling()
  if (!reasoningExpanded.value) return

  void refreshExecutionSteps()
  if (props.message?.isTyping) {
    executionTimer = setInterval(() => void refreshExecutionSteps(), 1500)
  }
}

function onReasoningToggle(expanded: boolean) {
  reasoningExpanded.value = expanded
  syncExecutionPolling()
}

const sendMessage = async () => {
  if (index.value < 0) {
    return
  }

  const currentRecord: ChatRecord = props.currentChat.records[index.value]
  if (props.currentChatId === undefined) {
    return
  }

  if (currentRecord.id && currentRecord.finish) {
    return
  }

  ;(currentRecord as any).message = ''
  currentRecord.sql_answer = ''

  await turn.run(props.currentChatId, currentRecord, {
    onEvent: (data: ChatStreamEvent) => {
      if (data.type === 'message') {
        ;(currentRecord as any).message =
          ((currentRecord as any).message || '') + (data.content || '')
        currentRecord.sql_answer = (currentRecord as any).message
      }
    },
    onError: (record) => {
      stopExecutionPolling()
      void refreshExecutionSteps()
      emits('error', record.id)
    },
    onFinish: async (record) => {
      if ((record as any).message) {
        record.sql_answer = (record as any).message
      }
      stopExecutionPolling()
      await refreshExecutionSteps()
      emits('finish', record.id)
    },
  })
}

function stop() {
  turn.stop()
  stopExecutionPolling()
  emits('stop')
}

watch(
  () => [props.message?.record?.id, props.message?.isTyping],
  () => syncExecutionPolling()
)

onBeforeUnmount(() => {
  turn.stop()
  stopExecutionPolling()
})

defineExpose({ sendMessage, index: () => index.value, stop })
</script>

<template>
  <BaseAnswer
    v-if="message"
    :message="message"
    :reasoning-items="executionSteps"
    :reasoning-available="!!message.record?.id"
    @reasoning-toggle="onReasoningToggle"
  >
    <MdComponent v-if="displayBody" :message="displayBody" style="margin-top: 12px" />
    <slot></slot>
    <template #tool>
      <slot name="tool"></slot>
    </template>
    <template #footer>
      <slot name="footer"></slot>
    </template>
  </BaseAnswer>
</template>
