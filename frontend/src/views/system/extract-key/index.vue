<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { extractKeyApi, type ExtractKeyInfo } from '@/api/dev'

const { t } = useI18n()
const loading = ref(false)
const info = ref<ExtractKeyInfo | null>(null)
const plaintext = ref('')

const load = async () => {
  loading.value = true
  try {
    info.value = (await extractKeyApi.get()) || null
  } catch {
    info.value = null
  } finally {
    loading.value = false
  }
}

const rotate = async () => {
  loading.value = true
  try {
    const created = await extractKeyApi.rotate()
    info.value = created
    plaintext.value = created.key || ''
  } finally {
    loading.value = false
  }
}

const revoke = async () => {
  loading.value = true
  try {
    await extractKeyApi.revoke()
    info.value = null
    plaintext.value = ''
  } finally {
    loading.value = false
  }
}

const copyKey = async () => {
  if (!plaintext.value) return
  await navigator.clipboard.writeText(plaintext.value)
}

onMounted(load)
</script>

<template>
  <div class="extract-key-page" v-loading="loading">
    <div class="title">{{ t('extract_key.title') }}</div>
    <p class="hint">{{ t('extract_key.hint') }}</p>
    <div v-if="info?.key_prefix" class="meta">
      {{ t('extract_key.prefix') }}: <code>{{ info.key_prefix }}…</code>
      <span v-if="info.created_at"> · {{ info.created_at }}</span>
    </div>
    <div v-else class="meta">{{ t('extract_key.none') }}</div>
    <el-alert
      v-if="plaintext"
      type="warning"
      :closable="false"
      class="plain-alert"
      :title="t('extract_key.show_once')"
    >
      <div class="plain-row">
        <code class="plain">{{ plaintext }}</code>
        <el-button size="small" @click="copyKey">{{ t('extract_key.copy') }}</el-button>
      </div>
    </el-alert>
    <div class="actions">
      <el-button type="primary" @click="rotate">{{ t('extract_key.rotate') }}</el-button>
      <el-button v-if="info?.key_prefix" @click="revoke">{{ t('extract_key.revoke') }}</el-button>
    </div>
    <pre class="sample">{{ t('extract_key.curl_hint') }}</pre>
  </div>
</template>

<style lang="less" scoped>
.extract-key-page {
  padding: 24px;
  max-width: 760px;
}
.title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}
.hint,
.meta {
  color: #646a73;
  font-size: 13px;
  line-height: 22px;
  margin-bottom: 12px;
}
.plain-alert {
  margin-bottom: 16px;
}
.plain-row {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.plain {
  word-break: break-all;
}
.actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.sample {
  background: #f5f6f7;
  padding: 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  font-size: 12px;
  color: #1f2329;
}
</style>
