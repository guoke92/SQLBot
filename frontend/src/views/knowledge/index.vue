<script lang="ts" setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { datasourceApi } from '@/api/datasource'
import {
  knowledgeApi,
  type KnowledgeImportReport,
  type KnowledgeImportRequest,
  type KnowledgePackageItem,
  type KnowledgePackageSummary,
  type KnowledgeSuggestion,
} from '@/api/knowledge'
import { useI18n } from 'vue-i18n'
import { formatTimestamp } from '@/utils/date'

const { t } = useI18n()
const activeTab = ref('triage')

const stagingList = ref<any[]>([])
const suggestions = ref<KnowledgeSuggestion[]>([])
const assetList = ref<any[]>([])
const loading = ref(false)
const importLoading = ref(false)
const importFileName = ref('')
const importDocuments = ref<Array<{ name: string; content: string }>>([])
const importReport = ref<KnowledgeImportReport | null>(null)
const importedPackages = ref<KnowledgePackageSummary[]>([])
const datasourceOptions = ref<Array<{ id: number; name: string }>>([])
const previewFingerprint = ref('')
const importForm = reactive({
  packageId: '',
  datasourceId: undefined as number | undefined,
})

const filters = reactive({ kind: '', trust_tier: '' })

const rejectDialogVisible = ref(false)
const rejectReason = ref('')
const rejectTarget = ref<number | null>(null)

const demoteDialogVisible = ref(false)
const demoteTarget = ref<number | null>(null)
const demoteForm = reactive({ to_tier: 'published', reason: '' })

async function loadTriage() {
  loading.value = true
  try {
    const [s, sg] = await Promise.all([knowledgeApi.getStaging(), knowledgeApi.getSuggestions()])
    stagingList.value = s.data || s
    suggestions.value = sg.data || sg
  } finally {
    loading.value = false
  }
}

async function loadAssets() {
  loading.value = true
  try {
    const params: any = {}
    if (filters.kind) params.kind = filters.kind
    if (filters.trust_tier) params.trust_tier = filters.trust_tier
    const res = await knowledgeApi.getAssets(params)
    assetList.value = res.data || res
  } finally {
    loading.value = false
  }
}

async function handleCertify(id: number) {
  await knowledgeApi.certify(id)
  ElMessage.success(t('knowledge.certify') + ' ✓')
  loadTriage()
}

function openReject(id: number) {
  rejectTarget.value = id
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

async function confirmReject() {
  if (!rejectTarget.value) return
  await knowledgeApi.reject(rejectTarget.value, rejectReason.value)
  rejectDialogVisible.value = false
  ElMessage.success(t('knowledge.reject') + ' ✓')
  loadTriage()
}

async function handlePromote(id: number) {
  await knowledgeApi.promote(id)
  ElMessage.success(t('knowledge.promote') + ' ✓')
  loadTriage()
}

function openDemote(id: number) {
  demoteTarget.value = id
  demoteForm.to_tier = 'published'
  demoteForm.reason = ''
  demoteDialogVisible.value = true
}

async function confirmDemote() {
  if (!demoteTarget.value) return
  await knowledgeApi.demote(demoteTarget.value, demoteForm.to_tier, demoteForm.reason)
  demoteDialogVisible.value = false
  ElMessage.success(t('knowledge.demote') + ' ✓')
  loadAssets()
}

async function handleDisable(row: any) {
  if (row.kind === 'rule') await knowledgeApi.disableRule(row.id)
  else await knowledgeApi.disable(row.id)
  ElMessage.success(t('knowledge.disable') + ' ✓')
  loadAssets()
}

function tierTagType(tier: string) {
  if (tier === 'certified') return 'success'
  if (tier === 'trusted') return 'warning'
  return 'info'
}

function onTabChange(tab: string) {
  if (tab === 'triage') loadTriage()
  else if (tab === 'assets') loadAssets()
  else if (tab === 'import') loadImportedPackages()
}

async function selectImportFiles(uploadFiles: Array<{ raw?: File; name?: string }>) {
  const supported = /\.(ya?ml|jsonl?)$/i
  const documents = await Promise.all(
    uploadFiles
      .filter((file) => file.raw && supported.test(file.name || file.raw.name))
      .map(async (file) => ({
        name:
          (file.raw as File & { webkitRelativePath?: string }).webkitRelativePath ||
          file.name ||
          file.raw!.name,
        content: await file.raw!.text(),
      }))
  )
  importDocuments.value = documents
  importFileName.value =
    documents.length === 1
      ? documents[0].name
      : t('knowledge.selected_documents', { count: documents.length })
  const firstPath = documents[0]?.name || ''
  importForm.packageId = firstPath.includes('/')
    ? firstPath.split('/')[0]
    : documents.length === 1
      ? firstPath.replace(/\.[^.]+$/, '')
      : `${firstPath.replace(/\.[^.]+$/, '') || 'knowledge'}-bundle`
  clearPreview()
}

function onImportInputChange(event: Event) {
  const input = event.target as HTMLInputElement
  void selectImportFiles(Array.from(input.files || []).map((raw) => ({ raw, name: raw.name })))
  input.value = ''
}

function importRequest(): KnowledgeImportRequest {
  return {
    documents: importDocuments.value,
    package_id: importForm.packageId || undefined,
    default_datasource_id: importForm.datasourceId,
  }
}

async function previewImport() {
  if (!importDocuments.value.length) {
    ElMessage.warning(t('knowledge.select_package'))
    return
  }
  importLoading.value = true
  try {
    const response = await knowledgeApi.previewImport(importRequest())
    importReport.value = response.data || response
    previewFingerprint.value = importReport.value?.package_fingerprint || ''
  } finally {
    importLoading.value = false
  }
}

async function applyImport() {
  if (!importReport.value || !importDocuments.value.length || !previewFingerprint.value) return
  importLoading.value = true
  try {
    const response = await knowledgeApi.applyImport({
      ...importRequest(),
      expected_preview_fingerprint: previewFingerprint.value,
    })
    importReport.value = response.data || response
    previewFingerprint.value = ''
    ElMessage.success(t('knowledge.import_complete'))
    void loadImportedPackages()
  } finally {
    importLoading.value = false
  }
}

async function loadImportedPackages() {
  const [packageResponse, datasourceResponse] = await Promise.all([
    knowledgeApi.getPackages(),
    datasourceApi.list(),
  ])
  importedPackages.value = packageResponse.data || packageResponse
  datasourceOptions.value = datasourceResponse.data || datasourceResponse
}

async function inspectPackage(packageId: string) {
  const response = await knowledgeApi.getPackageItems(packageId)
  const items: KnowledgePackageItem[] = response.data || response
  previewFingerprint.value = ''
  importReport.value = {
    package_id: packageId,
    package_fingerprint: '',
    dry_run: false,
    total: items.length,
    kind_counts: items.reduce((counts: Record<string, number>, item) => {
      counts[item.kind] = (counts[item.kind] || 0) + 1
      return counts
    }, {}),
    readiness_counts: items.reduce((counts: Record<string, number>, item) => {
      counts[item.readiness] = (counts[item.readiness] || 0) + 1
      return counts
    }, {}),
    action_counts: items.reduce((counts: Record<string, number>, item) => {
      const action = item.runtime_action || 'registered'
      counts[action] = (counts[action] || 0) + 1
      return counts
    }, {}),
    registry_action: 'registered',
    warnings: [],
    items: items.map((item: any) => ({
      item_id: item.item_id,
      kind: item.kind,
      readiness: item.readiness,
      action: item.runtime_action || 'registered',
      target_id: item.runtime_target_id,
      messages: item.messages || [],
      normalized: item.payload,
    })),
  }
}

function clearPreview() {
  importReport.value = null
  previewFingerprint.value = ''
}

function readinessTag(readiness: string) {
  if (readiness === 'ready') return 'success'
  if (readiness === 'invalid') return 'danger'
  if (readiness === 'review_required') return 'warning'
  return 'info'
}

function readinessLabel(readiness: string) {
  return t(`knowledge.readiness_${readiness}`)
}

function actionLabel(action: string) {
  const labels: Record<string, string> = {
    previewed: t('knowledge.action_previewed'),
    registered: t('knowledge.action_registered'),
    skipped: t('knowledge.action_skipped'),
    rejected: t('knowledge.action_rejected'),
    imported: t('knowledge.action_imported'),
    updated: t('knowledge.action_updated'),
    unchanged: t('knowledge.action_unchanged'),
    staged: t('knowledge.action_staged'),
    candidate: t('knowledge.action_candidate'),
    kept_confirmed: t('knowledge.action_kept_confirmed'),
    kept_rejected: t('knowledge.action_kept_rejected'),
    kept_disabled: t('knowledge.action_kept_disabled'),
  }
  return labels[action] || action
}

watch(() => [importForm.packageId, importForm.datasourceId], clearPreview)

onMounted(() => loadTriage())
</script>

<template>
  <div class="knowledge-container">
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane :label="t('knowledge.triage')" name="triage">
        <h4 style="margin: 0 0 12px">{{ t('knowledge.staging_queue') }}</h4>
        <el-table v-loading="loading" :data="stagingList" border size="small">
          <el-table-column prop="kind" label="Kind" width="100" />
          <el-table-column label="Label" min-width="200">
            <template #default="{ row }">
              {{ row.payload?.label || row.natural_key || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="trigger_id" label="Trigger" width="180" />
          <el-table-column prop="status" label="Status" width="100" />
          <el-table-column :label="t('knowledge.actions')" width="180">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="handleCertify(row.id)">
                {{ t('knowledge.certify') }}
              </el-button>
              <el-button type="danger" size="small" @click="openReject(row.id)">
                {{ t('knowledge.reject') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <h4 style="margin: 24px 0 12px">{{ t('knowledge.suggestions') }}</h4>
        <el-table :data="suggestions" border size="small">
          <el-table-column prop="label" label="Label" min-width="200" />
          <el-table-column prop="trust_tier" label="Tier" width="120">
            <template #default="{ row }">
              <el-tag :type="tierTagType(row.trust_tier)" size="small">{{ row.trust_tier }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="reproduce_count"
            :label="t('knowledge.reproductions')"
            width="110"
          />
          <el-table-column
            prop="successful_apply_count"
            :label="t('knowledge.applies')"
            width="100"
          />
          <el-table-column
            prop="positive_feedback_count"
            :label="t('knowledge.positive')"
            width="90"
          />
          <el-table-column
            prop="negative_feedback_count"
            :label="t('knowledge.negative')"
            width="90"
          />
          <el-table-column :label="t('knowledge.actions')" width="120">
            <template #default="{ row }">
              <el-button
                v-if="row.recommended_action === 'promote'"
                type="primary"
                size="small"
                @click="handlePromote(row.id)"
              >
                {{ t('knowledge.promote') }}
              </el-button>
              <el-tag v-else type="danger" size="small">{{ t('knowledge.needs_review') }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="t('knowledge.assets')" name="assets">
        <div style="margin-bottom: 12px; display: flex; gap: 12px">
          <el-select
            v-model="filters.kind"
            clearable
            placeholder="Kind"
            style="width: 150px"
            @change="loadAssets"
          >
            <el-option label="caliber" value="caliber" />
            <el-option label="rule" value="rule" />
          </el-select>
          <el-select
            v-model="filters.trust_tier"
            clearable
            placeholder="Trust Tier"
            style="width: 150px"
            @change="loadAssets"
          >
            <el-option label="certified" value="certified" />
            <el-option label="trusted" value="trusted" />
            <el-option label="published" value="published" />
          </el-select>
        </div>
        <el-table v-loading="loading" :data="assetList" border size="small">
          <el-table-column prop="kind" label="Kind" width="100" />
          <el-table-column prop="label" label="Label" min-width="200" />
          <el-table-column prop="trust_tier" label="Trust Tier" width="120">
            <template #default="{ row }">
              <el-tag :type="tierTagType(row.trust_tier)" size="small">{{ row.trust_tier }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="enabled" label="Enabled" width="80">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
                {{ row.enabled ? 'Yes' : 'No' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Created" width="160">
            <template #default="{ row }">
              {{ row.create_time ? formatTimestamp(row.create_time) : '-' }}
            </template>
          </el-table-column>
          <el-table-column :label="t('knowledge.actions')" width="180">
            <template #default="{ row }">
              <el-button v-if="row.kind === 'caliber'" size="small" @click="openDemote(row.id)">
                {{ t('knowledge.demote') }}
              </el-button>
              <el-button type="danger" size="small" @click="handleDisable(row)">
                {{ t('knowledge.disable') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="t('knowledge.import_package')" name="import">
        <el-alert
          :title="t('knowledge.import_description')"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        />
        <section class="import-section">
          <div class="section-title">{{ t('knowledge.import_source') }}</div>
          <div class="import-toolbar">
            <label class="file-picker el-button">
              {{ t('knowledge.select_files') }}
              <input
                type="file"
                multiple
                accept=".yaml,.yml,.json,.jsonl"
                @change="onImportInputChange"
              />
            </label>
            <label class="folder-picker el-button">
              {{ t('knowledge.select_folder') }}
              <input
                type="file"
                multiple
                webkitdirectory
                accept=".yaml,.yml,.json,.jsonl"
                @change="onImportInputChange"
              />
            </label>
            <span class="file-name" :title="importFileName">
              {{ importFileName || t('knowledge.no_package') }}
            </span>
          </div>
          <el-form class="import-form" label-position="top" inline>
            <el-form-item :label="t('knowledge.package_id')">
              <el-input v-model="importForm.packageId" style="width: 260px" />
            </el-form-item>
            <el-form-item :label="t('knowledge.datasource_scope')">
              <el-select
                v-model="importForm.datasourceId"
                clearable
                filterable
                :placeholder="t('knowledge.datasource_optional')"
                style="width: 260px"
              >
                <el-option
                  v-for="datasource in datasourceOptions"
                  :key="datasource.id"
                  :label="datasource.name"
                  :value="datasource.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item class="import-actions">
              <el-button :loading="importLoading" @click="previewImport">
                {{ t('knowledge.preview_import') }}
              </el-button>
              <el-button
                type="primary"
                :loading="importLoading"
                :disabled="!previewFingerprint || !importDocuments.length"
                @click="applyImport"
              >
                {{ t('knowledge.register_and_publish') }}
              </el-button>
            </el-form-item>
          </el-form>
        </section>

        <section v-if="importReport" class="import-section">
          <div class="section-title">{{ t('knowledge.import_result') }}</div>
          <div class="import-summary">
            <el-tag>{{ importReport.package_id }}</el-tag>
            <span>{{ t('knowledge.total_items', { count: importReport.total }) }}</span>
            <el-tag v-if="importReport.registry_action" type="success">
              {{ actionLabel(importReport.registry_action) }}
              <template v-if="importReport.registry_revision">
                · Revision {{ importReport.registry_revision }}
              </template>
            </el-tag>
            <span v-for="(count, key) in importReport.kind_counts" :key="`kind-${key}`">
              {{ t(`knowledge.kind_${key}`) }}: {{ count }}
            </span>
            <el-divider direction="vertical" />
            <span v-for="(count, key) in importReport.readiness_counts" :key="`readiness-${key}`">
              {{ readinessLabel(key) }}: {{ count }}
            </span>
            <template v-if="Object.keys(importReport.action_counts).length">
              <el-divider direction="vertical" />
              <span v-for="(count, key) in importReport.action_counts" :key="`action-${key}`">
                {{ actionLabel(key) }}: {{ count }}
              </span>
            </template>
          </div>
          <el-alert
            v-for="warning in importReport.warnings"
            :key="warning"
            :title="warning"
            type="warning"
            :closable="false"
            class="import-warning"
          />
          <el-table :data="importReport.items" border size="small" max-height="480">
            <el-table-column prop="item_id" label="ID" min-width="180" show-overflow-tooltip />
            <el-table-column prop="kind" label="Kind" width="120" />
            <el-table-column :label="t('knowledge.readiness')" width="150">
              <template #default="{ row }">
                <el-tag :type="readinessTag(row.readiness)">
                  {{ readinessLabel(row.readiness) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('knowledge.action')" width="130">
              <template #default="{ row }">{{ actionLabel(row.action) }}</template>
            </el-table-column>
            <el-table-column :label="t('knowledge.messages')" min-width="320">
              <template #default="{ row }">{{ row.messages.join('；') || '-' }}</template>
            </el-table-column>
          </el-table>
        </section>

        <section class="import-section">
          <div class="section-title">{{ t('knowledge.imported_packages') }}</div>
          <el-table :data="importedPackages" border size="small">
            <el-table-column
              prop="package_id"
              :label="t('knowledge.package_id')"
              min-width="220"
              show-overflow-tooltip
            />
            <el-table-column
              prop="title"
              :label="t('knowledge.package_title')"
              min-width="200"
              show-overflow-tooltip
            />
            <el-table-column prop="revision" label="Revision" width="100" />
            <el-table-column prop="item_count" :label="t('knowledge.item_count')" width="100" />
            <el-table-column :label="t('knowledge.actions')" width="100" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="inspectPackage(row.package_id)">
                  {{ t('knowledge.view') }}
                </el-button>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty :description="t('knowledge.no_imported_packages')" :image-size="72" />
            </template>
          </el-table>
        </section>
      </el-tab-pane>
    </el-tabs>

    <!-- Reject Dialog -->
    <el-dialog v-model="rejectDialogVisible" :title="t('knowledge.reject')" width="400px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="3"
        :placeholder="t('knowledge.reject_reason')"
      />
      <template #footer>
        <el-button @click="rejectDialogVisible = false">{{ t('knowledge.cancel') }}</el-button>
        <el-button type="primary" @click="confirmReject">{{ t('knowledge.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- Demote Dialog -->
    <el-dialog v-model="demoteDialogVisible" :title="t('knowledge.demote')" width="400px">
      <el-form label-width="80px">
        <el-form-item label="To Tier">
          <el-select v-model="demoteForm.to_tier">
            <el-option label="published" value="published" />
            <el-option label="trusted" value="trusted" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('knowledge.reason')">
          <el-input v-model="demoteForm.reason" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="demoteDialogVisible = false">{{ t('knowledge.cancel') }}</el-button>
        <el-button type="primary" @click="confirmDemote">{{ t('knowledge.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.knowledge-container {
  padding: 20px;
  height: 100%;
  overflow: auto;
}

.import-section {
  padding: 20px;
  margin-bottom: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
}

.section-title {
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 600;
}

.import-toolbar,
.import-summary {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.import-form {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 0 12px;
}

.import-form :deep(.el-form-item) {
  margin-right: 0;
  margin-bottom: 0;
}

.import-actions :deep(.el-form-item__content) {
  padding-bottom: 1px;
}

.file-name {
  max-width: 280px;
  overflow: hidden;
  color: var(--el-text-color-secondary);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-picker input,
.folder-picker input {
  display: none;
}

.import-warning {
  margin-bottom: 8px;
}

@media (max-width: 960px) {
  .knowledge-container {
    padding: 16px;
  }

  .import-section {
    padding: 16px;
  }

  .file-name {
    max-width: 100%;
    flex-basis: 100%;
  }
}
</style>
