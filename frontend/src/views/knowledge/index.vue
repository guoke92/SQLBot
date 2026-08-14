<script lang="ts" setup>
import { DocumentAdd, FolderOpened } from '@element-plus/icons-vue'
import { onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { datasourceApi } from '@/api/datasource'
import {
  knowledgeApi,
  type KnowledgeImportReport,
  type KnowledgeImportRequest,
  type KnowledgePackageDetail,
  type KnowledgePackageItem,
  type KnowledgePackageSummary,
  type KnowledgeReviewItem,
  type KnowledgeReviewPage,
  type KnowledgeSuggestion,
  type RuntimeKnowledgeItem,
  type RuntimeKnowledgePage,
} from '@/api/knowledge'
import KnowledgePackageWorkbench from './components/KnowledgePackageWorkbench.vue'
import KnowledgeReviewCenter from './components/KnowledgeReviewCenter.vue'
import RuntimeKnowledgeList from './components/RuntimeKnowledgeList.vue'

const { t } = useI18n()
const activeTab = ref('reviews')
const loading = ref(false)
const importLoading = ref(false)
const packageLoading = ref(false)
const reviewPage = ref<KnowledgeReviewPage | null>(null)
const runtimePage = ref<RuntimeKnowledgePage | null>(null)
const suggestions = ref<KnowledgeSuggestion[]>([])
const importedPackages = ref<KnowledgePackageSummary[]>([])
const packageDetail = ref<KnowledgePackageDetail | null>(null)
const importReport = ref<KnowledgeImportReport | null>(null)
const datasourceOptions = ref<Array<{ id: number; name: string }>>([])
const importDocuments = ref<Array<{ name: string; content: string }>>([])
const importFileName = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const folderInput = ref<HTMLInputElement | null>(null)
const selectedPackageId = ref('')
const previewFingerprint = ref('')
const importPanelOpen = ref(false)
const reportMode = ref<'preview' | 'applied' | 'registered'>('registered')
const importForm = reactive({ packageId: '', datasourceId: undefined as number | undefined })
let packageRequestSequence = 0

const rejectDialogVisible = ref(false)
const rejectReason = ref('')
const rejectTarget = ref<KnowledgeReviewItem | KnowledgePackageItem | null>(null)
const rejectSource = ref<'review' | 'package'>('review')
const demoteDialogVisible = ref(false)
const demoteTarget = ref<RuntimeKnowledgeItem | null>(null)
const demoteForm = reactive({ to_tier: 'published', reason: '' })

function unwrap<T>(response: { data?: T } | T): T {
  return (response as { data?: T }).data || (response as T)
}

async function loadReviews(query = { keyword: '', kind: '', page: 1, pageSize: 15 }) {
  loading.value = true
  try {
    const [reviews, suggestionResult] = await Promise.all([
      knowledgeApi.getReviews({
        keyword: query.keyword || undefined,
        kind: query.kind || undefined,
        page: query.page,
        page_size: query.pageSize,
      }),
      knowledgeApi.getSuggestions(),
    ])
    reviewPage.value = unwrap<KnowledgeReviewPage>(reviews)
    suggestions.value = unwrap<KnowledgeSuggestion[]>(suggestionResult)
  } finally {
    loading.value = false
  }
}

async function loadRuntime(
  query: {
    keyword: string
    kind: string
    enabled?: boolean
    page: number
    pageSize: number
  } = {
    keyword: '',
    kind: '',
    enabled: undefined,
    page: 1,
    pageSize: 15,
  }
) {
  loading.value = true
  try {
    const response = await knowledgeApi.getRuntimeAssets({
      keyword: query.keyword || undefined,
      kind: query.kind || undefined,
      enabled: query.enabled,
      page: query.page,
      page_size: query.pageSize,
    })
    runtimePage.value = unwrap<RuntimeKnowledgePage>(response)
  } finally {
    loading.value = false
  }
}

async function approveReview(item: KnowledgeReviewItem) {
  if (item.source === 'staging') await knowledgeApi.certify(item.id)
  else if (item.source === 'relation') await knowledgeApi.decideRelation(item.id, 'CONFIRMED')
  else if (item.package_id && item.item_id) {
    await knowledgeApi.advancePackageItem(item.package_id, item.item_id, {
      action: 'approve_publish',
      default_datasource_id: importForm.datasourceId,
    })
  }
  ElMessage.success(t('knowledge.review_completed'))
  await Promise.all([loadReviews(), loadRuntime()])
  if (selectedPackageId.value) await inspectPackage(selectedPackageId.value)
}

function openReviewReject(item: KnowledgeReviewItem) {
  rejectTarget.value = item
  rejectSource.value = 'review'
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

function openPackageReject(item: KnowledgePackageItem) {
  rejectTarget.value = item
  rejectSource.value = 'package'
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

async function confirmReject() {
  const target = rejectTarget.value
  if (!target) return
  if (rejectSource.value === 'package') {
    const item = target as KnowledgePackageItem
    await knowledgeApi.rejectPackageItem(selectedPackageId.value, item.item_id)
  } else {
    const item = target as KnowledgeReviewItem
    if (item.source === 'staging') await knowledgeApi.reject(item.id, rejectReason.value)
    else if (item.source === 'relation') await knowledgeApi.decideRelation(item.id, 'REJECTED')
    else if (item.package_id && item.item_id) {
      await knowledgeApi.rejectPackageItem(item.package_id, item.item_id)
    }
  }
  rejectDialogVisible.value = false
  ElMessage.success(t('knowledge.reject_completed'))
  await loadReviews()
  if (selectedPackageId.value) await inspectPackage(selectedPackageId.value)
}

async function handlePromote(item: KnowledgeSuggestion) {
  await knowledgeApi.promote(item.id)
  ElMessage.success(t('knowledge.promote') + ' ✓')
  await Promise.all([loadReviews(), loadRuntime()])
}

async function handleDisable(item: RuntimeKnowledgeItem) {
  if (item.kind === 'rule') await knowledgeApi.disableRule(item.id)
  else await knowledgeApi.disable(item.id)
  ElMessage.success(t('knowledge.disable') + ' ✓')
  await loadRuntime()
}

function openDemote(item: RuntimeKnowledgeItem) {
  demoteTarget.value = item
  demoteForm.to_tier = 'published'
  demoteForm.reason = ''
  demoteDialogVisible.value = true
}

async function confirmDemote() {
  if (!demoteTarget.value) return
  await knowledgeApi.demote(demoteTarget.value.id, demoteForm.to_tier, demoteForm.reason)
  demoteDialogVisible.value = false
  ElMessage.success(t('knowledge.demote') + ' ✓')
  await loadRuntime()
}

function onTabChange(tab: string) {
  if (tab === 'reviews') void loadReviews()
  else if (tab === 'runtime') void loadRuntime()
  else if (tab === 'packages') void loadImportedPackages()
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
    importReport.value = unwrap<KnowledgeImportReport>(
      await knowledgeApi.previewImport(importRequest())
    )
    previewFingerprint.value = importReport.value.package_fingerprint
    selectedPackageId.value = ''
    packageDetail.value = null
    reportMode.value = 'preview'
  } finally {
    importLoading.value = false
  }
}

async function applyImport() {
  if (!importReport.value || !importDocuments.value.length || !previewFingerprint.value) return
  importLoading.value = true
  try {
    const result = unwrap<KnowledgeImportReport>(
      await knowledgeApi.applyImport({
        ...importRequest(),
        expected_preview_fingerprint: previewFingerprint.value,
      })
    )
    importReport.value = result
    previewFingerprint.value = ''
    reportMode.value = 'applied'
    ElMessage.success(t('knowledge.import_complete'))
    await loadImportedPackages()
    await inspectPackage(result.package_id)
  } finally {
    importLoading.value = false
  }
}

async function loadImportedPackages() {
  const [packages, datasources] = await Promise.allSettled([
    knowledgeApi.getPackages(),
    datasourceApi.list(),
  ])
  if (packages.status === 'rejected') throw packages.reason
  importedPackages.value = unwrap<KnowledgePackageSummary[]>(packages.value)
  if (datasources.status === 'fulfilled') {
    datasourceOptions.value = unwrap<Array<{ id: number; name: string }>>(datasources.value)
  }
  if (!importedPackages.value.length) {
    importPanelOpen.value = true
    return
  }
  if (!selectedPackageId.value && reportMode.value === 'registered') {
    await inspectPackage(importedPackages.value[0].package_id)
  }
}

async function inspectPackage(
  packageId: string,
  query = { keyword: '', kind: '', readiness: '', page: 1, pageSize: 15 }
) {
  const sequence = ++packageRequestSequence
  packageLoading.value = true
  try {
    const response = await knowledgeApi.getPackageDetail(packageId, {
      keyword: query.keyword || undefined,
      kind: query.kind || undefined,
      readiness: query.readiness || undefined,
      page: query.page,
      page_size: query.pageSize,
    })
    if (sequence !== packageRequestSequence) return
    packageDetail.value = unwrap<KnowledgePackageDetail>(response)
    selectedPackageId.value = packageId
    importReport.value = null
    previewFingerprint.value = ''
    reportMode.value = 'registered'
  } finally {
    if (sequence === packageRequestSequence) packageLoading.value = false
  }
}

async function queryPackage(query: {
  keyword: string
  kind: string
  readiness: string
  page: number
  pageSize: number
}) {
  if (selectedPackageId.value) await inspectPackage(selectedPackageId.value, query)
}

async function advancePackageItem(
  item: KnowledgePackageItem,
  action: 'publish' | 'approve_publish'
) {
  await knowledgeApi.advancePackageItem(selectedPackageId.value, item.item_id, {
    action,
    default_datasource_id: importForm.datasourceId,
  })
  ElMessage.success(t('knowledge.advance_completed'))
  await Promise.all([inspectPackage(selectedPackageId.value), loadReviews(), loadRuntime()])
}

function gotoReview() {
  activeTab.value = 'reviews'
  void loadReviews()
}

function openImport() {
  importPanelOpen.value = true
  window.requestAnimationFrame(() =>
    document.querySelector('.import-entry')?.scrollIntoView({ behavior: 'smooth' })
  )
}

function clearPreview() {
  importReport.value = null
  previewFingerprint.value = ''
}

function invalidateImportPreview() {
  if (reportMode.value === 'preview' && previewFingerprint.value) clearPreview()
}

watch(() => [importForm.packageId, importForm.datasourceId], invalidateImportPreview)
onMounted(() => void loadReviews())
</script>

<template>
  <div class="knowledge-container">
    <el-tabs v-model="activeTab" class="knowledge-tabs" @tab-change="onTabChange">
      <el-tab-pane :label="t('knowledge.review_center')" name="reviews">
        <KnowledgeReviewCenter
          :page="reviewPage"
          :suggestions="suggestions"
          :loading="loading"
          @load="loadReviews"
          @approve="approveReview"
          @reject="openReviewReject"
          @promote="handlePromote"
        />
      </el-tab-pane>

      <el-tab-pane :label="t('knowledge.runtime_knowledge')" name="runtime">
        <RuntimeKnowledgeList
          :page="runtimePage"
          :loading="loading"
          @load="loadRuntime"
          @disable="handleDisable"
          @demote="openDemote"
        />
      </el-tab-pane>

      <el-tab-pane :label="t('knowledge.knowledge_packages')" name="packages">
        <section class="lifecycle-guide">
          <strong>{{ t('knowledge.lifecycle_title') }}</strong>
          <span>{{ t('knowledge.lifecycle_packages') }}</span
          ><i>→</i> <span>{{ t('knowledge.lifecycle_reviews') }}</span
          ><i>→</i>
          <span>{{ t('knowledge.lifecycle_runtime') }}</span>
        </section>

        <section class="import-entry">
          <button
            class="import-entry-toggle"
            type="button"
            @click="importPanelOpen = !importPanelOpen"
          >
            <span
              ><strong>{{ t('knowledge.import_new_package') }}</strong
              ><small>{{ t('knowledge.import_new_package_hint') }}</small></span
            >
            <span>{{ importPanelOpen ? t('knowledge.collapse') : t('knowledge.expand') }}</span>
          </button>
          <div v-show="importPanelOpen" class="import-entry-body">
            <div class="import-toolbar">
              <input
                ref="fileInput"
                class="native-file-input"
                type="file"
                multiple
                accept=".yaml,.yml,.json,.jsonl"
                @change="onImportInputChange"
              />
              <input
                ref="folderInput"
                class="native-file-input"
                type="file"
                multiple
                webkitdirectory
                accept=".yaml,.yml,.json,.jsonl"
                @change="onImportInputChange"
              />
              <el-button :icon="DocumentAdd" @click="fileInput?.click()">
                {{ t('knowledge.select_files') }}
              </el-button>
              <el-button :icon="FolderOpened" @click="folderInput?.click()">
                {{ t('knowledge.select_folder') }}
              </el-button>
              <div class="selected-source" :class="{ empty: !importFileName }">
                <strong>{{ importFileName || t('knowledge.no_package') }}</strong>
                <small>{{ t('knowledge.supported_package_files') }}</small>
              </div>
            </div>
            <el-form class="import-form" label-position="top">
              <el-form-item :label="t('knowledge.package_id')"
                ><el-input v-model="importForm.packageId"
              /></el-form-item>
              <el-form-item :label="t('knowledge.datasource_scope')">
                <el-select
                  v-model="importForm.datasourceId"
                  clearable
                  filterable
                  :placeholder="t('knowledge.datasource_optional')"
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
                <el-button :loading="importLoading" @click="previewImport">{{
                  t('knowledge.preview_import')
                }}</el-button>
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
          </div>
        </section>

        <KnowledgePackageWorkbench
          :packages="importedPackages"
          :detail="packageDetail"
          :preview="importReport"
          :selected-package-id="selectedPackageId"
          :loading="packageLoading"
          :mode="reportMode"
          @select-package="inspectPackage"
          @query="queryPackage"
          @advance="advancePackageItem"
          @reject="openPackageReject"
          @goto-review="gotoReview"
          @open-import="openImport"
        />
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="rejectDialogVisible" :title="t('knowledge.reject')" width="420px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="3"
        :placeholder="t('knowledge.reject_reason')"
      />
      <template #footer>
        <el-button @click="rejectDialogVisible = false">{{ t('knowledge.cancel') }}</el-button>
        <el-button type="danger" @click="confirmReject">{{ t('knowledge.confirm') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="demoteDialogVisible" :title="t('knowledge.demote')" width="420px">
      <el-form label-width="90px">
        <el-form-item :label="t('knowledge.trust_tier')">
          <el-select v-model="demoteForm.to_tier"
            ><el-option label="published" value="published" /><el-option
              label="trusted"
              value="trusted"
          /></el-select>
        </el-form-item>
        <el-form-item :label="t('knowledge.reason')"
          ><el-input v-model="demoteForm.reason" type="textarea" :rows="2"
        /></el-form-item>
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
  height: 100%;
  padding: 18px 24px 28px;
  overflow: auto;
  background: var(--el-fill-color-extra-light);
}
.knowledge-tabs {
  max-width: 1360px;
  margin: 0 auto;
}
.knowledge-tabs :deep(.el-tabs__header) {
  margin-bottom: 18px;
  background: var(--el-bg-color);
  border-radius: 9px 9px 0 0;
}
.knowledge-tabs :deep(.el-tabs__item) {
  height: 52px;
  padding: 0 24px;
  font-size: 15px;
  font-weight: 600;
}
.lifecycle-guide {
  display: flex;
  padding: 13px 16px;
  margin-bottom: 14px;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  color: var(--el-text-color-secondary);
  background: var(--el-color-primary-light-9);
  border: 1px solid var(--el-color-primary-light-8);
  border-radius: 9px;
}
.lifecycle-guide strong {
  margin-right: 8px;
  color: var(--el-text-color-primary);
}
.lifecycle-guide i {
  color: var(--el-text-color-placeholder);
  font-style: normal;
}
.import-entry {
  margin-bottom: 14px;
  overflow: hidden;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 9px;
}
.import-entry-toggle {
  display: flex;
  width: 100%;
  padding: 14px 18px;
  align-items: center;
  justify-content: space-between;
  color: var(--el-text-color-primary);
  text-align: left;
  cursor: pointer;
  background: transparent;
  border: 0;
}
.import-entry-toggle strong,
.import-entry-toggle small {
  display: block;
}
.import-entry-toggle small,
.import-entry-toggle > span:last-child {
  margin-top: 4px;
  color: var(--el-text-color-secondary);
}
.import-entry-body {
  padding: 14px 18px 18px;
  border-top: 1px solid var(--el-border-color-lighter);
}
.import-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.import-toolbar {
  padding-bottom: 13px;
  margin-bottom: 13px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.import-form {
  display: grid;
  align-items: end;
  gap: 12px;
  grid-template-columns: minmax(240px, 1fr) minmax(240px, 1fr) auto;
}
.import-form :deep(.el-form-item) {
  margin: 0;
}
.import-form :deep(.el-input),
.import-form :deep(.el-select) {
  width: 100%;
}
.native-file-input {
  display: none;
}
.selected-source {
  display: grid;
  min-width: 0;
  gap: 2px;
}
.selected-source strong {
  max-width: 520px;
  overflow: hidden;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.selected-source small,
.selected-source.empty strong {
  color: var(--el-text-color-secondary);
}
.import-actions :deep(.el-form-item__content) {
  flex-wrap: nowrap;
}
@media (max-width: 960px) {
  .knowledge-container {
    padding: 12px;
  }
  .knowledge-tabs :deep(.el-tabs__item) {
    padding: 0 14px;
  }
  .selected-source {
    flex-basis: 100%;
  }
  .import-form {
    grid-template-columns: 1fr;
  }
  .import-actions :deep(.el-form-item__content) {
    justify-content: flex-end;
  }
}
</style>
