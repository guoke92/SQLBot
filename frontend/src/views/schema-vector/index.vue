<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import { useI18n } from 'vue-i18n'
import {
  schemaVectorApi,
  type SchemaVectorJob,
  type SchemaVectorRow,
} from '@/api/schemaVector'

const { t } = useI18n()

const loading = ref(false)
const syncing = ref(false)
const items = ref<SchemaVectorRow[]>([])
const job = ref<SchemaVectorJob | null>(null)
const pollTimer = ref<number | null>(null)

const isRunning = computed(() => job.value?.status === 'running')

const loadStatus = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const data = await schemaVectorApi.status()
    items.value = data?.items || []
    job.value = data?.job || null
  } finally {
    if (!silent) loading.value = false
  }
}

const stateLabel = (state: string) => {
  const key = `schema_vector.state_${state}`
  const label = t(key)
  return label === key ? state : label
}

const jobStatusLabel = (status?: string) => {
  if (!status) return '-'
  const key = `schema_vector.job_${status}`
  const label = t(key)
  return label === key ? status : label
}

const syncOne = async (dsId?: number) => {
  syncing.value = true
  try {
    const result = await schemaVectorApi.sync(dsId)
    job.value = result
    ElMessage.success(t('schema_vector.sync_started'))
    await loadStatus(true)
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message
    if (String(detail || '').includes('already running')) {
      ElMessage.warning(t('schema_vector.sync_busy'))
    } else {
      ElMessage.error(detail || t('schema_vector.sync_failed'))
    }
  } finally {
    syncing.value = false
  }
}

const startPolling = () => {
  stopPolling()
  pollTimer.value = window.setInterval(async () => {
    await loadStatus(true)
    if (!isRunning.value) {
      // keep a light poll while page is open
    }
  }, 2500)
}

const stopPolling = () => {
  if (pollTimer.value != null) {
    window.clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

onMounted(async () => {
  await loadStatus()
  startPolling()
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<template>
  <main v-loading="loading" class="schema-vector-page">
    <div class="sv-toolbar">
      <div>
        <h2 class="sv-title">{{ t('schema_vector.title') }}</h2>
        <p class="sv-subtitle">{{ t('schema_vector.hint') }}</p>
      </div>
      <div class="sv-actions">
        <el-button @click="loadStatus()">{{ t('schema_vector.refresh') }}</el-button>
        <el-button type="primary" :loading="syncing || isRunning" @click="syncOne()">
          {{ t('schema_vector.sync_all') }}
        </el-button>
      </div>
    </div>

    <el-card shadow="never" class="sv-job-card">
      <div class="sv-job-row">
        <div>
          <div class="sv-job-label">{{ t('schema_vector.job_status') }}</div>
          <div class="sv-job-value">{{ jobStatusLabel(job?.status) }}</div>
        </div>
        <div>
          <div class="sv-job-label">{{ t('schema_vector.job_phase') }}</div>
          <div class="sv-job-value">{{ job?.phase || '-' }}</div>
        </div>
        <div>
          <div class="sv-job-label">{{ t('schema_vector.job_message') }}</div>
          <div class="sv-job-value">{{ job?.message || '-' }}</div>
        </div>
        <div>
          <div class="sv-job-label">{{ t('schema_vector.job_progress') }}</div>
          <div class="sv-job-value">
            {{ t('schema_vector.job_counts', {
              tables: job?.table_docs || 0,
              fields: job?.field_docs || 0,
              relations: job?.relation_docs || 0,
              embedded: job?.embedded_docs || 0,
              skipped: job?.skipped_docs || 0,
            }) }}
          </div>
        </div>
      </div>
      <div v-if="job?.error" class="sv-job-error">{{ job.error }}</div>
      <div class="sv-job-meta">
        <span>{{ t('schema_vector.started_at') }}: {{ job?.started_at || '-' }}</span>
        <span>{{ t('schema_vector.finished_at') }}: {{ job?.finished_at || '-' }}</span>
        <span v-if="job?.ds_ids?.length">
          {{ t('schema_vector.scope_ds') }}: {{ job.ds_ids.join(', ') }}
        </span>
        <span v-else>{{ t('schema_vector.scope_all') }}</span>
      </div>
    </el-card>

    <el-table :data="items" class="sv-table" stripe>
      <el-table-column prop="ds_id" :label="t('schema_vector.ds_id')" width="90" />
      <el-table-column prop="name" :label="t('schema_vector.ds_name')" min-width="160" />
      <el-table-column :label="t('schema_vector.state')" width="120">
        <template #default="{ row }">
          <el-tag
            :type="
              row.state === 'ready'
                ? 'success'
                : row.state === 'indexing'
                  ? 'warning'
                  : row.state === 'missing' || row.state === 'partial'
                    ? 'danger'
                    : 'info'
            "
            size="small"
          >
            {{ stateLabel(row.state) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('schema_vector.catalog')" min-width="160">
        <template #default="{ row }">
          {{ row.table_embeddings }} / {{ row.checked_tables }}
        </template>
      </el-table-column>
      <el-table-column :label="t('schema_vector.docs')" min-width="220">
        <template #default="{ row }">
          {{ t('schema_vector.doc_counts', {
            total: row.schema_docs,
            embedded: row.schema_embedded,
            tables: row.schema_tables,
            fields: row.schema_fields,
            relations: row.schema_relations,
          }) }}
        </template>
      </el-table-column>
      <el-table-column prop="update_time" :label="t('schema_vector.update_time')" min-width="160" />
      <el-table-column :label="t('schema_vector.actions')" width="140" fixed="right">
        <template #default="{ row }">
          <el-button
            link
            type="primary"
            :disabled="syncing || isRunning"
            @click="syncOne(row.ds_id)"
          >
            {{ t('schema_vector.sync_one') }}
          </el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty :description="t('schema_vector.empty')" />
      </template>
    </el-table>
  </main>
</template>

<style scoped>
.schema-vector-page {
  width: 100%;
  min-height: 100%;
  padding: 16px 24px 24px;
  box-sizing: border-box;
  background: var(--el-bg-color);
}

.sv-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.sv-title {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
}

.sv-subtitle {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.sv-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.sv-job-card {
  margin-bottom: 16px;
}

.sv-job-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.sv-job-label {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-bottom: 4px;
}

.sv-job-value {
  font-size: 13px;
  word-break: break-word;
}

.sv-job-error {
  margin-top: 10px;
  color: var(--el-color-danger);
  font-size: 13px;
}

.sv-job-meta {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.sv-table {
  width: 100%;
}

@media (max-width: 960px) {
  .sv-job-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
