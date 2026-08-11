<script lang="ts" setup>
import { onMounted, ref, reactive } from 'vue'
import { knowledgeApi } from '@/api/knowledge'
import { useI18n } from 'vue-i18n'
import { formatTimestamp } from '@/utils/date'

const { t } = useI18n()
const activeTab = ref('triage')

const stagingList = ref<any[]>([])
const suggestions = ref<any[]>([])
const assetList = ref<any[]>([])
const loading = ref(false)

const filters = reactive({ kind: '', trust_tier: '' })

const rejectDialogVisible = ref(false)
const rejectReason = ref('')
const rejectTarget = ref<string | null>(null)

const demoteDialogVisible = ref(false)
const demoteTarget = ref<string | null>(null)
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

async function handleCertify(id: string) {
  await knowledgeApi.certify(id)
  ElMessage.success(t('knowledge.certify') + ' ✓')
  loadTriage()
}

function openReject(id: string) {
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

async function handlePromote(id: string) {
  await knowledgeApi.promote(id)
  ElMessage.success(t('knowledge.promote') + ' ✓')
  loadTriage()
}

function openDemote(id: string) {
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

async function handleDisable(id: string) {
  await knowledgeApi.disable(id)
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
  else loadAssets()
}

onMounted(() => loadTriage())
</script>

<template>
  <div class="knowledge-container">
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane :label="t('knowledge.triage')" name="triage">
        <h4 style="margin: 0 0 12px">{{ t('knowledge.staging_queue') }}</h4>
        <el-table :data="stagingList" v-loading="loading" border size="small">
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
          <el-table-column prop="evidence_count" label="Evidence" width="100" />
          <el-table-column :label="t('knowledge.actions')" width="120">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handlePromote(row.id)">
                {{ t('knowledge.promote') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="t('knowledge.assets')" name="assets">
        <div style="margin-bottom: 12px; display: flex; gap: 12px">
          <el-select v-model="filters.kind" clearable placeholder="Kind" style="width: 150px" @change="loadAssets">
            <el-option label="pattern" value="pattern" />
            <el-option label="rule" value="rule" />
            <el-option label="metric" value="metric" />
          </el-select>
          <el-select v-model="filters.trust_tier" clearable placeholder="Trust Tier" style="width: 150px" @change="loadAssets">
            <el-option label="certified" value="certified" />
            <el-option label="trusted" value="trusted" />
            <el-option label="published" value="published" />
          </el-select>
        </div>
        <el-table :data="assetList" v-loading="loading" border size="small">
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
              <el-button size="small" @click="openDemote(row.id)">
                {{ t('knowledge.demote') }}
              </el-button>
              <el-button type="danger" size="small" @click="handleDisable(row.id)">
                {{ t('knowledge.disable') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Reject Dialog -->
    <el-dialog v-model="rejectDialogVisible" :title="t('knowledge.reject')" width="400px">
      <el-input v-model="rejectReason" type="textarea" :rows="3" :placeholder="t('knowledge.reject_reason')" />
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
</style>
