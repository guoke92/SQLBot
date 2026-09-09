<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import { useI18n } from 'vue-i18n'
import { knowledgeApi, type WikiCorpusRow } from '@/api/knowledge'
import { datasourceApi } from '@/api/datasource'

const { t } = useI18n()

const loading = ref(false)
const corpora = ref<WikiCorpusRow[]>([])
const datasources = ref<{ id: number; name: string }[]>([])
const pollTimer = ref<number | null>(null)

const importVisible = ref(false)
const importSubmitting = ref(false)
const importForm = reactive({
  corpus_key: 'pplatform',
  pages_dir: 'docs/wiki-knowledge/pplatform/wiki-pages',
  replace: true,
})

const bindVisible = ref(false)
const bindSubmitting = ref(false)
const bindForm = reactive({
  corpus_key: '',
  datasource_id: undefined as number | undefined,
})
const suggestedRemap = ref<Record<string, string>>({})

const hasIndexing = computed(() => corpora.value.some((row) => row.status === 'indexing'))

const loadCorpora = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    corpora.value = (await knowledgeApi.listCorpora()) || []
  } finally {
    if (!silent) loading.value = false
  }
}

const loadDatasources = async () => {
  const list = (await datasourceApi.list()) as { id: number; name: string }[]
  datasources.value = list || []
}

const statusLabel = (status: string) => {
  if (status === 'ready') return t('knowledge.wiki_status_ready')
  if (status === 'indexing') return t('knowledge.wiki_status_indexing')
  if (status === 'failed') return t('knowledge.wiki_status_failed')
  return status
}

const retryEmbed = async (row: WikiCorpusRow) => {
  await knowledgeApi.retryEmbed(row.corpus_key)
  ElMessage.success(t('knowledge.wiki_retry_done'))
  await loadCorpora()
}

const bindingText = (row: WikiCorpusRow) => {
  if (!row.bindings?.length) return t('knowledge.wiki_unbound')
  return row.bindings
    .map((item) => item.datasource_name || String(item.datasource_id))
    .join(', ')
}

const openImport = (row?: WikiCorpusRow) => {
  if (row && typeof row.corpus_key === 'string') {
    importForm.corpus_key = row.corpus_key
    importForm.pages_dir = row.source_path || importForm.pages_dir
    importForm.replace = true
  }
  importVisible.value = true
}

const submitImport = async () => {
  if (!importForm.corpus_key.trim() || !importForm.pages_dir.trim()) {
    ElMessage.warning(t('knowledge.wiki_import_required'))
    return
  }
  importSubmitting.value = true
  try {
    const result = await knowledgeApi.importCorpus({
      corpus_key: importForm.corpus_key.trim(),
      pages_dir: importForm.pages_dir.trim(),
      replace: importForm.replace,
    })
    ElMessage.success(
      t('knowledge.wiki_import_done', {
        total: result.total,
        published: result.published,
        draft: result.draft,
        failed: result.failed,
      })
    )
    importVisible.value = false
    await loadCorpora()
  } finally {
    importSubmitting.value = false
  }
}

const openBind = (row?: WikiCorpusRow) => {
  bindForm.corpus_key = row?.corpus_key || corpora.value[0]?.corpus_key || ''
  bindForm.datasource_id = undefined
  suggestedRemap.value = {}
  bindVisible.value = true
}

const refreshRemap = async () => {
  if (!bindForm.corpus_key || !bindForm.datasource_id) {
    suggestedRemap.value = {}
    return
  }
  try {
    const data = await knowledgeApi.suggestRemap(bindForm.corpus_key, bindForm.datasource_id)
    suggestedRemap.value = data?.remap_databases || {}
  } catch {
    suggestedRemap.value = {}
  }
}

const submitBind = async () => {
  if (!bindForm.corpus_key || !bindForm.datasource_id) {
    ElMessage.warning(t('knowledge.wiki_bind_required'))
    return
  }
  bindSubmitting.value = true
  try {
    await knowledgeApi.bindCorpus({
      corpus_key: bindForm.corpus_key,
      datasource_id: bindForm.datasource_id,
      remap_databases: suggestedRemap.value,
    })
    ElMessage.success(t('knowledge.wiki_bind_done'))
    bindVisible.value = false
    await loadCorpora()
  } finally {
    bindSubmitting.value = false
  }
}

const unbindDs = async (datasourceId: number) => {
  await ElMessageBox.confirm(t('knowledge.wiki_unbind_confirm'), t('knowledge.confirm'), {
    type: 'warning',
  })
  await knowledgeApi.unbindDatasource(datasourceId)
  ElMessage.success(t('knowledge.wiki_unbind_done'))
  await loadCorpora()
}

const removeCorpus = async (row: WikiCorpusRow) => {
  await ElMessageBox.confirm(
    t('knowledge.wiki_delete_confirm', { key: row.corpus_key }),
    t('knowledge.confirm'),
    { type: 'warning' }
  )
  await knowledgeApi.deleteCorpus(row.corpus_key)
  ElMessage.success(t('knowledge.wiki_delete_done'))
  await loadCorpora()
}

const startPolling = () => {
  if (pollTimer.value != null) return
  pollTimer.value = window.setInterval(() => {
    if (hasIndexing.value) {
      loadCorpora(true)
    }
  }, 4000)
}

onMounted(async () => {
  await Promise.all([loadCorpora(), loadDatasources()])
  startPolling()
})

onBeforeUnmount(() => {
  if (pollTimer.value != null) {
    window.clearInterval(pollTimer.value)
    pollTimer.value = null
  }
})
</script>

<template>
  <main class="knowledge-page">
    <div class="wiki-toolbar">
      <div>
        <h2 class="wiki-title">{{ t('knowledge.wiki_manage') }}</h2>
        <p class="wiki-subtitle">{{ t('knowledge.wiki_manage_hint') }}</p>
      </div>
      <div class="wiki-actions">
        <el-button @click="openBind()">{{ t('knowledge.wiki_bind') }}</el-button>
        <el-button type="primary" @click="openImport()">{{ t('knowledge.wiki_import') }}</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="corpora" border stripe class="wiki-table">
      <el-table-column prop="corpus_key" :label="t('knowledge.wiki_corpus_key')" min-width="140" />
      <el-table-column :label="t('knowledge.wiki_status')" min-width="220">
        <template #default="{ row }">
          <div>{{ statusLabel(row.status) }}</div>
          <div class="wiki-embed-counts">
            <span class="wiki-ok">{{ t('knowledge.wiki_embed_ok') }} {{ row.embedded_chunks || 0 }}</span>
            <span
              class="wiki-fail"
              :class="{ 'is-zero': !(row.failed_chunks > 0) }"
            >
              {{ t('knowledge.wiki_embed_fail') }} {{ row.failed_chunks || 0 }}
            </span>
          </div>
          <div v-if="row.embed_error && row.failed_chunks" class="wiki-embed-error">
            {{ row.embed_error }}
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="t('knowledge.wiki_pages')" min-width="160">
        <template #default="{ row }">
          {{ row.page_count }}
          ({{ t('knowledge.wiki_published') }} {{ row.published_count }} /
          {{ t('knowledge.wiki_draft') }} {{ row.draft_count }})
        </template>
      </el-table-column>
      <el-table-column prop="embedded_chunks" :label="t('knowledge.wiki_chunks')" width="120" />
      <el-table-column :label="t('knowledge.wiki_bound_ds')" min-width="180">
        <template #default="{ row }">
          <div>{{ bindingText(row) }}</div>
          <div v-for="item in row.bindings" :key="item.datasource_id" class="wiki-bind-row">
            <el-button link type="primary" @click="unbindDs(item.datasource_id)">
              {{ t('knowledge.wiki_unbind') }}
            </el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="generation" :label="t('knowledge.wiki_generation')" width="90" />
      <el-table-column :label="t('knowledge.actions')" width="320" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openBind(row)">{{ t('knowledge.wiki_bind') }}</el-button>
          <el-button
            v-if="row.status !== 'ready' || (row.failed_chunks || 0) > 0"
            link
            type="warning"
            @click="retryEmbed(row)"
          >
            {{ t('knowledge.wiki_retry_embed') }}
          </el-button>
          <el-button link type="primary" @click="openImport(row)">{{ t('knowledge.wiki_reimport') }}</el-button>
          <el-button link type="danger" @click="removeCorpus(row)">{{ t('knowledge.wiki_delete') }}</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty :description="t('knowledge.wiki_empty')" />
      </template>
    </el-table>

    <el-dialog v-model="importVisible" :title="t('knowledge.wiki_import')" width="560px">
      <el-form label-position="top">
        <el-form-item :label="t('knowledge.wiki_corpus_key')" required>
          <el-input v-model="importForm.corpus_key" />
        </el-form-item>
        <el-form-item :label="t('knowledge.wiki_pages_dir')" required>
          <el-input v-model="importForm.pages_dir" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="importForm.replace">{{ t('knowledge.wiki_replace') }}</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importVisible = false">{{ t('knowledge.cancel') }}</el-button>
        <el-button type="primary" :loading="importSubmitting" @click="submitImport">
          {{ t('knowledge.confirm') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="bindVisible" :title="t('knowledge.wiki_bind')" width="560px">
      <el-form label-position="top">
        <el-form-item :label="t('knowledge.wiki_corpus_key')" required>
          <el-select v-model="bindForm.corpus_key" style="width: 100%" @change="refreshRemap">
            <el-option
              v-for="row in corpora"
              :key="row.corpus_key"
              :label="row.corpus_key"
              :value="row.corpus_key"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('knowledge.wiki_datasource')" required>
          <el-select
            v-model="bindForm.datasource_id"
            style="width: 100%"
            filterable
            @change="refreshRemap"
          >
            <el-option
              v-for="ds in datasources"
              :key="ds.id"
              :label="`${ds.name} (#${ds.id})`"
              :value="ds.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="Object.keys(suggestedRemap).length" :label="t('knowledge.wiki_remap')">
          <pre class="wiki-remap">{{ JSON.stringify(suggestedRemap, null, 2) }}</pre>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindVisible = false">{{ t('knowledge.cancel') }}</el-button>
        <el-button type="primary" :loading="bindSubmitting" @click="submitBind">
          {{ t('knowledge.confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </main>
</template>

<style scoped>
.knowledge-page {
  width: 100%;
  min-height: 100%;
  padding: 16px 24px 24px;
  box-sizing: border-box;
  background: var(--el-bg-color);
}

.wiki-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.wiki-title {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
}

.wiki-subtitle {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.wiki-table {
  width: 100%;
}

.wiki-bind-row {
  margin-top: 2px;
}

.wiki-remap {
  margin: 0;
  font-size: 12px;
  background: var(--el-fill-color-light);
  padding: 8px 12px;
  border-radius: 4px;
  white-space: pre-wrap;
}

.wiki-embed-counts {
  display: flex;
  gap: 10px;
  font-size: 12px;
  margin-top: 2px;
}

.wiki-ok {
  color: var(--el-color-success);
}

.wiki-fail {
  color: var(--el-color-danger);
}

.wiki-fail.is-zero {
  color: var(--el-text-color-secondary);
}

.wiki-embed-error {
  margin-top: 4px;
  font-size: 12px;
  color: var(--el-color-danger);
  line-height: 1.4;
  word-break: break-all;
}
</style>
