<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Ambiguity, ConversationInterrupt, ResumeAnswer } from '@/api/chat'

const props = defineProps<{
  interrupt: ConversationInterrupt
  disabled?: boolean
  correctable?: boolean
}>()

const emit = defineEmits<{
  submit: [
    payload: { interrupt: ConversationInterrupt; answers: ResumeAnswer[]; displayText: string },
  ]
  correct: [
    payload: {
      interrupt: ConversationInterrupt
      answer: ResumeAnswer
      supersedesEvidenceId: string
    },
  ]
}>()

const { t } = useI18n()
const selected = reactive<Record<string, string>>({})
const custom = reactive<Record<string, string>>({})
const activeAmbiguityId = ref<string>()
const detailsAmbiguityId = ref<string>()
const showSummary = ref(false)
const validationError = ref('')
const editing = ref(false)
const correctionAmbiguityId = ref<string>()

const ambiguities = computed(() => props.interrupt.payload.ambiguities || [])
const answered = computed(() => props.interrupt.status === 'consumed')
const canSubmit = computed(() => (!answered.value || editing.value) && !props.disabled)

function existingAnswer(ambiguityId: string) {
  return (props.interrupt.answers || []).find((item) => item.ambiguity_id === ambiguityId)
}

function hasAnswer(ambiguity: Ambiguity) {
  return !!selected[ambiguity.ambiguity_id] || !!custom[ambiguity.ambiguity_id]?.trim()
}

function initialize() {
  for (const key of Object.keys(selected)) delete selected[key]
  for (const key of Object.keys(custom)) delete custom[key]
  for (const ambiguity of ambiguities.value) {
    const answer = existingAnswer(ambiguity.ambiguity_id)
    selected[ambiguity.ambiguity_id] = answer?.mode === 'option' ? answer.option_id || '' : ''
    custom[ambiguity.ambiguity_id] = answer?.mode === 'custom' ? answer.text || '' : ''
  }
  activeAmbiguityId.value = answered.value
    ? undefined
    : ambiguities.value.find((item) => !hasAnswer(item))?.ambiguity_id
  detailsAmbiguityId.value = undefined
  validationError.value = ''
  editing.value = false
  correctionAmbiguityId.value = undefined
}

watch(() => props.interrupt, initialize, { immediate: true, deep: true })

function marker(index: number) {
  return String.fromCharCode(65 + index)
}

function selectedText(ambiguity: Ambiguity) {
  const optionId = selected[ambiguity.ambiguity_id]
  const index = ambiguity.candidate_resolutions.findIndex((item) => item.option_id === optionId)
  if (index >= 0) return `${marker(index)}. ${ambiguity.candidate_resolutions[index].label}`
  return custom[ambiguity.ambiguity_id] || ''
}

function openNext(ambiguity: Ambiguity) {
  const index = ambiguities.value.findIndex((item) => item.ambiguity_id === ambiguity.ambiguity_id)
  activeAmbiguityId.value = ambiguities.value
    .slice(index + 1)
    .find((item) => !hasAnswer(item))?.ambiguity_id
  detailsAmbiguityId.value = undefined
}

function chooseOption(ambiguity: Ambiguity, optionId: string) {
  if (!canAnswer(ambiguity)) return
  if (editing.value) correctionAmbiguityId.value = ambiguity.ambiguity_id
  selected[ambiguity.ambiguity_id] = selected[ambiguity.ambiguity_id] === optionId ? '' : optionId
  if (selected[ambiguity.ambiguity_id]) {
    custom[ambiguity.ambiguity_id] = ''
    if (!editing.value) openNext(ambiguity)
  }
  validationError.value = ''
}

function onCustomInput(ambiguity: Ambiguity) {
  if (editing.value) correctionAmbiguityId.value = ambiguity.ambiguity_id
  if (custom[ambiguity.ambiguity_id]?.trim()) selected[ambiguity.ambiguity_id] = ''
  validationError.value = ''
}

function canAnswer(ambiguity: Ambiguity) {
  return (
    canSubmit.value &&
    (!editing.value ||
      !correctionAmbiguityId.value ||
      correctionAmbiguityId.value === ambiguity.ambiguity_id)
  )
}

function toggleCorrection() {
  if (!props.correctable || props.disabled) return
  if (editing.value) {
    initialize()
    return
  }
  editing.value = true
  activeAmbiguityId.value = ambiguities.value[0]?.ambiguity_id
  validationError.value = ''
}

function toggleAmbiguity(id: string) {
  activeAmbiguityId.value = activeAmbiguityId.value === id ? undefined : id
  if (detailsAmbiguityId.value !== activeAmbiguityId.value) detailsAmbiguityId.value = undefined
}

function toggleDetails(id: string) {
  detailsAmbiguityId.value = detailsAmbiguityId.value === id ? undefined : id
  if (detailsAmbiguityId.value) activeAmbiguityId.value = id
}

function submit() {
  if (!canSubmit.value) return
  if (editing.value) {
    const ambiguity = ambiguities.value.find(
      (item) => item.ambiguity_id === correctionAmbiguityId.value
    )
    const previous = ambiguity ? existingAnswer(ambiguity.ambiguity_id) : undefined
    if (!ambiguity || !previous?.evidence_id) {
      validationError.value = t('chat.clarification_correction_required')
      return
    }
    const text = custom[ambiguity.ambiguity_id]?.trim()
    const optionId = selected[ambiguity.ambiguity_id]
    if (!text && !optionId) {
      validationError.value = t('chat.clarification_correction_required')
      return
    }
    const answer: ResumeAnswer = text
      ? { ambiguity_id: ambiguity.ambiguity_id, mode: 'custom', text }
      : { ambiguity_id: ambiguity.ambiguity_id, mode: 'option', option_id: optionId }
    emit('correct', {
      interrupt: props.interrupt,
      answer,
      supersedesEvidenceId: previous.evidence_id,
    })
    return
  }
  const missing = ambiguities.value.find((item) => !item.can_assume && !hasAnswer(item))
  if (missing) {
    validationError.value = t('chat.clarification_required', {
      title: missing.business_question,
    })
    activeAmbiguityId.value = missing.ambiguity_id
    return
  }
  const answers: ResumeAnswer[] = []
  ambiguities.value.forEach((item) => {
    const text = custom[item.ambiguity_id]?.trim()
    if (text) {
      answers.push({ ambiguity_id: item.ambiguity_id, mode: 'custom', text })
      return
    }
    const optionId = selected[item.ambiguity_id]
    if (optionId) {
      answers.push({ ambiguity_id: item.ambiguity_id, mode: 'option', option_id: optionId })
    }
  })
  const lines = ambiguities.value
    .filter(hasAnswer)
    .map((item) => `- ${item.business_question}：${selectedText(item)}`)
  emit('submit', {
    interrupt: props.interrupt,
    answers,
    displayText: `${t('chat.clarification_confirmed')}\n${lines.join('\n')}`,
  })
}
</script>

<template>
  <section class="clarification-card">
    <header>
      <div>
        <div class="card-title">{{ t('chat.clarification_title') }}</div>
        <div v-if="showSummary && interrupt.payload.summary" class="secondary">
          {{ interrupt.payload.summary }}
        </div>
      </div>
      <div class="header-actions">
        <button
          v-if="answered && correctable"
          type="button"
          class="link-button"
          :disabled="disabled"
          @click="toggleCorrection"
        >
          {{
            editing ? t('chat.clarification_cancel_correction') : t('chat.clarification_correct')
          }}
        </button>
        <button
          v-if="interrupt.payload.summary"
          type="button"
          class="link-button"
          @click="showSummary = !showSummary"
        >
          {{ showSummary ? t('chat.clarification_hide_details') : t('chat.clarification_details') }}
        </button>
        <el-tag v-if="answered" type="info" effect="plain">
          {{ t('chat.clarification_answered') }}
        </el-tag>
      </div>
    </header>

    <div
      v-for="(ambiguity, ambiguityIndex) in ambiguities"
      :key="ambiguity.ambiguity_id"
      class="ambiguity"
    >
      <div
        class="ambiguity-heading"
        role="button"
        tabindex="0"
        @click="toggleAmbiguity(ambiguity.ambiguity_id)"
      >
        <span class="question-index">{{ ambiguityIndex + 1 }}</span>
        <div class="ambiguity-main">
          <div class="ambiguity-title">{{ ambiguity.business_question }}</div>
          <div
            v-if="activeAmbiguityId !== ambiguity.ambiguity_id && hasAnswer(ambiguity)"
            class="selected-summary"
          >
            {{ selectedText(ambiguity) }}
          </div>
        </div>
        <button
          type="button"
          class="link-button"
          @click.stop="toggleDetails(ambiguity.ambiguity_id)"
        >
          {{
            detailsAmbiguityId === ambiguity.ambiguity_id
              ? t('chat.clarification_hide_details')
              : t('chat.clarification_details')
          }}
        </button>
        <span class="chevron" :class="{ expanded: activeAmbiguityId === ambiguity.ambiguity_id }"
          >›</span
        >
      </div>

      <div v-if="activeAmbiguityId === ambiguity.ambiguity_id">
        <div
          v-if="detailsAmbiguityId === ambiguity.ambiguity_id && ambiguity.reason"
          class="secondary"
        >
          {{ ambiguity.reason }}
        </div>
        <div class="option-list">
          <button
            v-for="(option, optionIndex) in ambiguity.candidate_resolutions"
            :key="option.option_id"
            type="button"
            class="option"
            :class="{ selected: selected[ambiguity.ambiguity_id] === option.option_id }"
            :disabled="!canAnswer(ambiguity)"
            @click="chooseOption(ambiguity, option.option_id)"
          >
            <span class="option-marker">{{ marker(optionIndex) }}</span>
            <span class="selector"
              ><span
                v-if="selected[ambiguity.ambiguity_id] === option.option_id"
                class="selector-dot"
            /></span>
            <span class="option-content">
              <span class="option-title">
                {{ option.label }}
                <el-tag
                  v-if="ambiguity.recommended_candidate_id === option.option_id"
                  size="small"
                  type="success"
                  effect="light"
                >
                  {{ t('chat.clarification_recommended') }}
                </el-tag>
              </span>
              <span
                v-if="detailsAmbiguityId === ambiguity.ambiguity_id && option.description"
                class="secondary"
                >{{ option.description }}</span
              >
              <span
                v-if="detailsAmbiguityId === ambiguity.ambiguity_id && option.impact"
                class="secondary"
              >
                {{ t('chat.clarification_impact') }}：{{ option.impact }}
              </span>
            </span>
          </button>
        </div>
        <div
          v-if="detailsAmbiguityId === ambiguity.ambiguity_id && ambiguity.recommendation_reason"
          class="secondary"
        >
          {{ t('chat.clarification_recommendation_reason') }}：{{ ambiguity.recommendation_reason }}
        </div>
        <el-input
          v-if="!answered || editing || custom[ambiguity.ambiguity_id]?.trim()"
          v-model="custom[ambiguity.ambiguity_id]"
          class="custom-answer"
          type="textarea"
          :rows="2"
          :disabled="!canAnswer(ambiguity)"
          :placeholder="t('chat.clarification_custom_placeholder')"
          @input="onCustomInput(ambiguity)"
          @blur="custom[ambiguity.ambiguity_id]?.trim() && !editing && openNext(ambiguity)"
        />
      </div>
    </div>

    <div v-if="validationError" class="validation-error">{{ validationError }}</div>
    <footer v-if="!answered || editing">
      <span class="secondary">{{ t('chat.clarification_submit_hint') }}</span>
      <el-button type="primary" :disabled="!canSubmit" @click="submit">
        {{ editing ? t('chat.clarification_save_correction') : t('chat.clarification_continue') }}
      </el-button>
    </footer>
  </section>
</template>

<style scoped lang="less">
.clarification-card {
  margin-top: 8px;
  padding: 18px;
  border: 1px solid rgba(28, 186, 144, 0.28);
  border-radius: 12px;
  background: rgba(28, 186, 144, 0.04);
}
header,
footer,
.header-actions,
.ambiguity-heading,
.option-title {
  display: flex;
  align-items: center;
}
header,
footer {
  justify-content: space-between;
  gap: 16px;
}
.header-actions {
  gap: 8px;
}
.card-title,
.ambiguity-title {
  color: #1f2329;
  font-weight: 600;
}
.card-title {
  font-size: 16px;
}
.ambiguity {
  padding: 14px 0;
  border-top: 1px solid rgba(31, 35, 41, 0.08);
}
.ambiguity-heading {
  gap: 12px;
  cursor: pointer;
}
.ambiguity-main {
  min-width: 0;
  flex: 1;
}
.question-index,
.option-marker {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}
.selected-summary {
  margin-top: 4px;
  color: #10b981;
}
.link-button {
  border: 0;
  color: #667085;
  background: transparent;
  cursor: pointer;
}
.chevron {
  color: #667085;
  transform: rotate(90deg);
  transition: transform 0.2s;
}
.chevron.expanded {
  transform: rotate(-90deg);
}
.option-list {
  display: grid;
  gap: 8px;
  margin: 12px 0;
}
.option {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(31, 35, 41, 0.14);
  border-radius: 10px;
  text-align: left;
  background: #fff;
  cursor: pointer;
}
.option.selected {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.06);
}
.selector {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  margin-top: 5px;
  border: 1px solid #98a2b3;
  border-radius: 50%;
}
.selector-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #10b981;
}
.option-content {
  display: grid;
  flex: 1;
  gap: 4px;
}
.option-title {
  gap: 8px;
  font-weight: 500;
}
.secondary {
  margin-top: 6px;
  color: #667085;
  font-size: 13px;
}
.custom-answer {
  margin-top: 10px;
}
.validation-error {
  margin-top: 8px;
  color: #f04438;
}
</style>
