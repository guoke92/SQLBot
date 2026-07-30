<script lang="ts" setup>
import { computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import type { DictionaryFieldConfig } from '@/api/dictionary'

const props = defineProps<{
  config: DictionaryFieldConfig
  busy?: boolean
}>()
const emit = defineEmits<{
  toggle: [value: boolean]
  refresh: []
}>()
const { t } = useI18n()
const enabled = computed(() => props.config.enabled)

const statusType = computed(() => {
  if (props.config?.last_error) return 'danger'
  if (props.config?.status === 'READY') return 'success'
  if (props.config?.status === 'STALE') return 'warning'
  return 'info'
})

const toggle = (value: string | number | boolean) => {
  emit('toggle', Boolean(value))
}

const refresh = () => {
  emit('refresh')
}
</script>

<template>
  <div class="dictionary-control">
    <el-switch :model-value="enabled" :loading="busy" size="small" @change="toggle" />
    <template v-if="config.configured">
      <el-tooltip v-if="config.last_error" :content="config.last_error" placement="top">
        <el-tag :type="statusType" size="small">
          {{ t(`datasource.dictionary.status.${config.status.toLowerCase()}`) }}
        </el-tag>
      </el-tooltip>
      <el-tag v-else :type="statusType" size="small">
        {{ t(`datasource.dictionary.status.${config.status.toLowerCase()}`) }}
      </el-tag>
      <span v-if="config.status === 'READY'" class="value-count">
        {{ t('datasource.dictionary.value_count', { count: config.value_count }) }}
      </span>
      <el-button
        v-if="config.enabled"
        text
        :icon="Refresh"
        :loading="busy"
        :title="t('datasource.dictionary.refresh')"
        @click="refresh"
      />
    </template>
  </div>
</template>

<style scoped>
.dictionary-control {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 24px;
}

.value-count {
  color: #646a73;
  white-space: nowrap;
}
</style>
