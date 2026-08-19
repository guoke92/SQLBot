<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { debounce } from 'lodash-es'
import { useI18n } from 'vue-i18n'
import icon_expand_right_filled from '@/assets/svg/icon_expand-right_filled.svg'
import gou_icon from '@/assets/svg/gou_icon.svg'
import icon_error from '@/assets/svg/icon_error.svg'
import icon_database_colorful from '@/assets/svg/icon_database_colorful.svg'
import icon_alarm_clock_colorful from '@/assets/svg/icon_alarm-clock_colorful.svg'
import { chatApi, type ChatLogHistory } from '@/api/chat'
import { isMobile } from '@/utils/utils'
import {
  executionNodePhase,
  executionStepStatus,
  stepDisplayName,
} from '@/features/conversation/executionLog'
import ExecutionStepContent from './execution-component/ExecutionStepContent.vue'

const { t, te } = useI18n()
const logHistory = ref<ChatLogHistory>({})
const dialogFormVisible = ref(false)
const expandedIds = ref<Array<number | string>>([])
const drawerSize = ref('600px')
const activeRecordId = ref<number>()
const selectedRunId = ref<string>()
const loading = ref(false)
let pollTimer: ReturnType<typeof setTimeout> | undefined

const terminal = computed(() =>
  ['succeeded', 'degraded', 'failed', 'cancelled'].includes(logHistory.value.run?.status || '')
)
const tokenText = computed(() => logHistory.value.total_tokens ?? '—')
const durationText = computed(() =>
  logHistory.value.duration == null ? '—' : `${logHistory.value.duration}s`
)
const waitingText = computed(() =>
  logHistory.value.waiting_duration == null ? '—' : `${logHistory.value.waiting_duration}s`
)
const elapsedText = computed(() =>
  logHistory.value.elapsed_duration == null ? '—' : `${logHistory.value.elapsed_duration}s`
)
const phaseOrder = ['prepare', 'understand', 'plan', 'execute', 'review', 'present', 'respond']
const groupedSteps = computed(() => {
  const groups = new Map<string, any[]>()
  for (const step of logHistory.value.steps || []) {
    const phase = step.phase || 'plan'
    groups.set(phase, [...(groups.get(phase) || []), step])
  }
  return [...groups.entries()]
    .sort(([left], [right]) => phaseOrder.indexOf(left) - phaseOrder.indexOf(right))
    .map(([phase, steps]) => ({ phase, steps }))
})

const titleFor = (item: any) => {
  const key = item.title_key
  return key && te(key) ? t(key, item.title_params || {}) : stepDisplayName(item)
}
const runStatusText = computed(() => {
  const key = `chat.audit.run_${logHistory.value.run?.status || 'running'}`
  return te(key) ? t(key) : t('chat.audit.processing')
})
const runStageText = computed(() =>
  t(`chat.audit.phase_${executionNodePhase(logHistory.value.run?.current_node)}`)
)
const summaryFor = (item: any) => {
  const key = item.summary_key
  return key && te(key) ? t(key, item.summary_params || {}) : ''
}
const stepKey = (item: any, index: number) => item.id ?? `step-${index}`
const toggle = (key: number | string) => {
  expandedIds.value = expandedIds.value.includes(key)
    ? expandedIds.value.filter((id) => id !== key)
    : [...expandedIds.value, key]
}

async function load(silent = false) {
  if (!activeRecordId.value || loading.value) return
  loading.value = true
  try {
    logHistory.value =
      (await chatApi.get_chart_log_history(activeRecordId.value, {
        silent,
        runId: selectedRunId.value,
      })) || {}
    selectedRunId.value = logHistory.value.run?.run_id
    const important = (logHistory.value.steps || []).filter((item) =>
      ['running', 'failed', 'degraded'].includes(executionStepStatus(item))
    )
    for (const item of important) {
      if (item.id != null && !expandedIds.value.includes(item.id)) {
        expandedIds.value.push(item.id)
      }
    }
  } finally {
    loading.value = false
  }
}

function schedulePoll() {
  if (pollTimer) clearTimeout(pollTimer)
  if (!dialogFormVisible.value || terminal.value) return
  pollTimer = setTimeout(async () => {
    await load(true)
    schedulePoll()
  }, 2000)
}

async function getLogList(recordId: number) {
  setDrawerSize()
  activeRecordId.value = recordId
  selectedRunId.value = undefined
  dialogFormVisible.value = true
  expandedIds.value = []
  await load()
  schedulePoll()
}

async function selectRun(runId: string) {
  if (runId === selectedRunId.value) return
  selectedRunId.value = runId
  expandedIds.value = []
  await load(true)
  schedulePoll()
}

watch(dialogFormVisible, (visible) => {
  if (visible) schedulePoll()
  else if (pollTimer) clearTimeout(pollTimer)
})
watch(terminal, schedulePoll)

const setDrawerSize = debounce(() => {
  drawerSize.value = isMobile()
    ? `${window.innerWidth}px`
    : window.innerWidth < 500
      ? '460px'
      : `${Math.max(window.innerWidth * 0.5, 600)}px`
}, 200)

onMounted(() => window.addEventListener('resize', setDrawerSize))
onUnmounted(() => {
  window.removeEventListener('resize', setDrawerSize)
  if (pollTimer) clearTimeout(pollTimer)
})
defineExpose({ getLogList })
</script>

<template>
  <el-drawer
    v-model="dialogFormVisible"
    :title="t('parameter.execution_details')"
    destroy-on-close
    modal-class="execution-details"
    :size="drawerSize"
  >
    <div class="run-state">
      <el-icon v-if="!terminal" class="is-loading"><Loading /></el-icon>
      <span>{{ runStatusText }}</span>
      <span v-if="!terminal && logHistory.run?.current_node" class="current-node">
        {{ t('chat.audit.current_stage') }}：{{ runStageText }}
      </span>
      <span
        v-else-if="logHistory.run?.status === 'failed' && logHistory.run?.current_node"
        class="current-node"
      >
        {{ t('chat.audit.failed_stage') }}：{{ runStageText }}
      </span>
      <el-select
        v-if="(logHistory.attempts?.length || 0) > 1"
        :model-value="selectedRunId"
        class="attempt-select"
        size="small"
        @change="selectRun"
      >
        <el-option
          v-for="(attempt, index) in logHistory.attempts"
          :key="attempt.run_id"
          :label="t('chat.audit.run_attempt', { value: index + 1 })"
          :value="attempt.run_id"
        />
      </el-select>
    </div>
    <div class="title">{{ t('parameter.overview') }}</div>
    <div class="overview">
      <div class="item">
        <el-icon size="40"><icon_database_colorful /></el-icon>
        <div class="name">{{ t('parameter.tokens_required') }}</div>
        <div class="value">{{ tokenText }}</div>
      </div>
      <div class="item">
        <el-icon size="40"><icon_alarm_clock_colorful /></el-icon>
        <div class="name">{{ t('parameter.time_execution') }}</div>
        <div class="value">{{ durationText }}</div>
      </div>
      <div v-if="logHistory.waiting_duration" class="item compact-metric">
        <div class="name">{{ t('chat.audit.waiting_time') }}</div>
        <div class="value">{{ waitingText }}</div>
      </div>
      <div v-if="logHistory.waiting_duration" class="item compact-metric">
        <div class="name">{{ t('chat.audit.total_time') }}</div>
        <div class="value">{{ elapsedText }}</div>
      </div>
    </div>
    <div class="title">{{ t('parameter.execution_details') }}</div>
    <div class="list">
      <section v-for="group in groupedSteps" :key="group.phase" class="phase-group">
        <div class="phase-title">{{ t(`chat.audit.phase_${group.phase}`) }}</div>
        <div v-for="(item, index) in group.steps" :key="stepKey(item, index)" class="list-item">
          <div class="header" @click="toggle(stepKey(item, index))">
            <div class="name">
              <el-icon
                class="shrink"
                :class="expandedIds.includes(stepKey(item, index)) && 'expand'"
                size="10"
                ><icon_expand_right_filled
              /></el-icon>
              <span>{{ titleFor(item) }}</span>
              <el-tag v-if="(item.attempt_index || 0) > 0" size="small" type="info">
                {{ t('chat.audit.attempt', { value: item.attempt_index + 1 }) }}
              </el-tag>
              <el-tag v-if="(item.batch_index || 0) > 0" size="small" type="info">
                {{ t('chat.audit.batch', { value: item.batch_index + 1 }) }}
              </el-tag>
              <el-tag v-if="(item.unit_index || 0) > 0" size="small" type="info">
                {{ t('chat.audit.unit', { value: item.unit_index + 1 }) }}
              </el-tag>
            </div>
            <div class="status">
              <span v-if="summaryFor(item)" class="summary">{{ summaryFor(item) }}</span>
              <span v-if="item.total_tokens" class="time">{{ item.total_tokens }} tokens</span>
              <span class="time">{{ item.duration == null ? '—' : `${item.duration}s` }}</span>
              <el-icon v-if="executionStepStatus(item) === 'running'" class="is-loading"
                ><Loading
              /></el-icon>
              <el-icon v-else size="16">
                <icon_error v-if="['failed', 'interrupted'].includes(executionStepStatus(item))" />
                <WarningFilled
                  v-else-if="executionStepStatus(item) === 'degraded'"
                  class="degraded"
                />
                <gou_icon v-else />
              </el-icon>
            </div>
          </div>
          <ExecutionStepContent v-if="expandedIds.includes(stepKey(item, index))" :item="item" />
        </div>
      </section>
    </div>
  </el-drawer>
</template>

<style lang="less">
.execution-details {
  .run-state {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 20px;
    color: #646a73;
  }
  .current-node {
    margin-left: auto;
    font-size: 12px;
  }
  .attempt-select {
    width: 132px;
    margin-left: 8px;
  }
  .title {
    font-weight: 500;
    font-size: 16px;
    line-height: 24px;
    margin-bottom: 16px;
  }
  .overview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }
  .overview .item {
    height: 86px;
    border-radius: 12px;
    border: 1px solid #dee0e3;
    padding: 16px;
  }
  .overview .compact-metric {
    height: 86px;
  }
  .overview .ed-icon {
    float: left;
    margin: 8px 12px 0 0;
  }
  .overview .name {
    color: #646a73;
    font-size: 14px;
  }
  .overview .value {
    font-weight: 500;
    font-size: 20px;
    margin-top: 4px;
    color: #1f2329;
  }
  .list-item {
    border: 1px solid #dee0e3;
    border-radius: 12px;
    margin-bottom: 8px;
    overflow: hidden;
  }
  .phase-group {
    margin-bottom: 18px;
  }
  .phase-title {
    margin: 0 0 8px 4px;
    color: #646a73;
    font-size: 13px;
    font-weight: 500;
  }
  .header {
    display: flex;
    align-items: center;
    padding: 16px;
    cursor: pointer;
  }
  .header .name,
  .status {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .header .name {
    font-weight: 500;
    font-size: 14px;
  }
  .status {
    margin-left: auto;
    color: #646a73;
  }
  .summary {
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 12px;
  }
  .time {
    font-size: 12px;
  }
  .shrink {
    transition: transform 0.15s;
  }
  .shrink.expand {
    transform: rotate(90deg);
  }
  .degraded {
    color: #e6a23c;
  }
}
</style>
