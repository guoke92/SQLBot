<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue'
import icon_expand_right_filled from '@/assets/svg/icon_expand-right_filled.svg'
import gou_icon from '@/assets/svg/gou_icon.svg'
import icon_error from '@/assets/svg/icon_error.svg'
import icon_database_colorful from '@/assets/svg/icon_database_colorful.svg'
import icon_alarm_clock_colorful from '@/assets/svg/icon_alarm-clock_colorful.svg'
import { chatApi, type ChatLogHistory, type ChatLogHistoryItem } from '@/api/chat.ts'
import { useI18n } from 'vue-i18n'
import { isMobile } from '@/utils/utils'
import { debounce } from 'lodash-es'
import LogTerm from './execution-component/LogTerm.vue'
import LogSQLSample from './execution-component/LogSQLSample.vue'
import LogCustomPrompt from './execution-component/LogCustomPrompt.vue'
import LogDataQuery from './execution-component/LogDataQuery.vue'
import LogChooseTable from './execution-component/LogChooseTable.vue'
import LogGeneratePicture from './execution-component/LogGeneratePicture.vue'
import LogToolCall from './execution-component/LogToolCall.vue'
import LogWithAi from '@/views/chat/execution-component/LogWithAi.vue'
import LogSpanSummary from './execution-component/LogSpanSummary.vue'

const { t } = useI18n()
const logHistory = ref<ChatLogHistory>({})
const dialogFormVisible = ref(false)
const expandIds = ref<any>([])
const drawerSize = ref('600px')

/**
 * Drawer step title: i18n operate label + optional span meta
 * (batch / attempt / unit / tool name) from ChatLog messages.
 * Single title path — no parallel name maps.
 */
function parseLogMessage(ele: ChatLogHistoryItem | Record<string, any> | undefined): any {
  if (!ele) return null
  const raw = (ele as ChatLogHistoryItem).message
  if (raw && typeof raw === 'object') return raw
  if (typeof raw === 'string') {
    try {
      return JSON.parse(raw)
    } catch {
      return null
    }
  }
  return null
}

function spanMetaFromMessage(msg: any): Record<string, any> | null {
  if (!msg) return null
  if (msg.sqlbot_span) return msg
  if (Array.isArray(msg)) {
    const head = msg.find((m: any) => m?.sqlbot_span_meta || m?.sqlbot_span)
    if (head?.sqlbot_span) return head
    if (head?.content) {
      try {
        const parsed = typeof head.content === 'string' ? JSON.parse(head.content) : head.content
        if (parsed?.sqlbot_span) return parsed
      } catch {
        /* ignore */
      }
    }
  }
  return null
}

function isSpanPayload(ele: ChatLogHistoryItem | Record<string, any> | undefined): boolean {
  return !!spanMetaFromMessage(parseLogMessage(ele))
}

function stepDisplayName(ele: ChatLogHistoryItem | Record<string, any> | undefined): string {
  if (!ele) {
    return ''
  }
  const base = (ele as ChatLogHistoryItem).operate || ''
  const msg = parseLogMessage(ele)
  const key = (ele as ChatLogHistoryItem).operate_key
  if (key === 'TOOL_CALL') {
    const tool = msg?.name || msg?.tool || msg?.payload?.name
    if (tool) return `${base} · ${tool}`
  }
  const span = spanMetaFromMessage(msg)
  if (span) {
    const bits: string[] = []
    if (span.brief) bits.push(String(span.brief))
    if (span.step_index !== undefined && span.step_index !== null) {
      bits.push(`b${span.step_index}`)
    }
    if (span.gen_attempts !== undefined && span.gen_attempts !== null && Number(span.gen_attempts) > 0) {
      bits.push(`a${span.gen_attempts}`)
    }
    if (span.unit_index !== undefined && span.unit_index !== null) {
      bits.push(`#${span.unit_index}`)
    }
    if (bits.length) return `${base} · ${bits.join(' · ')}`
  }
  return base
}

const handleExpand = (index: number) => {
  if (expandIds.value.includes(index)) {
    expandIds.value = expandIds.value.filter((ele: any) => ele !== index)
  } else {
    expandIds.value.push(index)
  }
}

function getLogList(recordId: any) {
  setDrawerSize()
  chatApi.get_chart_log_history(recordId).then((res) => {
    logHistory.value = chatApi.toChatLogHistory(res) as ChatLogHistory
    dialogFormVisible.value = true
  })
}

const setDrawerSize = debounce(() => {
  if (isMobile()) {
    drawerSize.value = window.innerWidth + 'px'
    return
  }
  drawerSize.value =
    window.innerWidth < 500 ? '460px' : `${Math.max(window.innerWidth * 0.5, 600)}px`
}, 500)

onMounted(() => {
  window.addEventListener('resize', setDrawerSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', setDrawerSize)
})

defineExpose({
  getLogList,
})
</script>

<template>
  <el-drawer
    v-model="dialogFormVisible"
    :title="t('parameter.execution_details')"
    destroy-on-close
    modal-class="execution-details"
    :size="drawerSize"
  >
    <div class="title">{{ t('parameter.overview') }}</div>
    <div class="overview">
      <div class="item">
        <el-icon size="40">
          <icon_database_colorful></icon_database_colorful>
        </el-icon>
        <div class="name">{{ t('parameter.tokens_required') }}</div>
        <div class="value">{{ logHistory.total_tokens }}</div>
      </div>
      <div class="item">
        <el-icon size="40">
          <icon_alarm_clock_colorful></icon_alarm_clock_colorful>
        </el-icon>
        <div class="name">{{ t('parameter.time_execution') }}</div>
        <div class="value">{{ logHistory.duration }}s</div>
      </div>
    </div>
    <div class="title">{{ t('parameter.execution_details') }}</div>

    <div class="list">
      <div v-for="(ele, index) in logHistory.steps" :key="ele.id ?? index" class="list-item">
        <div class="header" @click="handleExpand(index)">
          <div class="name">
            <el-icon class="shrink" :class="expandIds.includes(index) && 'expand'" size="10">
              <icon_expand_right_filled></icon_expand_right_filled>
            </el-icon>
            {{ stepDisplayName(ele) }}
          </div>
          <div class="status">
            <div
              v-if="ele.total_tokens && ele.total_tokens > 0"
              class="time"
              style="margin-right: 12px"
            >
              {{ ele.total_tokens }} tokens
            </div>
            <div class="time">{{ ele.duration }}s</div>
            <el-icon size="16">
              <icon_error v-if="ele.error"></icon_error>
              <gou_icon v-else></gou_icon>
            </el-icon>
          </div>
        </div>
        <div v-if="expandIds.includes(index)" class="content">
          <LogTerm v-if="ele.operate_key === 'FILTER_TERMS'" :item="ele" />
          <LogSQLSample v-else-if="ele.operate_key === 'FILTER_QUERY_EXAMPLE'" :item="ele" />
          <LogCustomPrompt v-else-if="ele.operate_key === 'FILTER_CUSTOM_PROMPT'" :item="ele" />
          <LogChooseTable v-else-if="ele.operate_key === 'CHOOSE_TABLE'" :item="ele" />
          <LogDataQuery v-else-if="ele.operate_key === 'EXECUTE_QUERY'" :item="ele" />
          <LogGeneratePicture v-else-if="ele.operate_key === 'GENERATE_PICTURE'" :item="ele" />
          <LogToolCall
            v-else-if="ele.operate_key === 'TOOL_CALL' || ele.operate_key === 'CONFIG_AGENT'"
            :item="ele"
          />
          <LogSpanSummary
            v-else-if="
              ele.operate_key === 'GROUND_ENTITIES' ||
              ele.operate_key === 'PREPARE_BINDINGS' ||
              ele.operate_key === 'DECIDE_NEXT' ||
              (ele.operate_key === 'ANALYSIS' && isSpanPayload(ele))
            "
            :item="ele"
          />
          <LogWithAi v-else :item="ele" />
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<style lang="less">
.execution-details {
  .title {
    font-weight: 500;
    font-size: 16px;
    line-height: 24px;
    margin-bottom: 16px;
  }

  .overview {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    .item {
      width: calc(50% - 8px);
      height: 86px;
      border-radius: 12px;
      border: 1px solid #dee0e3;
      padding: 16px;

      .ed-icon {
        float: left;
        margin: 8px 12px 0 0;
      }

      .name {
        float: left;
        color: #646a73;
        font-weight: 400;
        font-size: 14px;
        line-height: 22px;
        width: calc(100% - 55px);
      }

      .value {
        float: left;
        font-weight: 500;
        font-size: 20px;
        line-height: 28px;
        color: #1f2329;
        margin-top: 4px;
      }
    }
  }

  .list {
    .list-item {
      width: 100%;
      border-radius: 12px;
      border: 1px solid #dee0e3;
      padding: 16px;
      margin-bottom: 8px;
      cursor: pointer;

      .header {
        display: flex;
        align-items: center;
      }

      @keyframes expand {
        0% {
          height: 54px;
        }

        100% {
          min-height: 54px;
        }
      }

      &:has(.expand) {
        min-height: 54px;
        //animation: expand 0.5s;
      }

      .shrink {
        margin-right: 8px;
        cursor: pointer;
      }

      .expand {
        transform: rotate(90deg);
      }

      .status {
        display: flex;
        align-items: center;
        margin-left: auto;
      }
      .name {
        font-weight: 500;
        font-size: 14px;
        line-height: 22px;
        display: flex;
        align-items: center;
      }

      .time {
        font-weight: 400;
        font-size: 14px;
        line-height: 22px;
        color: #646a73;
      }

      .ed-icon {
        margin-left: 12px;
      }
    }
  }
}
</style>
