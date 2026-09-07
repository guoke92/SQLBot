<script setup lang="ts">
import { chatApi, ChatInfo, type ChatMessage, ChatRecord } from '@/api/chat.ts'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import type { ChatStreamEvent } from '@/hooks/useChatStream'
import { useConversationTurn } from '@/features/conversation/useConversationTurn'
import AgentStagesView from './AgentStagesView.vue'
import BaseAnswer from './BaseAnswer.vue'
import ChatTokenTime from '@/views/chat/ChatTokenTime.vue'
import {
  applyDelta,
  extractProcessItem,
  removeItem,
  replaceItems,
  sortedItems,
  upsertItem,
  type ProcessItem,
  type TimelineMap,
} from '@/features/conversation/processTimeline'

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
const timelineMap = ref<TimelineMap>(new Map())
const timelineItems = computed(() => sortedItems(timelineMap.value))

const displayBody = computed(() => {
  const record = props.message?.record as ChatRecord | undefined
  if (!record) {
    return ''
  }
  const live = (record as any).message
  if (typeof live === 'string' && live.length > 0) {
    return live
  }
  const answerItem = [...timelineItems.value].reverse().find((item) => item.kind === 'answer')
  if (answerItem?.answer?.content) {
    return answerItem.answer.content
  }
  return record.sql_answer || ''
})

async function hydrateTimeline(record: ChatRecord) {
  if (!record.id) return
  const snapshot = await chatApi.get_timeline(record.id, {
    silent: true,
    runId: record.run_id,
    view: 'compact',
  })
  if (snapshot?.items) {
    timelineMap.value = replaceItems(snapshot.items as ProcessItem[])
  }
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
  timelineMap.value = new Map()

  await turn.run(props.currentChatId, currentRecord, turnHandlers(currentRecord))
}

function turnHandlers(currentRecord: ChatRecord) {
  return {
    onEvent: (data: ChatStreamEvent) => {
      if (data.type === 'message') {
        ;(currentRecord as any).message =
          ((currentRecord as any).message || '') + (data.content || '')
        currentRecord.sql_answer = (currentRecord as any).message
      }
      if (data.type === 'process_upsert') {
        const item = extractProcessItem(data as Record<string, unknown>)
        if (item) timelineMap.value = upsertItem(timelineMap.value, item)
      }
      if (data.type === 'process_delta') {
        const item = extractProcessItem(data as Record<string, unknown>)
        if (item) timelineMap.value = applyDelta(timelineMap.value, item)
      }
      if (data.type === 'process_remove') {
        const removeId = (data as Record<string, unknown>).id
        if (removeId != null) {
          timelineMap.value = removeItem(timelineMap.value, removeId as number | string)
        }
      }
    },
    onError: (record: ChatRecord) => {
      emits('error', record.id)
    },
    onFinish: async (record: ChatRecord) => {
      if ((record as any).message) {
        record.sql_answer = (record as any).message
      }
      await hydrateTimeline(record)
      emits('finish', record.id)
    },
  }
}

function stop() {
  turn.detach()
  emits('stop')
}

watch(
  () => [props.message?.record?.run_id, props.message?.record?.run_status] as const,
  ([runId, status]) => {
    const record = props.message?.record
    if (!record || !runId) return
    if (status === 'awaiting_input') {
      void hydrateTimeline(record).then(() => turn.attach(record, turnHandlers(record)))
      return
    }
    if (!['queued', 'running'].includes(status || '')) return
    if (turn.owned.value || turn.running.value) return
    ;(record as any).message = ''
    record.sql_answer = ''
    void hydrateTimeline(record).then(() => turn.attach(record, turnHandlers(record)))
  },
  { immediate: true }
)

watch(
  () => [props.message?.record?.id, props.message?.record?.finish] as const,
  ([recordId, finish]) => {
    const record = props.message?.record
    if (recordId && finish && record && !props.message?.isTyping) {
      void hydrateTimeline(record)
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  turn.detach()
})

defineExpose({ sendMessage, index: () => index.value, stop })
</script>

<template>
  <BaseAnswer v-if="message" :message="message" :hide-thinking-toggle="true">
    <AgentStagesView
      v-if="timelineItems.length > 0"
      :items="timelineItems"
      :is-typing="message?.isTyping"
      :record-id="message?.record?.id"
      :duration="message?.record?.duration"
      :total-tokens="message?.record?.total_tokens"
    />
    <MdComponent v-if="displayBody" :message="displayBody" style="margin-top: 12px" />
    <slot></slot>
    <template #tool>
      <ChatTokenTime
        v-if="!message?.isTyping && timelineItems.length === 0"
        :record-id="message?.record?.id"
        :duration="message?.record?.duration"
        :total-tokens="message?.record?.total_tokens"
      />
      <slot name="tool"></slot>
    </template>
    <template #footer>
      <slot name="footer"></slot>
    </template>
  </BaseAnswer>
</template>
