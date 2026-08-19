<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import {
  knowledgeApi,
  type DatasourceBindingCandidate,
  type KnowledgePackageDetail,
  type KnowledgePackageSummary,
  type KnowledgePackageUnitSummary,
} from '@/api/knowledge'
import {
  documentsFromDataTransfer,
  documentsFromFileList,
} from '@/api/knowledgePackageDocuments'
import { statusLabel, statusTagType } from '../presentation'
import KnowledgeUnitDrawer from './KnowledgeUnitDrawer.vue'
import ValidationIssueList from './ValidationIssueList.vue'
import IconOpeDelete from '@/assets/svg/icon_delete.svg'
import IconInfo from '@/assets/svg/icon_info_outlined_1.svg'

const loading = ref(false)
const importLoading = ref(false)
const packages = ref<KnowledgePackageSummary[]>([])
const selectedId = ref('')
const selectedRevision = ref<number>()
const detail = ref<KnowledgePackageDetail | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const folderInput = ref<HTMLInputElement | null>(null)
const candidates = ref<DatasourceBindingCandidate[]>([])
const datasourceId = ref<number>()
const dropActive = ref(false)
const packagePage = ref(1)
const packagePageSize = 10
const packageTotal = ref(0)
const selectedUnit = ref<KnowledgePackageUnitSummary | null>(null)
const unitDrawerVisible = ref(false)
const groupedUnits = computed(() =>
  [...(detail.value?.units || [])].sort(
    (left, right) =>
      left.domain.localeCompare(right.domain, 'zh-CN') ||
      left.title.localeCompare(right.title, 'zh-CN')
  )
)
const validationErrorTotal = computed(() =>
  groupedUnits.value.reduce((sum, item) => sum + (item.validation_error_count || 0), 0)
)
const validationWarningTotal = computed(() =>
  groupedUnits.value.reduce((sum, item) => sum + (item.validation_warning_count || 0), 0)
)
const issueUnits = computed(() =>
  groupedUnits.value.filter(
    (item) =>
      (item.validation_error_count || 0) > 0 ||
      (item.validation_warning_count || 0) > 0 ||
      item.validation_status === 'FAIL' ||
      item.validation_status === 'WARNING'
  )
)
const hasBoundUnit = computed(() =>
  groupedUnits.value.some((item) => item.binding_status && item.binding_status !== 'UNBOUND')
)
const packageStatus = computed(() => detail.value?.package.status || '')
const canSubmitReview = computed(() =>
  groupedUnits.value.some((item) => item.lifecycle_status === 'DRAFT')
)
const canPublishPackage = computed(
  () =>
    groupedUnits.value.length > 0 &&
    groupedUnits.value.every(
      (item) => item.lifecycle_status === 'APPROVED' || item.lifecycle_status === 'PUBLISHED'
    ) &&
    groupedUnits.value.some((item) => item.lifecycle_status === 'APPROVED')
)
const canUnpublishPackage = computed(() =>
  groupedUnits.value.some((item) => item.lifecycle_status === 'PUBLISHED')
)
const canRepublishPackage = computed(
  () =>
    groupedUnits.value.length > 0 &&
    groupedUnits.value.every((item) =>
      ['APPROVED', 'PUBLISHED', 'RETIRED'].includes(item.lifecycle_status)
    ) &&
    groupedUnits.value.some((item) => item.lifecycle_status === 'RETIRED')
)
const selectedCandidate = computed(() =>
  candidates.value.find((item) => item.datasource_id === datasourceId.value)
)

function errorCount(row: KnowledgePackageUnitSummary) {
  return row.validation_error_count || 0
}

function warningCount(row: KnowledgePackageUnitSummary) {
  return row.validation_warning_count || 0
}

async function loadPackages(selectFirst = false) {
  loading.value = true
  try {
    const result = (await knowledgeApi.getPackages({
      page: packagePage.value,
      page_size: packagePageSize,
    })) as {
      items: KnowledgePackageSummary[]
      total: number
    }
    packages.value = result.items
    packageTotal.value = result.total
    if (selectFirst || !selectedId.value || !selectedRevision.value) {
      if (result.items.length) {
        selectedId.value = result.items[0].package_id
        selectedRevision.value = result.items[0].revision
      } else {
        selectedId.value = ''
        selectedRevision.value = undefined
        detail.value = null
        candidates.value = []
      }
    }
    if (selectedId.value && selectedRevision.value)
      await selectPackage(selectedId.value, selectedRevision.value)
  } finally {
    loading.value = false
  }
}

async function selectPackage(id: string, revision: number) {
  selectedId.value = id
  selectedRevision.value = revision
  const [packageDetail, bindingCandidates] = await Promise.all([
    knowledgeApi.getPackage(id, revision),
    knowledgeApi.getBindingCandidates(id, revision),
  ])
  detail.value = packageDetail as KnowledgePackageDetail
  candidates.value = (bindingCandidates as { items: DatasourceBindingCandidate[] }).items
  const boundId = detail.value.units.find((item) => item.datasource_id)?.datasource_id
  datasourceId.value =
    boundId ||
    candidates.value.find((item) => item.coverage === 1)?.datasource_id ||
    datasourceId.value
}

function onPickerInput(event: Event) {
  const input = event.target as HTMLInputElement
  const picked = documentsFromFileList(input.files)
  input.value = ''
  void importPackage(picked)
}

function openPicker(kind: string | number) {
  if (kind === 'folder') folderInput.value?.click()
  else fileInput.value?.click()
}

async function onDrop(event: DragEvent) {
  dropActive.value = false
  void importPackage(await documentsFromDataTransfer(event.dataTransfer))
}

async function importPackage(values: File[]) {
  if (!values.length) return
  importLoading.value = true
  try {
    const result = (await knowledgeApi.importFiles(values)) as {
      package: KnowledgePackageSummary
    }
    ElMessage.success('知识包已登记，请绑定数据源')
    selectedId.value = result.package.package_id
    selectedRevision.value = result.package.revision
    await loadPackages()
  } finally {
    importLoading.value = false
  }
}

async function bind() {
  if (!selectedId.value || !selectedRevision.value || !datasourceId.value) return
  loading.value = true
  try {
    const result = (await knowledgeApi.bindPackage(
      selectedId.value,
      selectedRevision.value,
      datasourceId.value
    )) as {
      status: string
      package_issue?: { missing_datasets?: string[] }
    }
    await selectPackage(selectedId.value, selectedRevision.value)
    if (result.package_issue?.missing_datasets?.length) {
      ElMessage.warning(`数据源缺少：${result.package_issue.missing_datasets.join('、')}`)
    } else if (validationErrorTotal.value > 0) {
      ElMessage.warning(
        `已绑定，仍有 ${validationErrorTotal.value} 个失败、${validationWarningTotal.value} 个告警`
      )
    } else if (validationWarningTotal.value > 0) {
      ElMessage.warning(`已绑定，存在 ${validationWarningTotal.value} 个告警`)
    } else ElMessage.success('已绑定并完成校验')
  } finally {
    loading.value = false
  }
}

async function revalidatePackage() {
  if (!selectedId.value || !selectedRevision.value) return
  loading.value = true
  try {
    const result = (await knowledgeApi.validatePackage(
      selectedId.value,
      selectedRevision.value
    )) as { skipped_unbound?: number[] }
    await selectPackage(selectedId.value, selectedRevision.value)
    if (result.skipped_unbound?.length)
      ElMessage.warning('部分知识单元尚未绑定数据源，已跳过')
    else if (validationErrorTotal.value > 0)
      ElMessage.warning(
        `重新校验完成：失败 ${validationErrorTotal.value} · 告警 ${validationWarningTotal.value}`
      )
    else if (validationWarningTotal.value > 0)
      ElMessage.warning(`重新校验完成，存在 ${validationWarningTotal.value} 个告警`)
    else ElMessage.success('已按当前绑定重新校验')
  } finally {
    loading.value = false
  }
}

async function changePackagePage(page: number) {
  packagePage.value = page
  selectedId.value = ''
  selectedRevision.value = undefined
  await loadPackages(true)
}

function openUnit(row: KnowledgePackageUnitSummary) {
  selectedUnit.value = row
  unitDrawerVisible.value = true
}

async function refreshCurrent() {
  await loadPackages()
}

async function submitPackageReview() {
  if (!selectedId.value || !selectedRevision.value) return
  loading.value = true
  try {
    const result = (await knowledgeApi.submitPackageReview(
      selectedId.value,
      selectedRevision.value
    )) as { submitted_units?: string[] }
    await loadPackages()
    const count = result.submitted_units?.length || 0
    ElMessage.success(count ? `已提交 ${count} 个知识单元审核` : '当前知识包已在审核中')
  } finally {
    loading.value = false
  }
}

async function publishCurrentPackage(republish = false) {
  if (!selectedId.value || !selectedRevision.value) return
  loading.value = true
  try {
    await knowledgeApi.publishPackage(selectedId.value, selectedRevision.value)
    await loadPackages()
    ElMessage.success(republish ? '知识包已重新发布' : '知识包已发布')
  } finally {
    loading.value = false
  }
}

async function unpublishCurrentPackage() {
  if (!selectedId.value || !selectedRevision.value) return
  try {
    await ElMessageBox.confirm(
      '撤销发布后，这些知识单元将不再被问数召回。知识包、绑定和内容会保留，可以重新发布。',
      '撤销发布知识包',
      { type: 'warning', confirmButtonText: '撤销发布', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  loading.value = true
  try {
    await knowledgeApi.unpublishPackage(selectedId.value, selectedRevision.value)
    await loadPackages()
    ElMessage.success('知识包已撤销发布')
  } finally {
    loading.value = false
  }
}

async function deletePackageItem(item: KnowledgePackageSummary) {
  try {
    await ElMessageBox.confirm(
      `删除「${item.title}」后，知识包及其知识单元将从系统中删除，且无法恢复。`,
      '删除知识包',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  loading.value = true
  try {
    await knowledgeApi.deletePackage(item.package_id, item.revision)
    ElMessage.success('知识包已删除')
    if (item.package_id === selectedId.value && item.revision === selectedRevision.value) {
      selectedId.value = ''
      selectedRevision.value = undefined
      await loadPackages(true)
    } else {
      await loadPackages()
    }
  } finally {
    loading.value = false
  }
}

async function deleteUnit(row: KnowledgePackageUnitSummary) {
  try {
    await ElMessageBox.confirm(
      `删除「${row.title}」将删除该知识单元的全部版本，且无法恢复。`,
      '删除知识单元',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  loading.value = true
  try {
    await knowledgeApi.deleteUnit(row.unit_id)
    ElMessage.success('知识单元已删除')
    await refreshCurrent()
  } finally {
    loading.value = false
  }
}

onMounted(() => loadPackages(true))
</script>

<template>
  <section v-loading="loading" class="package-page">
    <div
      class="import-panel"
      :class="{ active: dropActive }"
      @dragover.prevent="dropActive = true"
      @dragleave.prevent="dropActive = false"
      @drop.prevent="onDrop"
    >
      <div>
        <h3>导入知识包</h3>
        <p>选择或拖入文件、目录或 ZIP，系统会自动识别并登记。</p>
      </div>
      <input
        ref="fileInput"
        hidden
        type="file"
        multiple
        accept=".yaml,.yml,.json,.jsonl,.zip"
        @change="onPickerInput"
      />
      <input
        ref="folderInput"
        hidden
        type="file"
        multiple
        directory
        webkitdirectory
        @change="onPickerInput"
      />
      <el-dropdown trigger="click" :disabled="importLoading" @command="openPicker">
        <el-button type="primary" :loading="importLoading">选择知识包</el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="files">选择文件/ZIP</el-dropdown-item>
            <el-dropdown-item command="folder">选择文件夹</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <div class="workbench">
      <aside class="package-list">
        <div class="list-heading">
          <strong>已登记知识包</strong><el-tag>{{ packages.length }}</el-tag>
        </div>
        <button
          v-for="item in packages"
          :key="`${item.package_id}:${item.revision}`"
          type="button"
          :class="{
            active: item.package_id === selectedId && item.revision === selectedRevision,
          }"
          @click="selectPackage(item.package_id, item.revision)"
        >
          <div class="card-head">
            <el-tag size="small" :type="statusTagType(item.status)">{{
              statusLabel(item.status)
            }}</el-tag>
            <el-tooltip content="删除知识包" placement="top">
              <el-icon class="card-delete" @click.stop="deletePackageItem(item)">
                <IconOpeDelete />
              </el-icon>
            </el-tooltip>
          </div>
          <strong>{{ item.title }}</strong>
          <span>{{ item.unit_count }} 个知识单元 · Rev {{ item.revision }}</span>
        </button>
        <el-empty v-if="!packages.length" description="暂无知识包" :image-size="64" />
        <el-pagination
          v-if="packageTotal > packagePageSize"
          class="package-pagination"
          small
          layout="prev, pager, next"
          :current-page="packagePage"
          :page-size="packagePageSize"
          :total="packageTotal"
          @current-change="changePackagePage"
        />
      </aside>

      <main v-if="detail" class="package-detail">
        <header>
          <div>
            <h2>{{ detail.package.title }}</h2>
            <p>{{ detail.package.description }}</p>
          </div>
        </header>
        <div class="package-meta">
          <span>Schema {{ detail.package.schema_version }}</span>
          <span>{{ detail.sources.length }} 个来源</span>
          <span>{{ detail.evidence_count }} 条证据</span>
          <span>{{ detail.units.length }} 个知识单元</span>
        </div>

        <section class="binding-panel">
          <div>
            <strong>数据源</strong>
            <p>
              分数表示该数据源目录能匹配到知识包声明的几张表，例如 4/4 表示 4 张声明表全部存在。绑定后会自动校验。
            </p>
          </div>
          <el-select v-model="datasourceId" placeholder="选择目标数据源" filterable>
            <el-option
              v-for="candidate in candidates"
              :key="candidate.datasource_id"
              :value="candidate.datasource_id"
              :label="`${candidate.datasource_name} · ${candidate.matched_count}/${candidate.required_count} 张表`"
            />
          </el-select>
          <div class="binding-actions">
            <el-button type="primary" :disabled="!datasourceId" :loading="loading" @click="bind">
              {{ hasBoundUnit ? '更换并绑定' : '绑定数据源' }}
            </el-button>
            <el-button :disabled="!hasBoundUnit" :loading="loading" @click="revalidatePackage">
              重新校验
            </el-button>
            <el-button
              v-if="canSubmitReview"
              type="success"
              :disabled="!groupedUnits.length"
              :loading="loading"
              @click="submitPackageReview"
            >
              提交审核
            </el-button>
            <el-tag v-else-if="packageStatus === 'IN_REVIEW'" type="warning">审核中</el-tag>
            <el-button
              v-if="canPublishPackage"
              type="success"
              :loading="loading"
              @click="publishCurrentPackage(false)"
            >
              发布知识包
            </el-button>
            <el-button
              v-if="canRepublishPackage"
              type="success"
              :loading="loading"
              @click="publishCurrentPackage(true)"
            >
              重新发布
            </el-button>
            <el-button
              v-if="canUnpublishPackage"
              :loading="loading"
              @click="unpublishCurrentPackage"
            >
              撤销发布
            </el-button>
            <el-tag v-if="packageStatus === 'PUBLISHED'" type="success">已发布</el-tag>
            <el-tag v-else-if="packageStatus === 'RETIRED'">已退役</el-tag>
          </div>
        </section>
        <el-alert
          v-if="selectedCandidate && selectedCandidate.coverage < 1"
          class="issue-banner"
          type="warning"
          :closable="false"
          :title="`当前数据源可能缺少：${selectedCandidate.missing.join('、') || '部分表'}`"
        />
        <section v-if="issueUnits.length" class="issue-panel">
          <h3>
            校验问题（失败 {{ validationErrorTotal }} · 告警 {{ validationWarningTotal }}）
          </h3>
          <article v-for="unit in issueUnits" :key="unit.unit_id">
            <div class="issue-heading">
              <strong>{{ unit.title }}</strong>
              <el-tag v-if="errorCount(unit)" size="small" type="danger">
                失败 {{ errorCount(unit) }}
              </el-tag>
              <el-tag v-if="warningCount(unit)" size="small" type="warning">
                告警 {{ warningCount(unit) }}
              </el-tag>
              <el-tag
                v-if="!errorCount(unit) && !warningCount(unit)"
                size="small"
                :type="statusTagType(unit.validation_status)"
              >
                {{ statusLabel(unit.validation_status) }}
              </el-tag>
              <el-button link type="primary" @click="openUnit(unit)">查看单元</el-button>
            </div>
            <ValidationIssueList
              compact
              :status="unit.validation_status"
              :summary="unit.validation_summary_text"
              :issues="unit.validation_issues"
            />
          </article>
        </section>

        <el-table :data="groupedUnits">
          <el-table-column label="知识单元" min-width="280">
            <template #default="{ row }"
              ><strong>{{ row.title }}</strong>
              <div class="subtle">{{ row.domain }} · {{ row.unit_key }}</div></template
            >
          </el-table-column>
          <el-table-column label="Revision" width="90" prop="revision" />
          <el-table-column label="生命周期" width="110">
            <template #default="{ row }">{{ statusLabel(row.lifecycle_status) }}</template>
          </el-table-column>
          <el-table-column label="校验" min-width="220">
            <template #default="{ row }">
              <el-popover
                v-if="errorCount(row) || warningCount(row) || row.validation_issue_count"
                placement="left"
                :width="420"
                trigger="hover"
              >
                <ValidationIssueList
                  compact
                  :status="row.validation_status"
                  :summary="row.validation_summary_text"
                  :issues="row.validation_issues"
                />
                <template #reference>
                  <div class="validation-tags">
                    <el-tag v-if="errorCount(row)" type="danger">失败 {{ errorCount(row) }}</el-tag>
                    <el-tag v-if="warningCount(row)" type="warning">
                      告警 {{ warningCount(row) }}
                    </el-tag>
                    <el-tag
                      v-if="!errorCount(row) && !warningCount(row)"
                      :type="statusTagType(row.validation_status)"
                    >
                      {{ statusLabel(row.validation_status) }}
                    </el-tag>
                  </div>
                </template>
              </el-popover>
              <el-tag v-else :type="statusTagType(row.validation_status)">{{
                statusLabel(row.validation_status)
              }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="88" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <el-tooltip content="详情" placement="top">
                  <el-icon class="action-icon" @click="openUnit(row)">
                    <IconInfo />
                  </el-icon>
                </el-tooltip>
                <el-tooltip content="删除知识单元" placement="top">
                  <el-icon class="action-icon danger" @click="deleteUnit(row)">
                    <IconOpeDelete />
                  </el-icon>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </main>
      <el-empty v-else class="package-detail" description="请选择知识包" />
    </div>

    <KnowledgeUnitDrawer
      v-model="unitDrawerVisible"
      mode="package"
      :item="selectedUnit"
      @changed="refreshCurrent"
    />
  </section>
</template>

<style scoped>
.package-page {
  display: grid;
  gap: 14px;
}
.import-panel {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) auto;
  padding: 16px;
  align-items: center;
  gap: 10px;
  border: 1px dashed var(--el-border-color);
  border-radius: 10px;
  background: var(--el-fill-color-extra-light);
}
.import-panel.active {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.import-panel h3 {
  margin: 0;
}
.import-panel p {
  margin: 5px 0 0;
  color: var(--el-text-color-secondary);
}
.workbench {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  min-height: 520px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  overflow: hidden;
}
.package-list {
  padding: 12px;
  background: var(--el-fill-color-extra-light);
  border-right: 1px solid var(--el-border-color-lighter);
}
.list-heading {
  display: flex;
  margin-bottom: 10px;
  align-items: center;
  justify-content: space-between;
}
.package-list button {
  display: grid;
  width: 100%;
  padding: 11px;
  margin-bottom: 6px;
  text-align: left;
  gap: 5px;
  cursor: pointer;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 7px;
}
.package-list button:hover,
.package-list button.active {
  background: var(--el-bg-color);
  border-color: var(--el-color-primary-light-7);
}
.card-head,
.row-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.row-actions {
  justify-content: center;
}
.card-delete,
.action-icon {
  color: var(--el-text-color-secondary);
  cursor: pointer;
}
.action-icon:hover {
  color: var(--el-color-primary);
}
.action-icon.danger:hover,
.card-delete:hover {
  color: var(--el-color-danger);
}
.package-pagination {
  margin-top: 10px;
  justify-content: center;
}
.package-list span,
.package-list small,
.subtle {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.package-detail {
  padding: 18px;
  min-width: 0;
}
.package-detail header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.validation-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.package-detail h2 {
  margin: 0;
}
.package-detail header p {
  margin: 7px 0;
  color: var(--el-text-color-secondary);
}
.package-meta {
  display: flex;
  margin: 14px 0;
  gap: 8px;
  flex-wrap: wrap;
}
.package-meta span {
  padding: 6px 10px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  font-size: 12px;
}
.binding-panel {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) 280px auto;
  padding: 13px;
  margin-bottom: 14px;
  align-items: center;
  gap: 12px;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
}
.binding-actions {
  display: flex;
  gap: 8px;
}
.issue-banner {
  margin-bottom: 12px;
}
.issue-panel {
  display: grid;
  gap: 12px;
  margin-bottom: 14px;
  padding: 12px;
  border: 1px solid var(--el-color-warning-light-7);
  border-radius: 8px;
  background: var(--el-color-warning-light-9);
}
.issue-panel h3 {
  margin: 0;
  font-size: 14px;
}
.issue-heading {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
}
.binding-panel p {
  margin: 5px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
@media (max-width: 900px) {
  .import-panel {
    grid-template-columns: 1fr auto;
  }
  .import-panel > div {
    grid-column: 1/-1;
  }
  .workbench {
    grid-template-columns: 1fr;
  }
  .package-list {
    border-right: 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }
  .binding-panel {
    grid-template-columns: 1fr;
  }
}
</style>
