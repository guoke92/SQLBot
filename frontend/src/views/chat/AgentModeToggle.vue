<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

export type AgentModeId = 'query' | 'analyze'

const props = withDefaults(
  defineProps<{
    modelValue?: AgentModeId
    disabled?: boolean
  }>(),
  {
    modelValue: 'query',
    disabled: false,
  }
)

const emit = defineEmits<{
  'update:modelValue': [AgentModeId]
}>()

const { t } = useI18n()

const current = computed(() => (props.modelValue === 'analyze' ? 'analyze' : 'query'))

const options: { id: AgentModeId; label: string; hint: string }[] = [
  {
    id: 'query',
    label: t('qa.agent_mode_query'),
    hint: t('qa.agent_mode_query_hint'),
  },
  {
    id: 'analyze',
    label: t('qa.agent_mode_analyze'),
    hint: t('qa.agent_mode_analyze_hint'),
  },
]

function select(id: AgentModeId) {
  if (props.disabled || id === current.value) return
  emit('update:modelValue', id)
}
</script>

<template>
  <div class="agent-mode-toggle" role="group" :aria-label="t('qa.agent_mode')">
    <button
      v-for="option in options"
      :key="option.id"
      type="button"
      class="mode-chip"
      :class="{ 'is-active': current === option.id }"
      :disabled="props.disabled"
      :title="option.hint"
      @click="select(option.id)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<style scoped lang="less">
.agent-mode-toggle {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  height: 28px;
  padding: 2px;
  border-radius: 8px;
  background: rgba(31, 35, 41, 0.06);
}

.mode-chip {
  height: 24px;
  padding: 0 8px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: rgba(100, 106, 115, 1);
  font-size: 13px;
  line-height: 22px;
  cursor: pointer;

  &:hover:not(:disabled):not(.is-active) {
    color: rgba(31, 35, 41, 1);
  }

  &.is-active {
    background: #fff;
    color: rgba(31, 35, 41, 1);
    font-weight: 500;
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.55;
  }
}
</style>
