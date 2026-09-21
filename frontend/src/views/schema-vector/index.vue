<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import { useI18n } from 'vue-i18n'
import {
  catalogIndexApi,
  type CatalogIndexJob,
  type CatalogIndexRow,
} from '@/api/catalogIndex'

const { t } = useI18n()

const loading = ref(false)
const syncing = ref(false)
const items = ref<CatalogIndexRow[]>([])
const job = ref<CatalogIndexJob | null>(null)
const pollTimer = ref<number | null>(null)

const isRunning = computed(() => job.value?.status === 'running')

const loadStatus = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const data = await catalogIndexApi.status()
    items.value = data?.items || []
    job.value = data?.job || null
  } finally {
    if (!silent) loading.value = false
  }
}

const stateLabel = (state: string) => {
  const key = `catalog_index.state_${state}`
  const label = t(key)
  return label === key ? state : label
}

const jobStatusLabel = (status?: string) => {
  if (!status) return '-'
  const key = `catalog_index.job_${status}`
  const label = t(key)
  return label === key ? status : label
}

const runAction = async (kind: 'extract' | 'wiki', dsId?: number) => {
  syncing.value = true
  try {
    const result =
      kind === 'wiki'
        ? await catalogIndexApi.generateWiki(Number(dsId))
        : await catalogIndexApi.extractValues(dsId)
    job.value = result
    ElMessage.success(
      t(kind === 'wiki' ? 'catalog_index.wiki_started' : 'catalog_index.extract_started'),
    )
    await loadStatus(true)
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message
    if (String(detail || '').includes('already running')) {
      ElMessage.warning(t('catalog_index.sync_busy'))
    } else {
      ElMessage.error(detail || t('catalog_index.sync_failed'))
    }
  } finally {
    syncing.value = false
  }
}

const startPolling = () => {
  stopPolling()
  pollTimer.value = window.setInterval(async () => {
    await loadStatus(true)
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
  <main v-loading="loading" class="catalog-index-page">
    <div class="ci-toolbar">
      <div>
        <h2 class="ci-title">{{ t('catalog_index.title') }}</h2>
        <p class="ci-subtitle">{{ t('catalog_index.hint') }}</p>
      </div>
      <div class="ci-actions">
        <el-button @click="loadStatus()">{{ t('catalog_index.refresh') }}</el-button>
        <el-button type="primary" :loading="syncing || isRunning" @click="runAction('extract')">
          {{ t('catalog_index.extract_all') }}
        </el-button>
      </div>
    </div>

    <el-card shadow="never" class="ci-job-card">
      <div class="ci-job-row">
        <div>
          <div class="ci-job-label">{{ t('catalog_index.job_status') }}</div>
          <div class="ci-job-value">{{ jobStatusLabel(job?.status) }}</div>
        </div>
        <div>
          <div class="ci-job-label">{{ t('catalog_index.job_phase') }}</div>
          <div class="ci-job-value">{{ job?.phase || job?.kind || '-' }}</div>
        </div>
        <div>
          <div class="ci-job-label">{{ t('catalog_index.job_message') }}</div>
          <div class="ci-job-value">{{ job?.message || '-' }}</div>
        </div>
        <div>
          <div class="ci-job-label">{{ t('catalog_index.job_progress') }}</div>
          <div class="ci-job-value">
            {{
              t('catalog_index.job_counts', {
                tables: job?.tables || 0,
                pages: job?.pages || 0,
                values: job?.value_rows || 0,
              })
            }}
          </div>
        </div>
      </div>
      <div v-if="job?.error" class="ci-job-error">{{ job.error }}</div>
      <div class="ci-job-meta">
        <span>{{ t('catalog_index.started_at') }}: {{ job?.started_at || '-' }}</span>
        <span>{{ t('catalog_index.finished_at') }}: {{ job?.finished_at || '-' }}</span>
        <span v-if="job?.ds_ids?.length">
          {{ t('catalog_index.scope_ds') }}: {{ job.ds_ids.join(', ') }}
        </span>
        <span v-else>{{ t('catalog_index.scope_all') }}</span>
      </div>
    </el-card>

    <el-table :data="items" class="ci-table" stripe>
      <el-table-column prop="ds_id" :label="t('catalog_index.ds_id')" width="90" />
      <el-table-column prop="name" :label="t('catalog_index.ds_name')" min-width="160" />
      <el-table-column :label="t('catalog_index.state')" width="120">
        <template #default="{ row }">
          <el-tag
            :type="
              row.state === 'ready'
                ? 'success'
                : row.state === 'partial'
                  ? 'warning'
                  : row.state === 'missing' || row.state === 'empty'
                    ? 'danger'
                    : 'info'
            "
            size="small"
          >
            {{ stateLabel(row.state) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('catalog_index.catalog')" min-width="140">
        <template #default="{ row }">
          {{ row.checked_tables }} / {{ row.tables }}
        </template>
      </el-table-column>
      <el-table-column :label="t('catalog_index.wiki')" min-width="200">
        <template #default="{ row }">
          <div v-if="row.corpus_key">
            {{ row.corpus_key }} · {{ row.wiki_pages }}
            {{ t('catalog_index.pages') }}
          </div>
          <div v-else>{{ t('catalog_index.wiki_unbound') }}</div>
        </template>
      </el-table-column>
      <el-table-column :label="t('catalog_index.values')" min-width="120">
        <template #default="{ row }">
          {{ row.value_rows }}
        </template>
      </el-table-column>
      <el-table-column :label="t('catalog_index.actions')" width="220" fixed="right">
        <template #default="{ row }">
          <el-button
            link
            type="primary"
            :disabled="syncing || isRunning"
            @click="runAction('wiki', row.ds_id)"
          >
            {{ t('catalog_index.generate_wiki') }}
          </el-button>
          <el-button
            link
            type="primary"
            :disabled="syncing || isRunning"
            @click="runAction('extract', row.ds_id)"
          >
            {{ t('catalog_index.extract_one') }}
          </el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty :description="t('catalog_index.empty')" />
      </template>
    </el-table>
  </main>
</template>

<style scoped>
.catalog-index-page {
  width: 100%;
  min-height: 100%;
  padding: 16px 24px 24px;
  box-sizing: border-box;
  background: var(--el-bg-color);
}

.ci-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.ci-title {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
}

.ci-subtitle {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.ci-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.ci-job-card {
  margin-bottom: 16px;
}

.ci-job-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.ci-job-label {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-bottom: 4px;
}

.ci-job-value {
  font-size: 13px;
  word-break: break-word;
}

.ci-job-error {
  margin-top: 10px;
  color: var(--el-color-danger);
  font-size: 13px;
}

.ci-job-meta {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.ci-table {
  width: 100%;
}

@media (max-width: 960px) {
  .ci-job-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
