<script setup lang="ts">
import type { ResultQuality } from '@/api/chat'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  quality: ResultQuality
}>()

const { t } = useI18n()
const label = computed(() => t(`chat.quality_grade.${props.quality.grade}`))
const coverage = computed(() =>
  t(
    props.quality.coverage.truncated
      ? 'chat.quality_coverage_truncated'
      : 'chat.quality_coverage_returned',
    {
      rows: props.quality.coverage.returned_rows,
      steps: props.quality.coverage.step_count,
    }
  )
)

const detailText = (code: string, params: Record<string, any>) =>
  t(`chat.quality_detail.${code}`, params)

const observationText = (code: string, params: Record<string, any>) =>
  t(`chat.data_observation.${code}`, params)
</script>

<template>
  <el-popover placement="bottom-end" :width="440" trigger="click">
    <template #reference>
      <button
        type="button"
        class="quality-stamp"
        :class="`quality-stamp--${quality.grade}`"
        :aria-label="`${label} ${quality.score}`"
      >
        <span class="quality-stamp__label">{{ label }}</span>
        <span class="quality-stamp__score">{{ quality.score }} {{ t('chat.quality_points') }}</span>
      </button>
    </template>

    <div class="quality-detail">
      <div class="quality-detail__title">
        {{ t('chat.quality_score') }}：{{ quality.score }} / 100
      </div>
      <div class="quality-detail__coverage">{{ coverage }}</div>

      <div class="quality-detail__section">{{ t('chat.quality_dimensions') }}</div>
      <div
        v-for="dimension in quality.dimensions"
        :key="dimension.code"
        class="quality-detail__dimension"
      >
        <div class="quality-detail__dimension-heading">
          <span>{{ t(`chat.quality_dimension.${dimension.code}`) }}</span>
          <span class="quality-detail__dimension-score">
            {{ dimension.score }}/100 ·
            {{ t('chat.quality_weight', { weight: dimension.weight }) }} ·
            {{ dimension.weighted_score }} {{ t('chat.quality_points') }} ·
            {{ t(`chat.quality_assessor.${dimension.assessor}`) }}
          </span>
        </div>
        <div
          v-for="(detail, index) in dimension.details"
          :key="`${detail.step_index ?? 0}-${detail.code}-${index}`"
          class="quality-detail__reason-text"
        >
          <span v-if="detail.step_index && quality.coverage.step_count > 1">
            {{ t('chat.quality_step', { step: detail.step_index }) }}：
          </span>
          {{ detailText(detail.code, detail.params) }}
        </div>
      </div>

      <template v-if="quality.observations.length">
        <div class="quality-detail__section">{{ t('chat.data_observations') }}</div>
        <div class="quality-detail__observation-hint">
          {{ t('chat.data_observations_hint') }}
        </div>
        <div
          v-for="(observation, index) in quality.observations"
          :key="`${observation.step_index ?? 0}-${observation.code}-${index}`"
          class="quality-detail__observation"
          :class="`quality-detail__observation--${observation.severity}`"
        >
          <span v-if="observation.step_index && quality.coverage.step_count > 1">
            {{ t('chat.quality_step', { step: observation.step_index }) }}：
          </span>
          {{ observationText(observation.code, observation.params) }}
        </div>
      </template>

      <template v-if="quality.passed_checks.length">
        <div class="quality-detail__section">{{ t('chat.quality_checks') }}</div>
        <ul class="quality-detail__checks">
          <li v-for="check in quality.passed_checks" :key="check">
            {{ t(`chat.quality_check.${check}`) }}
          </li>
        </ul>
      </template>
    </div>
  </el-popover>
</template>

<style scoped lang="less">
.quality-stamp {
  --stamp-color: #16a34a;
  --stamp-bg: #f0fdf4;
  --stamp-outline: #86efac;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  min-width: 76px;
  padding: 3px 9px 2px;
  border: 2px solid var(--stamp-color);
  border-radius: 5px;
  outline: 1px solid var(--stamp-outline);
  outline-offset: -5px;
  background: var(--stamp-bg);
  color: var(--stamp-color);
  font-family: inherit;
  line-height: 1;
  transform: rotate(-3deg);
  cursor: pointer;

  &--acceptable {
    --stamp-color: #b7791f;
    --stamp-bg: #fffbeb;
    --stamp-outline: #fcd34d;
  }

  &--reference_only {
    --stamp-color: #dd6b20;
    --stamp-bg: #fff7ed;
    --stamp-outline: #fdba74;
  }

  &--unreliable {
    --stamp-color: #dc2626;
    --stamp-bg: #fef2f2;
    --stamp-outline: #fca5a5;
  }
}

.quality-stamp__label {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1px;
}

.quality-stamp__score {
  margin-top: 3px;
  font-size: 10px;
  font-weight: 600;
}

.quality-detail {
  max-height: 560px;
  overflow-y: auto;
  color: rgba(31, 35, 41, 1);
  font-size: 13px;
}

.quality-detail__title {
  font-size: 15px;
  font-weight: 600;
}

.quality-detail__coverage,
.quality-detail__observation-hint {
  margin-top: 6px;
  color: rgba(100, 106, 115, 1);
}

.quality-detail__section {
  margin-top: 14px;
  font-weight: 600;
}

.quality-detail__dimension {
  margin-top: 10px;
}

.quality-detail__dimension-heading {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-weight: 500;
}

.quality-detail__dimension-score {
  flex-shrink: 0;
  color: rgba(100, 106, 115, 1);
  font-variant-numeric: tabular-nums;
}

.quality-detail__reason-text {
  margin-top: 3px;
  color: rgba(100, 106, 115, 1);
  line-height: 20px;
}

.quality-detail__observation {
  margin-top: 7px;
  padding-left: 9px;
  border-left: 3px solid #94a3b8;
  color: rgba(71, 85, 105, 1);
  line-height: 20px;

  &--warning {
    border-color: #f59e0b;
  }

  &--error {
    border-color: #dc2626;
  }
}

.quality-detail__checks {
  margin: 6px 0 0;
  padding-left: 18px;
  color: rgba(100, 106, 115, 1);
  line-height: 20px;
}
</style>
