<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import arrow_down from '@/assets/svg/arrow-down.svg'
import icon_thinking_outlined from '@/assets/svg/icon_thinking_outlined.svg'
import { useReasoningEffortStore, type ReasoningEffortChoice } from '@/stores/reasoningEffort'
import type { ReasoningEffortLevel } from '@/api/chat'

const props = withDefaults(
  defineProps<{
    disabled?: boolean
    chatId?: number
  }>(),
  {
    disabled: false,
    chatId: undefined,
  }
)

const { t } = useI18n()
const store = useReasoningEffortStore()
const visible = ref(false)

onMounted(() => {
  if (!store.loaded) {
    void store.loadCapabilities()
  }
})

watch(
  () => props.chatId,
  (chatId) => {
    store.setActiveChat(chatId)
  },
  { immediate: true }
)

/** Wire: none/low/high/max → UI: 关闭/低/中/高 */
const levels: ReasoningEffortLevel[] = ['none', 'low', 'high', 'max']

const levelLabel = (level: ReasoningEffortLevel | null) => {
  if (level === 'none') return t('qa.reasoning_effort_none')
  if (level === 'low') return t('qa.reasoning_effort_low')
  if (level === 'high') return t('qa.reasoning_effort_mid')
  if (level === 'max') return t('qa.reasoning_effort_high')
  return t('qa.reasoning_effort_unset')
}

const levelHint = (level: ReasoningEffortLevel) => {
  if (level === 'none') return t('qa.reasoning_effort_none_hint')
  if (level === 'low') return t('qa.reasoning_effort_low_hint')
  if (level === 'high') return t('qa.reasoning_effort_mid_hint')
  return t('qa.reasoning_effort_high_hint')
}

const chipLabel = computed(() => {
  const level = store.effectiveEffort
  if (!level) return t('qa.reasoning_effort_unset')
  const base = levelLabel(level)
  if (store.choice == null && store.defaultEffort === level) {
    return `${base} · ${t('qa.reasoning_effort_default')}`
  }
  return base
})

const options = computed(() =>
  levels.map((level) => {
    const isModelDefault = store.defaultEffort === level
    return {
      value: level as ReasoningEffortChoice,
      label: isModelDefault
        ? `${levelLabel(level)}（${t('qa.reasoning_effort_default')}）`
        : levelLabel(level),
      hint: levelHint(level),
      active:
        store.choice === level || (store.choice == null && store.defaultEffort === level),
    }
  })
)

function select(choice: ReasoningEffortChoice) {
  store.setChoice(choice)
  visible.value = false
}
</script>

<template>
  <el-popover
    v-model:visible="visible"
    placement="top-start"
    :width="260"
    trigger="click"
    :disabled="props.disabled"
    popper-class="reasoning-effort-popper"
  >
    <template #reference>
      <button
        type="button"
        class="effort-chip"
        :disabled="props.disabled"
        :title="t('qa.reasoning_effort')"
      >
        <el-icon size="16">
          <icon_thinking_outlined />
        </el-icon>
        <span class="effort-chip__label">{{ chipLabel }}</span>
        <el-icon class="effort-chip__arrow" size="12">
          <arrow_down />
        </el-icon>
      </button>
    </template>
    <div class="effort-menu">
      <div class="effort-menu__title">{{ t('qa.reasoning_effort') }}</div>
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        class="effort-option"
        :class="{ 'is-active': option.active }"
        @click="select(option.value)"
      >
        <div class="effort-option__label">{{ option.label }}</div>
        <div class="effort-option__hint">{{ option.hint }}</div>
      </button>
    </div>
  </el-popover>
</template>

<style scoped lang="less">
.effort-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 168px;
  height: 28px;
  padding: 0 8px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: rgba(100, 106, 115, 1);
  font-size: 13px;
  line-height: 22px;
  cursor: pointer;

  &:hover:not(:disabled) {
    background: rgba(31, 35, 41, 0.08);
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.55;
  }
}

.effort-chip__label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.effort-chip__arrow {
  flex-shrink: 0;
}
</style>

<style lang="less">
.reasoning-effort-popper {
  padding: 8px !important;

  .effort-menu__title {
    padding: 4px 8px 8px;
    font-size: 12px;
    line-height: 18px;
    color: rgba(100, 106, 115, 1);
  }

  .effort-option {
    display: block;
    width: 100%;
    padding: 8px;
    border: none;
    border-radius: 8px;
    background: transparent;
    text-align: left;
    cursor: pointer;

    &:hover,
    &.is-active {
      background: rgba(31, 35, 41, 0.06);
    }
  }

  .effort-option__label {
    font-size: 14px;
    line-height: 22px;
    color: rgba(31, 35, 41, 1);
  }

  .effort-option.is-active .effort-option__label {
    font-weight: 500;
  }

  .effort-option__hint {
    margin-top: 2px;
    font-size: 12px;
    line-height: 18px;
    color: rgba(100, 106, 115, 1);
  }
}
</style>
