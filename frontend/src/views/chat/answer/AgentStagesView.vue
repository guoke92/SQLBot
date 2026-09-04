<script setup lang="ts">
import { computed, ref } from 'vue'
import MdComponent from '@/views/chat/component/MdComponent.vue'
import SQLComponent from '@/views/chat/component/SQLComponent.vue'
import icon_up_outlined from '@/assets/svg/icon_up_outlined.svg'
import icon_down_outlined from '@/assets/svg/icon_down_outlined.svg'
import gou_icon from '@/assets/svg/gou_icon.svg'
import icon_error from '@/assets/svg/icon_error.svg'

export interface AgentStageItem {
  id: string
  type: 'thought' | 'tool'
  title: string
  content?: string
  status: 'running' | 'completed' | 'failed'
  toolName?: string
  toolArgs?: Record<string, any>
  sql?: string
  duration?: number
}

const props = withDefaults(
  defineProps<{
    stages: AgentStageItem[]
    isTyping?: boolean
  }>(),
  {
    stages: () => [],
    isTyping: false,
  }
)

// Track which stage cards are expanded.
const expandedStageIds = ref<Record<string, boolean>>({})

function toggleStage(id: string) {
  expandedStageIds.value[id] = !expandedStageIds.value[id]
}

function isExpanded(id: string, isLast: boolean): boolean {
  if (expandedStageIds.value[id] !== undefined) {
    return expandedStageIds.value[id]
  }
  if (props.isTyping && isLast) {
    return true
  }
  return true
}

const hasStages = computed(() => props.stages.length > 0)
</script>

<template>
  <div v-if="hasStages" class="agent-stages-view">
    <div
      v-for="(stage, idx) in stages"
      :key="stage.id || `stage-${idx}`"
      class="agent-stage-card"
      :class="[`type-${stage.type}`, `status-${stage.status}`]"
    >
      <div
        class="stage-header"
        @click="toggleStage(stage.id || `stage-${idx}`)"
      >
        <div class="stage-header-left">
          <span class="stage-icon">
            <el-icon v-if="stage.status === 'running'" class="is-loading">
              <Loading />
            </el-icon>
            <el-icon v-else-if="stage.status === 'failed'" class="status-error">
              <icon_error />
            </el-icon>
            <el-icon v-else class="status-success">
              <gou_icon />
            </el-icon>
          </span>
          <span class="stage-title">{{ stage.title }}</span>
          <span v-if="stage.duration" class="stage-duration">{{ stage.duration }}s</span>
        </div>
        <div class="stage-header-right">
          <el-icon class="toggle-icon">
            <icon_up_outlined v-if="isExpanded(stage.id || `stage-${idx}`, idx === stages.length - 1)" />
            <icon_down_outlined v-else />
          </el-icon>
        </div>
      </div>

      <div
        v-show="isExpanded(stage.id || `stage-${idx}`, idx === stages.length - 1)"
        class="stage-body"
      >
        <div v-if="stage.content" class="stage-content">
          <MdComponent :message="stage.content" />
        </div>
        <div v-if="stage.sql" class="stage-sql">
          <SQLComponent :sql="stage.sql" />
        </div>
        <div v-if="stage.toolArgs && Object.keys(stage.toolArgs).length > 0 && !stage.sql" class="stage-args">
          <pre class="stage-json">{{ JSON.stringify(stage.toolArgs, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.agent-stages-view {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.agent-stage-card {
  border: 1px solid #dee0e3;
  border-radius: 8px;
  background: #fcfcfd;
  overflow: hidden;
  transition: all 0.2s ease;

  &:hover {
    border-color: #c9cdd4;
  }

  &.type-thought {
    border-left: 3px solid #3370ff;
  }

  &.type-tool {
    border-left: 3px solid #00b42a;
  }

  &.status-failed {
    border-left-color: #f53f3f;
  }
}

.stage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  cursor: pointer;
  user-select: none;
  background: #f7f8fa;

  &:hover {
    background: #f2f3f5;
  }
}

.stage-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stage-icon {
  display: flex;
  align-items: center;
  font-size: 14px;

  .status-success {
    color: #00b42a;
  }
  .status-error {
    color: #f53f3f;
  }
}

.stage-title {
  font-size: 13px;
  font-weight: 500;
  color: #1f2329;
}

.stage-duration {
  font-size: 12px;
  color: #8f959e;
}

.stage-header-right {
  display: flex;
  align-items: center;
  color: #8f959e;
  font-size: 12px;
}

.stage-body {
  padding: 10px 14px;
  border-top: 1px solid #edf0f3;
  background: #ffffff;
  font-size: 13px;
  line-height: 20px;
  color: #646a73;
}

.stage-content {
  color: #4e5969;
}

.stage-sql {
  margin-top: 6px;
}

.stage-json {
  margin: 0;
  padding: 8px;
  border-radius: 4px;
  background: #f7f8fa;
  font-family: monospace;
  font-size: 12px;
  color: #1f2329;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}
</style>
