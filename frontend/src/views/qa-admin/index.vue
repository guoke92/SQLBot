<script lang="ts" setup>
import { computed, provide, ref, watch } from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/en'
import 'dayjs/locale/ko'
import 'dayjs/locale/zh-cn'
import 'dayjs/locale/zh-tw'
import { useI18n } from 'vue-i18n'
import { ChatInfo, type ChatMessage } from '@/api/chat'
import {
  qaAdminApi,
  type DevChatFilters,
  type DevChatRow,
  type DevDatasource,
  type DevOperator,
  type DevWorkspace,
} from '@/api/dev'
import ChatRow from '@/views/chat/ChatRow.vue'
import MultiStepAnswer from '@/views/chat/answer/MultiStepAnswer.vue'
import ConfigAnswer from '@/views/chat/answer/ConfigAnswer.vue'
import ErrorInfo from '@/views/chat/ErrorInfo.vue'
import UserChat from '@/views/chat/chat-block/UserChat.vue'
import ChatToolBar from '@/views/chat/ChatToolBar.vue'
import icon_export_outlined from '@/assets/svg/icon_export_outlined.svg'
import icon_searchOutline_outlined from '@/assets/svg/icon_search-outline_outlined.svg'
import {
  CHAT_DATA_SOURCE_KEY,
  type ChatDataSource,
} from '@/features/chat/chatDataSource'

dayjs.extend(relativeTime)

const AVATAR_COLORS = [
  '#3370FF',
  '#14C0FF',
  '#2FC25B',
  '#F5A300',
  '#F54A45',
  '#8B5CF6',
  '#0E9F77',
  '#E6A23C',
  '#1F6FEB',
  '#C9372C',
]

const { t, locale } = useI18n()

const loadingList = ref(false)
const loadingChat = ref(false)
const exporting = ref(false)
const workspaces = ref<DevWorkspace[]>([])
const operators = ref<DevOperator[]>([])
const datasources = ref<DevDatasource[]>([])
const chats = ref<DevChatRow[]>([])
const selectedOid = ref('')
const selectedOperator = ref('')
const selectedDatasource = ref('')
const feedbackFilter = ref('all')
const chatTypeFilter = ref('chat')
const keyword = ref('')
const timeRange = ref<[string, string] | null>(null)
const selectedChatIds = ref<string[]>([])
const currentChat = ref<ChatInfo>(new ChatInfo())
const currentChatId = ref<number | undefined>()

const chatDataSource = ref<ChatDataSource>({
  readOnly: true,
  getTimeline: (recordId, view, runId) =>
    qaAdminApi.getTimeline(recordId, { view, runId }),
  getDatasetRows: (recordId, datasetId, options) =>
    qaAdminApi.getDatasetRows(recordId, datasetId, options),
})
provide(CHAT_DATA_SOURCE_KEY, chatDataSource)

const isConfigChat = computed(() => (currentChat.value?.chat_type || 'chat') === 'config')

function dayjsLocale(code: string) {
  if (code.startsWith('zh-TW')) return 'zh-tw'
  if (code.startsWith('zh')) return 'zh-cn'
  if (code.startsWith('ko')) return 'ko'
  return 'en'
}

function firstChar(text?: string | null) {
  const value = (text || '').trim()
  if (!value) return '?'
  return [...value][0] || '?'
}

function avatarColor(key?: string | number | null) {
  const seed = String(key || '')
  let hash = 0
  for (let i = 0; i < seed.length; i++) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0
  }
  return AVATAR_COLORS[hash % AVATAR_COLORS.length]
}

function lastDays(days: number): [string, string] {
  return [
    dayjs().subtract(days, 'day').format('YYYY-MM-DD HH:mm:ss'),
    dayjs().format('YYYY-MM-DD HH:mm:ss'),
  ]
}

const timeShortcuts = computed(() => [
  { text: t('qa_admin.time_1d'), value: () => lastDays(1) },
  { text: t('qa_admin.time_3d'), value: () => lastDays(3) },
  { text: t('qa_admin.time_5d'), value: () => lastDays(5) },
  { text: t('qa_admin.time_7d'), value: () => lastDays(7) },
  { text: t('qa_admin.time_15d'), value: () => lastDays(15) },
  { text: t('qa_admin.time_30d'), value: () => lastDays(30) },
])

function operatorDisplay(row: DevChatRow) {
  return (row.user_name || row.user_account || '').trim()
}

function timeAgo(value?: string | null) {
  if (!value) return ''
  return dayjs(value).locale(dayjsLocale(locale.value)).fromNow()
}

function chatTitle(row: DevChatRow) {
  const brief = (row.brief || '').trim()
  return brief || `#${row.id}`
}

function downFeedbackText(message: ChatMessage) {
  const comment = (message.record?.feedback_comment || '').trim()
  return comment || t('qa_admin.feedback_comment_empty')
}

function toggleChat(id: string | number, checked: boolean) {
  const key = String(id)
  if (checked) {
    if (!selectedChatIds.value.includes(key)) selectedChatIds.value.push(key)
    return
  }
  selectedChatIds.value = selectedChatIds.value.filter((item) => item !== key)
}

const currentFilters = computed<DevChatFilters | null>(() => {
  if (!selectedOid.value) return null
  return {
    oid: selectedOid.value,
    create_by: selectedOperator.value || undefined,
    q: keyword.value.trim() || undefined,
    feedback: feedbackFilter.value,
    datasource: selectedDatasource.value || undefined,
    created_from: timeRange.value?.[0],
    created_to: timeRange.value?.[1],
    chat_ids: selectedChatIds.value.length ? selectedChatIds.value : undefined,
    chat_type: chatTypeFilter.value,
  }
})

const computedMessages = computed<Array<ChatMessage>>(() => {
  const messages: Array<ChatMessage> = []
  if (currentChatId.value === undefined) return messages
  for (let i = 0; i < currentChat.value.records.length; i++) {
    const record = currentChat.value.records[i]
    if (record.question !== undefined && !record.first_chat) {
      messages.push({
        role: 'user',
        create_time: record.create_time,
        record,
        content: record.question,
        index: i,
      })
    }
    messages.push({
      role: 'assistant',
      create_time: record.create_time,
      record,
      isTyping: false,
      first_chat: record.first_chat,
      recommended_question: record.recommended_question,
      index: i,
    })
  }
  return messages
})

const reloadOperators = async () => {
  if (!selectedOid.value) {
    operators.value = []
    return
  }
  operators.value = (await qaAdminApi.operators(selectedOid.value)) || []
}

const reloadDatasources = async () => {
  if (!selectedOid.value) {
    datasources.value = []
    return
  }
  datasources.value = (await qaAdminApi.datasources(selectedOid.value)) || []
}

const reloadChats = async () => {
  if (!selectedOid.value) return
  loadingList.value = true
  try {
    chats.value =
      (await qaAdminApi.chats({
        oid: selectedOid.value,
        create_by: selectedOperator.value || undefined,
        q: keyword.value.trim() || undefined,
        feedback: feedbackFilter.value,
        datasource: selectedDatasource.value || undefined,
        created_from: timeRange.value?.[0],
        created_to: timeRange.value?.[1],
        chat_type: chatTypeFilter.value,
      })) || []
    selectedChatIds.value = []
  } finally {
    loadingList.value = false
  }
}

const onWorkspaceChange = async () => {
  selectedOperator.value = ''
  selectedDatasource.value = ''
  currentChat.value = new ChatInfo()
  currentChatId.value = undefined
  await Promise.all([reloadOperators(), reloadDatasources()])
  await reloadChats()
}

const openChat = async (row: DevChatRow) => {
  loadingChat.value = true
  try {
    const chat = await qaAdminApi.getChat(row.id)
    if (!chat) return
    currentChat.value = chat
    currentChatId.value = chat.id
  } finally {
    loadingChat.value = false
  }
}

const exportFeedback = async () => {
  if (!currentFilters.value) return
  exporting.value = true
  try {
    await qaAdminApi.downloadFeedbackXlsx(currentFilters.value)
  } finally {
    exporting.value = false
  }
}

watch(selectedOid, (oid, prev) => {
  if (!oid || oid === prev) return
  void onWorkspaceChange()
})

const bootstrap = async () => {
  workspaces.value = (await qaAdminApi.workspaces()) || []
  if (!selectedOid.value && workspaces.value.length) {
    selectedOid.value = String(workspaces.value[0].id)
  }
}

void bootstrap()
</script>

<template>
  <div class="qa-admin">
    <div class="qa-admin-header">
      <div class="title-row">
        <div class="title">{{ t('menu.qa_admin') }}</div>
        <el-button :loading="exporting" :disabled="!selectedOid" @click="exportFeedback">
          <el-icon><icon_export_outlined /></el-icon>
          {{ t('qa_admin.export_feedback') }}
        </el-button>
      </div>
      <div class="filters">
        <div class="filter-field">
          <span class="label">{{ t('qa_admin.workspace') }}</span>
          <el-select
            v-model="selectedOid"
            filterable
            style="width: 200px"
            :placeholder="t('qa_admin.workspace_placeholder')"
          >
            <el-option
              v-for="ws in workspaces"
              :key="String(ws.id)"
              :label="ws.name"
              :value="String(ws.id)"
            />
          </el-select>
        </div>
        <div class="filter-field">
          <span class="label">{{ t('qa_admin.operator') }}</span>
          <el-select
            v-model="selectedOperator"
            clearable
            filterable
            style="width: 180px"
            :placeholder="t('qa_admin.operator_placeholder')"
            :disabled="!selectedOid"
            @change="reloadChats"
          >
            <el-option
              v-for="user in operators"
              :key="String(user.id)"
              :label="user.name || user.account || String(user.id)"
              :value="String(user.id)"
            />
          </el-select>
        </div>
        <div class="filter-field">
          <span class="label">{{ t('qa_admin.datasource') }}</span>
          <el-select
            v-model="selectedDatasource"
            clearable
            filterable
            style="width: 180px"
            :placeholder="t('qa_admin.datasource_placeholder')"
            :disabled="!selectedOid"
            @change="reloadChats"
          >
            <el-option
              v-for="ds in datasources"
              :key="String(ds.id)"
              :label="ds.name"
              :value="String(ds.id)"
            />
          </el-select>
        </div>
        <div class="filter-field">
          <span class="label">{{ t('qa_admin.chat_type') }}</span>
          <el-select
            v-model="chatTypeFilter"
            style="width: 140px"
            @change="reloadChats"
          >
            <el-option :label="t('qa_admin.chat_type_chat')" value="chat" />
            <el-option :label="t('qa_admin.chat_type_config')" value="config" />
            <el-option :label="t('qa_admin.chat_type_all')" value="all" />
          </el-select>
        </div>
        <div class="filter-field">
          <span class="label">{{ t('qa_admin.feedback_status') }}</span>
          <el-select
            v-model="feedbackFilter"
            style="width: 140px"
            @change="reloadChats"
          >
            <el-option :label="t('qa_admin.feedback_all')" value="all" />
            <el-option :label="t('qa_admin.feedback_up')" value="up" />
            <el-option :label="t('qa_admin.feedback_none')" value="none" />
            <el-option :label="t('qa_admin.feedback_down')" value="down" />
          </el-select>
        </div>
        <div class="filter-field">
          <span class="label">{{ t('qa_admin.time_range') }}</span>
          <el-date-picker
            v-model="timeRange"
            type="datetimerange"
            value-format="YYYY-MM-DD HH:mm:ss"
            :start-placeholder="t('common.start_time')"
            :end-placeholder="t('common.end_time')"
            :shortcuts="timeShortcuts"
            clearable
            style="width: 360px"
            @change="reloadChats"
          />
        </div>
        <div class="filter-field filter-search">
          <span class="label">{{ t('qa_admin.chat_name') }}</span>
          <el-input
            v-model="keyword"
            clearable
            style="width: 220px"
            :placeholder="t('qa_admin.search_brief')"
            @keyup.enter="reloadChats"
          >
            <template #prefix>
              <el-icon>
                <icon_searchOutline_outlined class="svg-icon" />
              </el-icon>
            </template>
          </el-input>
        </div>
        <el-button type="primary" @click="reloadChats">{{ t('common.search') }}</el-button>
      </div>
    </div>

    <div class="qa-admin-body">
      <div class="chat-list" v-loading="loadingList">
        <div
          v-for="row in chats"
          :key="String(row.id)"
          class="chat-item"
          :class="{ active: currentChatId != null && String(currentChatId) === String(row.id) }"
          @click="openChat(row)"
        >
          <el-checkbox
            :model-value="selectedChatIds.includes(String(row.id))"
            @click.stop
            @update:model-value="(checked: boolean) => toggleChat(row.id, !!checked)"
          />
          <div
            class="avatar"
            :style="{ background: avatarColor(row.create_by || row.user_account) }"
          >
            {{ firstChar(row.user_name || row.user_account) }}
          </div>
          <div class="chat-item-main">
            <div class="brief" :title="chatTitle(row)">{{ chatTitle(row) }}</div>
            <div class="meta">
              <span v-if="operatorDisplay(row)" class="operator" :title="operatorDisplay(row)">
                {{ operatorDisplay(row) }}
              </span>
              <span class="ago">{{ timeAgo(row.last_time || row.create_time) }}</span>
              <span v-if="row.datasource_name" class="ds-name" :title="row.datasource_name">
                {{ row.datasource_name }}
              </span>
              <span v-if="row.feedback_up" class="fb-icon is-up" :title="t('qa.feedback_up')">
                <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M602.2 438.4h245.5c30.4 0 55 24.6 55 55 0 8.4-1.9 16.7-5.6 24.3L767.6 802c-8.7 17.9-27 29.3-47.1 29.3H256V438.4l196.4-292.2c17.1-25.5 49.3-34.5 75.8-21.2l5.4 3.1c26.5 17.1 34.1 52.5 17 79l-5.3 7.5-87 164.8h143.9zM320 502.4v265h400.5l113.1-230.6H538.2l110.6-209.2-13-7.4L320 502.4zM256 438.4H128v393h128v-393z"
                    fill="currentColor"
                  />
                </svg>
                <span v-if="row.feedback_up > 1">{{ row.feedback_up }}</span>
              </span>
              <span v-if="row.feedback_down" class="fb-icon is-down" :title="t('qa.feedback_down')">
                <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M421.8 585.6H176.3c-30.4 0-55-24.6-55-55 0-8.4 1.9-16.7 5.6-24.3L256.4 222c8.7-17.9 27-29.3 47.1-29.3H768v393H571.6l-196.4 292.2c-17.1 25.5-49.3 34.5-75.8 21.2l-5.4-3.1c-26.5-17.1-34.1-52.5-17-79l5.3-7.5 87-164.8H421.8zM704 521.6v-265H303.5L190.4 487.2h232.4L312.2 696.4l13 7.4L704 521.6zM768 585.6h128v-393H768v393z"
                    fill="currentColor"
                  />
                </svg>
                <span v-if="row.feedback_down > 1">{{ row.feedback_down }}</span>
              </span>
            </div>
          </div>
        </div>
        <div v-if="!chats.length" class="empty">{{ t('qa_admin.no_chats') }}</div>
      </div>

      <div class="chat-restore" v-loading="loadingChat">
        <div v-if="computedMessages.length" class="restore-scroll">
          <template
            v-for="message in computedMessages"
            :key="`${message.role}-${message.record?.id ?? message.index}`"
          >
            <ChatRow :current-chat="currentChat" :msg="message" :hide-avatar="message.first_chat">
              <UserChat v-if="message.role === 'user'" :message="message" :all-messages="computedMessages" />
              <template v-if="message.role === 'assistant' && !message.first_chat">
                <ConfigAnswer
                  v-if="isConfigChat"
                  :current-chat="currentChat"
                  :current-chat-id="currentChatId"
                  :message="message"
                >
                  <ErrorInfo :error="message.record?.error" class="error-container" />
                  <template #tool>
                    <ChatToolBar :message="message">
                      <div class="tool-btns">
                        <el-tooltip :content="t('qa.feedback_up')" placement="top" :offset="8">
                          <el-button
                            class="tool-btn feedback-up"
                            :class="{ 'is-active': message.record?.feedback === 'up' }"
                            text
                          >
                            <el-icon size="18">
                              <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                                <path
                                  d="M602.2 438.4h245.5c30.4 0 55 24.6 55 55 0 8.4-1.9 16.7-5.6 24.3L767.6 802c-8.7 17.9-27 29.3-47.1 29.3H256V438.4l196.4-292.2c17.1-25.5 49.3-34.5 75.8-21.2l5.4 3.1c26.5 17.1 34.1 52.5 17 79l-5.3 7.5-87 164.8h143.9zM320 502.4v265h400.5l113.1-230.6H538.2l110.6-209.2-13-7.4L320 502.4zM256 438.4H128v393h128v-393z"
                                  fill="currentColor"
                                />
                              </svg>
                            </el-icon>
                          </el-button>
                        </el-tooltip>
                        <el-tooltip
                          :content="message.record?.feedback_comment || t('qa.feedback_down')"
                          placement="top"
                          :offset="8"
                        >
                          <el-button
                            class="tool-btn feedback-down"
                            :class="{ 'is-active': message.record?.feedback === 'down' }"
                            text
                          >
                            <el-icon size="18">
                              <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                                <path
                                  d="M421.8 585.6H176.3c-30.4 0-55-24.6-55-55 0-8.4 1.9-16.7 5.6-24.3L256.4 222c8.7-17.9 27-29.3 47.1-29.3H768v393H571.6l-196.4 292.2c-17.1 25.5-49.3 34.5-75.8 21.2l-5.4-3.1c-26.5-17.1-34.1-52.5-17-79l5.3-7.5 87-164.8H421.8zM704 521.6v-265H303.5L190.4 487.2h232.4L312.2 696.4l13 7.4L704 521.6zM768 585.6h128v-393H768v393z"
                                  fill="currentColor"
                                />
                              </svg>
                            </el-icon>
                          </el-button>
                        </el-tooltip>
                      </div>
                    </ChatToolBar>
                  </template>
                </ConfigAnswer>
                <MultiStepAnswer
                  v-else
                  :chat-list="[]"
                  :current-chat="currentChat"
                  :current-chat-id="currentChatId"
                  :record-id="message.record?.id"
                  :loading="false"
                  :message="message"
                >
                  <ErrorInfo :error="message.record?.error" class="error-container" />
                  <template #tool>
                    <ChatToolBar :message="message">
                      <div class="tool-btns">
                        <el-tooltip :content="t('qa.feedback_up')" placement="top" :offset="8">
                          <el-button
                            class="tool-btn feedback-up"
                            :class="{ 'is-active': message.record?.feedback === 'up' }"
                            text
                          >
                            <el-icon size="18">
                              <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                                <path
                                  d="M602.2 438.4h245.5c30.4 0 55 24.6 55 55 0 8.4-1.9 16.7-5.6 24.3L767.6 802c-8.7 17.9-27 29.3-47.1 29.3H256V438.4l196.4-292.2c17.1-25.5 49.3-34.5 75.8-21.2l5.4 3.1c26.5 17.1 34.1 52.5 17 79l-5.3 7.5-87 164.8h143.9zM320 502.4v265h400.5l113.1-230.6H538.2l110.6-209.2-13-7.4L320 502.4zM256 438.4H128v393h128v-393z"
                                  fill="currentColor"
                                />
                              </svg>
                            </el-icon>
                          </el-button>
                        </el-tooltip>
                        <el-tooltip
                          :content="message.record?.feedback_comment || t('qa.feedback_down')"
                          placement="top"
                          :offset="8"
                        >
                          <el-button
                            class="tool-btn feedback-down"
                            :class="{ 'is-active': message.record?.feedback === 'down' }"
                            text
                          >
                            <el-icon size="18">
                              <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                                <path
                                  d="M421.8 585.6H176.3c-30.4 0-55-24.6-55-55 0-8.4 1.9-16.7 5.6-24.3L256.4 222c8.7-17.9 27-29.3 47.1-29.3H768v393H571.6l-196.4 292.2c-17.1 25.5-49.3 34.5-75.8 21.2l-5.4-3.1c-26.5-17.1-34.1-52.5-17-79l5.3-7.5 87-164.8H421.8zM704 521.6v-265H303.5L190.4 487.2h232.4L312.2 696.4l13 7.4L704 521.6zM768 585.6h128v-393H768v393z"
                                  fill="currentColor"
                                />
                              </svg>
                            </el-icon>
                          </el-button>
                        </el-tooltip>
                      </div>
                    </ChatToolBar>
                  </template>
                </MultiStepAnswer>
                <div
                  v-if="message.record?.feedback === 'down'"
                  class="down-feedback"
                >
                  <div class="down-feedback-label">{{ t('qa_admin.feedback_comment') }}</div>
                  <div class="down-feedback-body">
                    {{ downFeedbackText(message) }}
                  </div>
                </div>
              </template>
            </ChatRow>
          </template>
        </div>
        <div v-else class="empty">{{ t('qa_admin.pick_chat') }}</div>
      </div>
    </div>
  </div>
</template>

<style lang="less" scoped>
.qa-admin {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  gap: 12px;
  min-height: 0;
}
.qa-admin-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
.filters {
  display: flex;
  align-items: center;
  gap: 12px 16px;
  flex-wrap: wrap;
}
.filter-field {
  display: flex;
  align-items: center;
  gap: 8px;
}
.label {
  color: #646a73;
  font-size: 14px;
  white-space: nowrap;
}
.qa-admin-body {
  flex: 1;
  min-height: 0;
  display: flex;
  gap: 12px;
}
.chat-list {
  width: 360px;
  overflow: auto;
  border: 1px solid #dee0e3;
  border-radius: 8px;
  padding: 8px;
  background: #fff;
}
.chat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  line-height: 22px;
  color: #1f2329;
  &.active,
  &:hover {
    background: #f5f6f7;
  }
}
.avatar {
  flex: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.chat-item-main {
  min-width: 0;
  flex: 1;
}
.brief {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
  min-width: 0;
}
.ago {
  color: #8f959e;
  font-size: 12px;
  white-space: nowrap;
}
.operator {
  flex: none;
  max-width: 96px;
  color: #646a73;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ds-name {
  min-width: 0;
  color: #8f959e;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.fb-icon {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  line-height: 1;
  svg {
    width: 14px;
    height: 14px;
  }
  &.is-up {
    color: #22a06b;
  }
  &.is-down {
    color: #c9372c;
  }
}
.chat-restore {
  flex: 1;
  min-width: 0;
  border: 1px solid #dee0e3;
  border-radius: 8px;
  background: #fff;
  display: flex;
  flex-direction: column;
}
.restore-scroll {
  flex: 1;
  overflow: auto;
  padding: 16px;
}
.empty {
  color: #8f959e;
  padding: 24px;
  text-align: center;
}
.tool-btns {
  display: flex;
  flex-direction: row;
  align-items: center;
  column-gap: 16px;
  .tool-btn {
    font-size: 14px;
    color: rgba(100, 106, 115, 1);
    &:hover,
    &:active {
      background: rgba(31, 35, 41, 0.1);
    }
  }
  .tool-btn.feedback-up.is-active {
    color: #22a06b !important;
    background: rgba(34, 160, 107, 0.16);
  }
  .tool-btn.feedback-down.is-active {
    color: #c9372c !important;
    background: rgba(201, 55, 44, 0.16);
  }
}
.down-feedback {
  margin-top: 4px;
  padding: 10px 12px;
  border-radius: 6px;
  background: rgba(201, 55, 44, 0.06);
  border: 1px solid rgba(201, 55, 44, 0.18);
}
.down-feedback-label {
  font-size: 12px;
  line-height: 18px;
  font-weight: 500;
  color: #c9372c;
  margin-bottom: 4px;
}
.down-feedback-body {
  font-size: 13px;
  line-height: 20px;
  color: #1f2329;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
