<script lang="ts" setup>
import { computed, provide, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { chatApi, ChatInfo, type ChatMessage } from '@/api/chat'
import ChatRow from '@/views/chat/ChatRow.vue'
import UserChat from '@/views/chat/chat-block/UserChat.vue'
import MultiStepAnswer from '@/views/chat/answer/MultiStepAnswer.vue'
import ConfigAnswer from '@/views/chat/answer/ConfigAnswer.vue'
import ErrorInfo from '@/views/chat/ErrorInfo.vue'
import { CHAT_DATA_SOURCE_KEY, type ChatDataSource } from '@/features/chat/chatDataSource'

const props = defineProps<{
  chatId: number
  recordId: number
}>()

const { t } = useI18n()
const loading = ref(false)
const failed = ref(false)
const currentChat = ref<ChatInfo>(new ChatInfo())

const source = ref<ChatDataSource>({
  readOnly: true,
  getTimeline: (recordId, view, runId) =>
    chatApi.get_timeline(recordId, { silent: true, view, runId }),
  getDatasetRows: (recordId, datasetId, options) =>
    chatApi.get_dataset_rows(recordId, datasetId, options),
})
provide(CHAT_DATA_SOURCE_KEY, source)

const isConfigChat = computed(() => (currentChat.value.chat_type || 'chat') === 'config')

const messages = computed<ChatMessage[]>(() => {
  const record = currentChat.value.records.find((item) => item.id === props.recordId)
  if (!record) return []
  const index = currentChat.value.records.indexOf(record)
  const rows: ChatMessage[] = []
  if (record.question !== undefined && !record.first_chat) {
    rows.push({
      role: 'user',
      create_time: record.create_time,
      record,
      content: record.question,
      index,
    })
  }
  rows.push({
    role: 'assistant',
    create_time: record.create_time,
    record,
    isTyping: false,
    first_chat: record.first_chat,
    recommended_question: record.recommended_question,
    index,
  })
  return rows
})

async function load() {
  loading.value = true
  failed.value = false
  try {
    const info = chatApi.toChatInfo(await chatApi.get(props.chatId))
    currentChat.value = info || new ChatInfo()
    if (!info?.records.some((item) => item.id === props.recordId)) failed.value = true
  } catch {
    failed.value = true
    currentChat.value = new ChatInfo()
  } finally {
    loading.value = false
  }
}

watch(() => [props.chatId, props.recordId], load, { immediate: true })
</script>

<template>
  <div v-loading="loading" class="record-preview">
    <p v-if="failed && !loading" class="record-preview-empty">
      {{ t('knowledge.wiki_preview_empty') }}
    </p>
    <template v-for="message in messages" :key="`${message.role}-${message.record?.id}`">
      <ChatRow :current-chat="currentChat" :msg="message" :hide-avatar="message.first_chat">
        <UserChat v-if="message.role === 'user'" :message="message" />
        <template v-if="message.role === 'assistant' && !message.first_chat">
          <ConfigAnswer
            v-if="isConfigChat"
            :current-chat="currentChat"
            :current-chat-id="chatId"
            :message="message"
          >
            <ErrorInfo :error="message.record?.error" class="error-container" />
          </ConfigAnswer>
          <MultiStepAnswer
            v-else
            :chat-list="[]"
            :current-chat="currentChat"
            :current-chat-id="chatId"
            :record-id="message.record?.id"
            :loading="false"
            :message="message"
          >
            <ErrorInfo :error="message.record?.error" class="error-container" />
          </MultiStepAnswer>
          <div v-if="message.record?.feedback === 'down'" class="down-feedback">
            <div class="down-feedback-label">{{ t('qa_admin.feedback_comment') }}</div>
            <div class="down-feedback-body">
              {{ message.record.feedback_comment || t('qa_admin.feedback_comment_empty') }}
            </div>
          </div>
        </template>
      </ChatRow>
    </template>
  </div>
</template>

<style lang="less" scoped>
.record-preview {
  min-height: 120px;
}

.record-preview-empty {
  color: var(--ed-text-color-secondary);
}

.down-feedback {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f5f6f7;
}

.down-feedback-label {
  color: #8f959e;
  font-size: 12px;
}

.down-feedback-body {
  margin-top: 4px;
  white-space: pre-wrap;
}
</style>
