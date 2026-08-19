<script lang="ts" setup>
import { computed } from 'vue'
import { issueHeading, issueMessage, issueSeverity } from '../presentation'

const props = defineProps<{
  status?: string | null
  summary?: string
  issues?: Array<Record<string, unknown>>
  compact?: boolean
}>()

const alertType = computed(() => {
  if (props.status === 'FAIL' || props.status === 'ERROR')
    return 'error'
  if (props.status === 'WARNING' || props.status === 'STALE') return 'warning'
  if (props.status === 'PASS') return 'success'
  return 'info'
})
const visibleIssues = computed(() => props.issues || [])
</script>

<template>
  <div v-if="status || summary || visibleIssues.length" class="issue-block">
    <el-alert
      v-if="!compact && (summary || status)"
      :title="summary || '校验结果'"
      :type="alertType"
      :closable="false"
      show-icon
    />
    <ul v-if="visibleIssues.length" :class="{ compact }">
      <li v-for="(issue, index) in visibleIssues" :key="`${issue.code}:${index}`">
        <el-tag size="small" :type="issueSeverity(issue)">
          {{ issue.severity === 'warning' ? '警告' : '失败' }}
        </el-tag>
        <div class="issue-copy">
          <strong>{{ issueHeading(issue) }}</strong>
          <span v-if="issueMessage(issue)">{{ issueMessage(issue) }}</span>
        </div>
      </li>
    </ul>
    <p v-else-if="!compact" class="empty">没有更细的校验条目</p>
  </div>
</template>

<style scoped>
.issue-block {
  display: grid;
  gap: 8px;
}
ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}
li {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  line-height: 1.5;
}
.issue-copy {
  display: grid;
  gap: 2px;
  min-width: 0;
}
.issue-copy span {
  color: var(--el-text-color-secondary);
  word-break: break-word;
}
.compact li {
  font-size: 12px;
}
.empty {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
