<script lang="ts" setup>
/**
 * Agent configuration console: system prompt, tools, pre-execute rules, loop bounds.
 *
 * Draft / publish / rollback are one atomic unit — the three blocks are always
 * edited and released together, matching the backend's single versioned row.
 */
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { agentConfigApi } from '@/api/agentConfig'
import type {
  AgentConfigDetail,
  AgentConfigMeta,
  AgentConfigSnapshot,
  AgentToolOverride,
} from '@/api/agentConfig'
import { formatTimestamp } from '@/utils/date'

interface ToolRow extends AgentToolOverride {
  name: string
}

interface ParamRow {
  key: string
  label_key: string
  default: number
  minimum: number
  maximum: number
  value: number
}

interface RuleRow {
  key: string
  label_key: string
  defaultEnabled: boolean
  enabled: boolean
}

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const publishing = ref(false)
const rollingBack = ref<number | null>(null)

const meta = ref<AgentConfigMeta | null>(null)
const detail = ref<AgentConfigDetail | null>(null)

const activeTab = ref('prompt')
const promptBody = ref('')
const changeNote = ref('')
const toolRows = ref<ToolRow[]>([])
const paramRows = ref<ParamRow[]>([])
const ruleRows = ref<RuleRow[]>([])

/** Server state the editor was seeded from — used for dirty detection + discard. */
const baseline = ref('')

const requiredTools = computed(() => new Set(meta.value?.required_tool_names ?? []))
const budgetRange = computed(() => {
  const bounds = meta.value?.tool_round_budget
  if (!bounds) return [] as number[]
  const out: number[] = []
  for (let n = bounds.min; n <= bounds.max; n += 1) out.push(n)
  return out
})

/** Normalised snapshot — the exact shape the PUT endpoint validates. */
const currentSnapshot = (): AgentConfigSnapshot => ({
  prompt_body: promptBody.value,
  tools: Object.fromEntries(
    toolRows.value.map((row) => [
      row.name,
      {
        enabled: row.enabled,
        description: row.description?.trim() ? row.description : null,
        parallel_safe: row.parallel_safe,
        round_budget: row.round_budget,
      },
    ])
  ),
  loop_params: Object.fromEntries(paramRows.value.map((row) => [row.key, row.value])),
  sql_rules: Object.fromEntries(ruleRows.value.map((row) => [row.key, { enabled: row.enabled }])),
  change_note: changeNote.value.trim() || null,
})

const fingerprint = (payload: unknown) => JSON.stringify(payload)
const dirty = computed(() => !!baseline.value && fingerprint(currentSnapshot()) !== baseline.value)

const isRequired = (name: string) => requiredTools.value.has(name)

const toolLabel = (name: string) => {
  const key = `agent_config.tools.${name}`
  const label = t(key)
  return label === key ? name : label
}

const fmtTime = (value?: string | null) =>
  value ? formatTimestamp(new Date(value).getTime(), 'YYYY-MM-DD HH:mm:ss') : '-'

const sourceLabel = computed(() => {
  const source = detail.value?.source ?? 'code'
  return t(`agent_config.source.${source}`)
})

const activeVersionText = computed(() => {
  const no = detail.value?.active_version_no
  return no ? `v${no}` : t('agent_config.version_none')
})

const warning = computed(() => {
  if (!detail.value) return ''
  const live = detail.value.active_version_no
  if (detail.value.source === 'draft') {
    if (!live) return t('agent_config.warning_draft_unpublished')
    return t('agent_config.warning_draft', { version: `v${live}` })
  }
  if (detail.value.source === 'code') {
    return t('agent_config.warning_code')
  }
  return ''
})

const promptRequiredMarkers = computed(() => meta.value?.prompt.required_markers ?? [])
const hasPlaceholder = computed(() =>
  promptBody.value.includes(meta.value?.prompt.placeholder ?? '{execution_limit}')
)
const promptLengthOk = computed(() => {
  const spec = meta.value?.prompt
  if (!spec) return true
  const size = promptBody.value.length
  return size >= spec.min_chars && size <= spec.max_chars
})

const canPublish = computed(
  () =>
    !!meta.value &&
    !loading.value &&
    !publishing.value &&
    (dirty.value || !!detail.value?.draft_version_no)
)

const applyDetail = (payload: AgentConfigDetail) => {
  detail.value = payload
  const spec = meta.value
  promptBody.value = payload.snapshot.prompt_body ?? ''
  changeNote.value = payload.snapshot.change_note ?? ''
  toolRows.value = (spec?.tool_names ?? Object.keys(payload.snapshot.tools ?? {})).map((name) => {
    const override = payload.snapshot.tools?.[name]
    return {
      name,
      enabled: override?.enabled ?? true,
      description: override?.description ?? '',
      parallel_safe: override?.parallel_safe ?? null,
      round_budget: override?.round_budget ?? null,
    }
  })
  paramRows.value = (spec?.params ?? []).map((item) => ({
    key: item.key,
    label_key: item.label_key,
    default: item.default,
    minimum: item.minimum,
    maximum: item.maximum,
    value: payload.snapshot.loop_params?.[item.key] ?? item.default,
  }))
  ruleRows.value = (spec?.sql_rules ?? []).map((item) => ({
    key: item.key,
    label_key: item.label_key,
    defaultEnabled: item.default_enabled,
    enabled: payload.snapshot.sql_rules?.[item.key]?.enabled ?? item.default_enabled,
  }))
  baseline.value = fingerprint(currentSnapshot())
}

const load = async () => {
  loading.value = true
  try {
    if (!meta.value) {
      meta.value = (await agentConfigApi.getMeta()) || null
    }
    const payload = (await agentConfigApi.get()) || null
    if (payload) {
      applyDetail(payload)
    }
  } catch {
    // The shared interceptor already surfaced the failure.
  } finally {
    loading.value = false
  }
}

const onSaveDraft = async () => {
  saving.value = true
  try {
    const payload = (await agentConfigApi.saveDraft(currentSnapshot())) || null
    if (payload) applyDetail(payload)
    ElMessage.success(t('agent_config.save_success'))
    return true
  } catch {
    return false
  } finally {
    saving.value = false
  }
}

const onPublish = async () => {
  try {
    await ElMessageBox.confirm(t('agent_config.publish_confirm'), {
      confirmButtonType: 'primary',
      confirmButtonText: t('agent_config.publish'),
      cancelButtonText: t('common.cancel'),
      customClass: 'confirm-no_icon',
      autofocus: false,
    })
  } catch {
    return
  }
  publishing.value = true
  try {
    // Publishing always saves first so "what I see" is "what goes live".
    if (dirty.value) {
      const saved = await onSaveDraft()
      if (!saved) return
    }
    const payload = (await agentConfigApi.publish()) || null
    if (payload) applyDetail(payload)
    ElMessage.success(t('agent_config.publish_success'))
  } catch {
    // handled by interceptor
  } finally {
    publishing.value = false
  }
}

const onRollback = async (row: { id: number; version_no: number }) => {
  try {
    await ElMessageBox.confirm(t('agent_config.rollback_confirm', { version: row.version_no }), {
      confirmButtonType: 'primary',
      confirmButtonText: t('agent_config.rollback'),
      cancelButtonText: t('common.cancel'),
      customClass: 'confirm-no_icon',
      autofocus: false,
    })
  } catch {
    return
  }
  rollingBack.value = row.id
  try {
    const payload = (await agentConfigApi.rollback(row.id)) || null
    if (payload) applyDetail(payload)
    ElMessage.success(t('agent_config.rollback_success'))
  } catch {
    // handled by interceptor
  } finally {
    rollingBack.value = null
  }
}

const canRollback = (row: { id: number; version_no: number }) =>
  row.version_no !== detail.value?.active_version_no

const statusTagType = (status: string) => {
  if (status === 'published') return 'success'
  if (status === 'draft') return 'warning'
  return 'info'
}

const statusLabel = (status: string) => {
  const key = `agent_config.status_${status}`
  const label = t(key)
  return label === key ? status : label
}

onMounted(load)
</script>

<template>
  <div v-loading="loading" class="agent-config">
    <div class="ac-header">
      <div class="title">{{ t('agent_config.title') }}</div>
      <div class="hint">{{ t('agent_config.hint') }}</div>
    </div>

    <div v-if="detail" class="ac-status">
      <el-tag size="small" :type="detail.source === 'published' ? 'success' : 'info'">
        {{ sourceLabel }}
      </el-tag>
      <span class="ac-status-item">
        {{ t('agent_config.live_version') }}: <b>{{ activeVersionText }}</b>
      </span>
      <span v-if="detail.draft_version_no" class="ac-status-item">
        {{ t('agent_config.draft_version') }}: <b>v{{ detail.draft_version_no }}</b>
      </span>
      <el-tag v-if="dirty" size="small" type="warning">{{ t('agent_config.dirty') }}</el-tag>
      <div class="ac-spacer"></div>
      <el-input
        v-model="changeNote"
        class="ac-note"
        size="default"
        clearable
        :maxlength="meta?.change_note_max_chars"
        :placeholder="t('agent_config.change_note_placeholder')"
      />
      <el-button :loading="saving" :disabled="loading || publishing" @click="onSaveDraft">
        {{ t('agent_config.save_draft') }}
      </el-button>
      <el-button type="primary" :loading="publishing" :disabled="!canPublish" @click="onPublish">
        {{ t('agent_config.publish') }}
      </el-button>
      <el-button link :disabled="!dirty || loading" @click="load">
        {{ t('agent_config.discard') }}
      </el-button>
    </div>

    <el-alert
      v-if="warning"
      class="ac-alert"
      type="warning"
      show-icon
      :closable="false"
      :title="warning"
    />

    <div v-if="!meta && !loading" class="ac-failed">
      <span>{{ t('agent_config.load_failed') }}</span>
      <el-button link type="primary" @click="load">{{ t('common.refresh') }}</el-button>
    </div>

    <div v-else class="ac-scroll">
      <el-tabs v-if="meta" v-model="activeTab" class="ac-tabs">
        <el-tab-pane :label="t('agent_config.tabs.prompt')" name="prompt">
          <div class="ac-pane">
            <div class="ac-pane-hint">{{ t('agent_config.prompt_hint') }}</div>
            <div class="ac-prompt-meta">
              <span class="ac-counter" :class="{ bad: !promptLengthOk }">
                {{ promptBody.length }} / {{ meta.prompt.max_chars }}
              </span>
              <el-tag v-if="!hasPlaceholder" size="small" type="danger">
                {{ t('agent_config.prompt_missing_placeholder') }}
              </el-tag>
              <span class="ac-markers">
                {{ t('agent_config.prompt_required_markers') }}:
                <code
                  v-for="marker in promptRequiredMarkers"
                  :key="marker"
                  class="ac-marker"
                  :class="{ bad: !promptBody.includes(marker) }"
                >
                  {{ marker }}
                </code>
              </span>
            </div>
            <el-input
              v-model="promptBody"
              class="ac-prompt-editor"
              type="textarea"
              :rows="26"
              resize="vertical"
              spellcheck="false"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane :label="t('agent_config.tabs.tools')" name="tools">
          <div class="ac-pane">
            <div class="ac-pane-hint">{{ t('agent_config.tools_hint') }}</div>
            <el-table :data="toolRows" border class="ac-table">
              <el-table-column :label="t('agent_config.tool_name')" min-width="230">
                <template #default="{ row }">
                  <div class="ac-tool-name">{{ toolLabel(row.name) }}</div>
                  <div class="ac-tool-raw">
                    <code>{{ row.name }}</code>
                    <el-tag v-if="isRequired(row.name)" size="small" type="info">
                      {{ t('agent_config.tool_required') }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                :label="t('agent_config.tool_enabled')"
                width="90"
                align="center"
                header-align="center"
              >
                <template #default="{ row }">
                  <el-switch v-model="row.enabled" :disabled="isRequired(row.name)" />
                </template>
              </el-table-column>
              <el-table-column :label="t('agent_config.tool_description')" min-width="320">
                <template #default="{ row }">
                  <el-input
                    v-model="row.description"
                    type="textarea"
                    :autosize="{ minRows: 2, maxRows: 6 }"
                    :maxlength="meta.tool_description_max_chars"
                    :placeholder="t('agent_config.tool_description_placeholder')"
                  />
                </template>
              </el-table-column>
              <el-table-column
                :label="t('agent_config.tool_parallel_safe')"
                width="120"
                align="center"
                header-align="center"
              >
                <template #default="{ row }">
                  <el-tooltip
                    effect="dark"
                    placement="top"
                    :content="t('agent_config.tool_parallel_safe_hint')"
                  >
                    <el-switch :model-value="!!row.parallel_safe" disabled />
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column :label="t('agent_config.tool_round_budget')" width="180">
                <template #default="{ row }">
                  <el-select v-model="row.round_budget" class="ac-budget">
                    <el-option :label="t('agent_config.tool_round_budget_inherit')" :value="null" />
                    <el-option v-for="n in budgetRange" :key="n" :label="String(n)" :value="n" />
                  </el-select>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="t('agent_config.tabs.sql_rules')" name="sql_rules">
          <div class="ac-pane">
            <div class="ac-pane-hint">{{ t('agent_config.sql_rules_hint') }}</div>
            <div class="ac-params">
              <div v-for="row in ruleRows" :key="row.key" class="ac-param">
                <div class="ac-param-label">
                  {{ t(row.label_key) }}
                  <code class="ac-param-key">{{ row.key }}</code>
                </div>
                <div class="ac-param-value">
                  <el-switch v-model="row.enabled" />
                  <el-button
                    link
                    size="small"
                    :disabled="row.enabled === row.defaultEnabled"
                    @click="row.enabled = row.defaultEnabled"
                  >
                    {{ t('agent_config.params_reset') }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="t('agent_config.tabs.params')" name="params">
          <div class="ac-pane">
            <div class="ac-pane-hint">{{ t('agent_config.params_hint') }}</div>
            <div class="ac-params">
              <div v-for="row in paramRows" :key="row.key" class="ac-param">
                <div class="ac-param-label">
                  {{ t(row.label_key) }}
                  <code class="ac-param-key">{{ row.key }}</code>
                </div>
                <div class="ac-param-value">
                  <el-input-number
                    v-model="row.value"
                    controls-position="right"
                    :min="row.minimum"
                    :max="row.maximum"
                    :step="1"
                  />
                  <span class="ac-param-default">
                    {{ t('agent_config.params_default', { value: row.default }) }}
                  </span>
                  <el-button
                    link
                    size="small"
                    :disabled="row.value === row.default"
                    @click="row.value = row.default"
                  >
                    {{ t('agent_config.params_reset') }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="t('agent_config.tabs.versions')" name="versions">
          <div class="ac-pane">
            <div class="ac-pane-hint">{{ t('agent_config.versions_hint') }}</div>
            <el-table :data="detail?.versions ?? []" border class="ac-table">
              <el-table-column :label="t('agent_config.version_no')" width="100">
                <template #default="{ row }">v{{ row.version_no }}</template>
              </el-table-column>
              <el-table-column :label="t('agent_config.status')" width="110">
                <template #default="{ row }">
                  <el-tag size="small" :type="statusTagType(row.status)">
                    {{ statusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('agent_config.change_note')" min-width="200">
                <template #default="{ row }">
                  <span class="ac-note-cell">{{ row.change_note || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('agent_config.create_time')" width="180">
                <template #default="{ row }">{{ fmtTime(row.create_time) }}</template>
              </el-table-column>
              <el-table-column :label="t('agent_config.published_time')" width="180">
                <template #default="{ row }">{{ fmtTime(row.published_time) }}</template>
              </el-table-column>
              <el-table-column :label="t('agent_config.actions')" width="110" fixed="right">
                <template #default="{ row }">
                  <el-button
                    link
                    type="primary"
                    :disabled="!canRollback(row)"
                    :loading="rollingBack === row.id"
                    @click="onRollback(row)"
                  >
                    {{ t('agent_config.rollback') }}
                  </el-button>
                </template>
              </el-table-column>
              <template #empty>
                <div class="ac-empty">{{ t('agent_config.versions_empty') }}</div>
              </template>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style lang="less" scoped>
.agent-config {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .title {
    font-weight: 500;
    font-size: 20px;
    line-height: 28px;
  }

  .hint {
    margin-top: 4px;
    color: #646a73;
    font-size: 13px;
    line-height: 22px;
  }

  .ac-status {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 16px;

    .ac-status-item {
      color: #646a73;
      font-size: 13px;
      line-height: 22px;

      b {
        color: #1f2329;
        font-weight: 500;
      }
    }

    .ac-spacer {
      flex: 1;
    }

    .ac-note {
      width: 240px;
    }
  }

  .ac-alert {
    margin-top: 12px;
  }

  .ac-failed {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 24px;
    color: #646a73;
    font-size: 14px;
  }

  // Own the scroll container so the page never depends on el-tabs internals.
  .ac-scroll {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 4px;
  }

  .ac-tabs {
    margin-top: 8px;

    :deep(.ed-tabs__header) {
      position: sticky;
      top: 0;
      z-index: 2;
      background: #fff;
      margin-bottom: 8px;
    }
  }

  .ac-pane-hint {
    color: #646a73;
    font-size: 13px;
    line-height: 22px;
    margin: 8px 0 12px;
  }

  .ac-prompt-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 8px;
    font-size: 13px;
    line-height: 22px;

    .ac-counter {
      color: #646a73;

      &.bad {
        color: var(--ed-color-danger);
      }
    }

    .ac-markers {
      color: #646a73;
    }

    .ac-marker {
      display: inline-block;
      margin-left: 6px;
      padding: 1px 6px;
      border-radius: 4px;
      background: #f5f6f7;
      color: #1f2329;
      font-size: 12px;

      &.bad {
        background: #fef0f0;
        color: var(--ed-color-danger);
      }
    }
  }

  .ac-prompt-editor {
    :deep(.ed-textarea__inner) {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12.5px;
      line-height: 20px;
    }
  }

  .ac-table {
    .ac-tool-name {
      font-weight: 500;
      font-size: 14px;
      line-height: 22px;
    }

    .ac-tool-raw {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 2px;

      code {
        color: #646a73;
        font-size: 12px;
      }
    }

    .ac-budget {
      width: 100%;
    }

    .ac-note-cell {
      word-break: break-word;
    }
  }

  .ac-params {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;

    .ac-param {
      border: 1px solid #dee0e3;
      border-radius: 12px;
      padding: 16px;

      .ac-param-label {
        font-size: 14px;
        line-height: 22px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;

        .ac-param-key {
          font-weight: 400;
          color: #646a73;
          font-size: 12px;
        }
      }

      .ac-param-value {
        margin-top: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;

        .ac-param-default {
          color: #646a73;
          font-size: 13px;
        }
      }
    }
  }

  .ac-empty {
    padding: 24px 0;
    color: #646a73;
    font-size: 13px;
  }
}
</style>
