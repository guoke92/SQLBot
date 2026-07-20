<script setup lang="ts">
import BaseAnswer from './BaseAnswer.vue'
import { chatApi, ChatInfo, type ChatMessage, ChatRecord } from '@/api/chat.ts'
import { computed, nextTick, onBeforeUnmount, ref } from 'vue'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import { useChatStream, type ChatStreamEvent } from '@/hooks/useChatStream'
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

const _chatList = computed({
  get() {
    return props.chatList
  },
  set(v) {
    emits('update:chatList', v)
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

const stream = useChatStream()
const sendMessage = async () => {
  _loading.value = true

  if (index.value < 0) {
    _loading.value = false
    return
  }

  const currentRecord: ChatRecord = _currentChat.value.records[index.value]

  if (_currentChatId.value === undefined || currentRecord.analysis_record_id === undefined) {
    return
  }

  let analysis_answer = ''
  let analysis_answer_thinking = ''

  try {
    stream.createController()
    await stream.run(
      (controller) =>
        chatApi.analysis(currentRecord.analysis_record_id, controller) as Promise<Response>,
      {
        onEvent: async (data: ChatStreamEvent) => {
          switch (data.type) {
            case 'id':
              currentRecord.id = data.id
              _currentChat.value.records[index.value].id = data.id
              break
            case 'info':
              console.info(data.msg)
              break
            case 'error':
              currentRecord.error = data.content
              emits('error', currentRecord.id)
              break
            case 'analysis-result':
              analysis_answer += data.content
              analysis_answer_thinking += data.reasoning_content
              _currentChat.value.records[index.value].analysis = analysis_answer
              _currentChat.value.records[index.value].analysis_thinking = analysis_answer_thinking
              break
            case 'analysis_finish':
              emits('finish', currentRecord.id)
              break
          }
          await nextTick()
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
defineExpose({ sendMessage, index: () => index.value, chatList: () => _chatList.value, stop })
</script>

<template>
  <BaseAnswer
    v-if="message"
    :message="message"
    :reasoning-name="['analysis_thinking']"
    :loading="_loading"
  >
    <MdComponent :message="message.record?.analysis" style="margin-top: 12px" />
    <slot></slot>
    <template #tool>
      <slot name="tool"></slot>
    </template>
    <template #footer>
      <slot name="footer"></slot>
    </template>
  </BaseAnswer>
</template>

<style scoped lang="less"></style>
