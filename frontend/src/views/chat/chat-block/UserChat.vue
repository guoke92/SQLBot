<script setup lang="ts">
import type { ChatMessage } from '@/api/chat.ts'
import icon_copy_outlined from '@/assets/embedded/icon_copy_outlined.svg'
import { useI18n } from 'vue-i18n'
import { useClipboard } from '@vueuse/core'

const props = defineProps<{
  message?: ChatMessage
}>()
const { t } = useI18n()
const { copy } = useClipboard({ legacy: true })

const copyCode = () => {
  const str = props.message?.content || ''
  copy(str as string)
    .then(function () {
      ElMessage.success(t('embedded.copy_successful'))
    })
    .catch(function () {
      ElMessage.error(t('embedded.copy_failed'))
    })
}
</script>

<template>
  <div class="question flex-gap-fallback">
    <span style="width: 100%">{{ message?.content }}</span>
    <div style="position: absolute; right: 12px; bottom: -24px">
      <el-tooltip :offset="12" effect="dark" :content="t('datasource.copy')" placement="top">
        <el-icon style="cursor: pointer" size="16" @click="copyCode">
          <icon_copy_outlined></icon_copy_outlined>
        </el-icon>
      </el-tooltip>
    </div>
  </div>
</template>

<style scoped lang="less">
.question {
  display: flex;
  flex-direction: row;
  --gap-size: 8px;
  gap: 8px;
  border-radius: 16px;
  min-height: 48px;
  line-height: 24px;
  font-size: 16px;
  padding: 12px 16px;
  color: rgba(31, 35, 41, 1);
  background: rgba(245, 246, 247, 1);
  position: relative;

  word-wrap: break-word;
  white-space: pre-wrap;
}
</style>
