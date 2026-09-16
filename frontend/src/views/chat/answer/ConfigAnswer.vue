<script setup lang="ts">
import { chatApi, ChatInfo, type ChatMessage, ChatRecord } from '@/api/chat.ts'
import { computed, onBeforeUnmount, ref, watch, inject, unref, type Ref } from 'vue'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import type { ChatStreamEvent } from '@/hooks/useChatStream'
import { useConversationTurn } from '@/features/conversation/useConversationTurn'
import AgentStagesView from './AgentStagesView.vue'
import BaseAnswer from './BaseAnswer.vue'
import ChatTokenTime from '@/views/chat/ChatTokenTime.vue'
import { CHAT_DATA_SOURCE_KEY, type ChatDataSource } from '@/features/chat/chatDataSource'
import {
  applyDelta,
  belongsToRun,
  extractProcessItem,
  itemsForRun,
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
const chatDataSourceRef = inject<Ref<ChatDataSource | null> | null>(CHAT_DATA_SOURCE_KEY, null)
const chatDataSource = () => unref(chatDataSourceRef) || null
const isReadOnly = () => !!chatDataSource()?.readOnly

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
const timelineItems = computed(() =>
  itemsForRun(sortedItems(timelineMap.value), props.message?.record?.run_id)
)
let liveAttemptEpoch = 0

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
  const epoch = liveAttemptEpoch
  const requestedRunId = record.run_id
  const source = chatDataSource()
  const timeline = source
    ? await source.getTimeline(record.id, 'compact', record.run_id)
    : await chatApi.get_timeline(record.id, {
        silent: true,
        runId: record.run_id,
        view: 'compact',
      })
  if (epoch !== liveAttemptEpoch) return
  if (requestedRunId && record.run_id && requestedRunId !== record.run_id) return
  if (timeline?.items) {
    timelineMap.value = replaceItems(
      itemsForRun(timeline.items as ProcessItem[], record.run_id)
    )
  }
}

function beginLiveAttempt() {
  liveAttemptEpoch += 1
  timelineMap.value = new Map()
  const record = props.message?.record as ChatRecord | undefined
  if (record) {
    ;(record as any).message = ''
    record.sql_answer = ''
  }
}

const sendMessage = async () => {
  if (isReadOnly()) return
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

  await turn.run(props.currentChatId, currentRecord, turnHandlers(currentRecord))
}

function ingestProcessItem(record: ChatRecord, item: ProcessItem | undefined, mode: 'upsert' | 'delta') {
  if (!item || !belongsToRun(item, record.run_id)) return
  timelineMap.value =
    mode === 'delta' ? applyDelta(timelineMap.value, item) : upsertItem(timelineMap.value, item)
}

function turnHandlers(currentRecord: ChatRecord) {
  return {
    onAttemptStart: () => beginLiveAttempt(),
    onEvent: (data: ChatStreamEvent) => {
      if (data.type === 'message') {
        ;(currentRecord as any).message =
          ((currentRecord as any).message || '') + (data.content || '')
        currentRecord.sql_answer = (currentRecord as any).message
      }
      if (data.type === 'process_upsert') {
        ingestProcessItem(
          currentRecord,
          extractProcessItem(data as Record<string, unknown>),
          'upsert'
        )
      }
      if (data.type === 'process_delta') {
        ingestProcessItem(
          currentRecord,
          extractProcessItem(data as Record<string, unknown>),
          'delta'
        )
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
      const epoch = liveAttemptEpoch
      if ((record as any).message) {
        record.sql_answer = (record as any).message
      }
      await hydrateTimeline(record)
      if (epoch !== liveAttemptEpoch) return
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
    if (isReadOnly()) {
      void hydrateTimeline(record)
      return
    }
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
        v-if="!isReadOnly() && !message?.isTyping && timelineItems.length === 0"
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
