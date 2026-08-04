<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ClarificationAnswer, ClarificationQuestion, IntentContext } from '@/api/chat'

const props = defineProps<{
  recordId?: number
  context: IntentContext
  disabled?: boolean
  answered?: boolean
  initialAnswers?: ClarificationAnswer[]
}>()

const emit = defineEmits<{
  submit: [
    payload: {
      parentRecordId: number
      answers: ClarificationAnswer[]
      displayText: string
    },
  ]
}>()

const { t } = useI18n()
const selected = reactive<Record<string, string[]>>({})
const custom = reactive<Record<string, string>>({})
const validationError = ref('')
const activeQuestionId = ref<string>()
const detailsQuestionId = ref<string>()
const showCardDetails = ref(false)

const isBlocked = computed(() => props.context.status === 'blocked')
const canSubmit = computed(
  () =>
    !!props.recordId &&
    props.context.status === 'needs_clarification' &&
    !props.disabled &&
    !props.answered
)

function hasAnswer(question: ClarificationQuestion) {
  return !!selected[question.id]?.length || !!custom[question.id]?.trim()
}

function initializeQuestions(
  questions: ClarificationQuestion[],
  initialAnswers: ClarificationAnswer[] = []
) {
  for (const key of Object.keys(selected)) delete selected[key]
  for (const key of Object.keys(custom)) delete custom[key]
  const answersByQuestion = new Map(initialAnswers.map((answer) => [answer.question_id, answer]))
  for (const question of questions) {
    const answer = answersByQuestion.get(question.id)
    selected[question.id] = [...(answer?.option_ids || [])]
    custom[question.id] = answer?.custom_text || ''
  }
  activeQuestionId.value = props.answered
    ? undefined
    : questions.find((question) => !hasAnswer(question))?.id
  detailsQuestionId.value = undefined
  showCardDetails.value = false
  validationError.value = ''
}

watch(
  [() => props.context.questions, () => props.initialAnswers, () => props.answered],
  ([questions, initialAnswers]) => initializeQuestions(questions || [], initialAnswers || []),
  { immediate: true, deep: true }
)

function optionMarker(index: number) {
  return String.fromCharCode(65 + index)
}

function selectedLabels(question: ClarificationQuestion) {
  return (selected[question.id] || []).map((optionId) => {
    const optionIndex = question.options.findIndex((option) => option.id === optionId)
    const option = question.options[optionIndex]
    return option ? `${optionMarker(optionIndex)}. ${option.label}` : optionId
  })
}

function toggleQuestion(questionId: string) {
  const nextQuestionId = activeQuestionId.value === questionId ? undefined : questionId
  activeQuestionId.value = nextQuestionId
  if (detailsQuestionId.value !== nextQuestionId) detailsQuestionId.value = undefined
}

function toggleDetails(questionId: string) {
  const opening = detailsQuestionId.value !== questionId
  detailsQuestionId.value = opening ? questionId : undefined
  if (opening) activeQuestionId.value = questionId
}

function openNextQuestion(question: ClarificationQuestion) {
  const currentIndex = props.context.questions.findIndex((item) => item.id === question.id)
  const next = props.context.questions.slice(currentIndex + 1).find((item) => !hasAnswer(item))
  activeQuestionId.value = next?.id
  detailsQuestionId.value = undefined
}

function chooseOption(question: ClarificationQuestion, optionId: string) {
  if (!canSubmit.value) return
  const values = selected[question.id] || []
  if (question.selection_type === 'multiple') {
    const removing = values.includes(optionId)
    selected[question.id] = removing
      ? values.filter((id) => id !== optionId)
      : [...values, optionId]
    if (!removing) custom[question.id] = ''
  } else {
    const removing = values.includes(optionId)
    selected[question.id] = removing ? [] : [optionId]
    if (!removing) {
      custom[question.id] = ''
      openNextQuestion(question)
    }
  }
  validationError.value = ''
}

function onCustomInput(question: ClarificationQuestion) {
  if (custom[question.id]?.trim()) selected[question.id] = []
  validationError.value = ''
}

function completeCustomAnswer(question: ClarificationQuestion) {
  if (custom[question.id]?.trim()) openNextQuestion(question)
}

function questionAnswer(question: ClarificationQuestion): ClarificationAnswer {
  return {
    question_id: question.id,
    option_ids: selected[question.id] || [],
    custom_text: (custom[question.id] || '').trim(),
  }
}

function submit() {
  if (!canSubmit.value || !props.recordId) return
  const answers = props.context.questions.map(questionAnswer)
  const missing = props.context.questions.find(
    (question, index) =>
      question.required && answers[index].option_ids.length === 0 && !answers[index].custom_text
  )
  if (missing) {
    validationError.value = t('chat.clarification_required', { title: missing.title })
    return
  }

  const lines = props.context.questions.map((question, index) => {
    const answer = answers[index]
    const labels = answer.option_ids
      .map((id) => question.options.find((option) => option.id === id)?.label)
      .filter(Boolean)
    if (answer.custom_text) labels.push(answer.custom_text)
    return `- ${question.title}：${labels.join('、')}`
  })
  emit('submit', {
    parentRecordId: props.recordId,
    answers,
    displayText: `${t('chat.clarification_confirmed')}\n${lines.join('\n')}`,
  })
}
</script>

<template>
  <section class="clarification-card" :class="{ blocked: isBlocked }">
    <header>
      <div>
        <div class="card-title">
          {{ isBlocked ? t('chat.clarification_blocked_title') : t('chat.clarification_title') }}
        </div>
        <div v-if="context.summary && showCardDetails" class="card-summary">
          {{ context.summary }}
        </div>
      </div>
      <div class="header-actions">
        <button
          v-if="context.summary"
          type="button"
          class="details-toggle"
          @click="showCardDetails = !showCardDetails"
        >
          {{
            showCardDetails ? t('chat.clarification_hide_details') : t('chat.clarification_details')
          }}
        </button>
        <el-tag v-if="answered" type="info" effect="plain">
          {{ t('chat.clarification_answered') }}
        </el-tag>
      </div>
    </header>

    <template v-if="isBlocked">
      <el-alert
        v-for="reason in context.blocking_reasons"
        :key="reason"
        :title="reason"
        type="warning"
        :closable="false"
        show-icon
      />
    </template>

    <div
      v-for="(question, questionIndex) in context.questions"
      v-else
      :key="question.id"
      class="clarification-question"
    >
      <div
        class="question-heading"
        role="button"
        tabindex="0"
        @click="toggleQuestion(question.id)"
        @keydown.enter="toggleQuestion(question.id)"
        @keydown.space.prevent="toggleQuestion(question.id)"
      >
        <span class="question-index">{{ questionIndex + 1 }}</span>
        <div class="question-main">
          <div class="question-title">{{ question.title }}</div>
          <div
            v-if="activeQuestionId !== question.id && hasAnswer(question)"
            class="collapsed-answer"
          >
            {{ selectedLabels(question).join('、') }}
            <template v-if="custom[question.id]">
              <span v-if="selected[question.id]?.length">；</span>{{ custom[question.id] }}
            </template>
          </div>
        </div>
        <button
          v-if="
            question.reason ||
            question.recommendation_reason ||
            question.options.some((option) => option.description || option.impact)
          "
          type="button"
          class="details-toggle"
          @click.stop="toggleDetails(question.id)"
        >
          {{
            detailsQuestionId === question.id
              ? t('chat.clarification_hide_details')
              : t('chat.clarification_details')
          }}
        </button>
        <span class="question-chevron" :class="{ expanded: activeQuestionId === question.id }"
          >›</span
        >
      </div>

      <div
        v-if="
          activeQuestionId === question.id && detailsQuestionId === question.id && question.reason
        "
        class="question-reason"
      >
        {{ question.reason }}
      </div>

      <div v-if="activeQuestionId === question.id && question.options.length" class="option-list">
        <button
          v-for="(option, optionIndex) in question.options"
          :key="option.id"
          type="button"
          class="option"
          :class="{ selected: selected[question.id]?.includes(option.id) }"
          :disabled="!canSubmit"
          @click="chooseOption(question, option.id)"
        >
          <span class="option-marker">{{ optionMarker(optionIndex) }}</span>
          <span class="selector">
            <span v-if="selected[question.id]?.includes(option.id)" class="selector-dot" />
          </span>
          <span class="option-content">
            <span class="option-title-row">
              <span class="option-label">{{ option.label }}</span>
              <el-tag
                v-if="question.recommended_option_ids.includes(option.id)"
                size="small"
                type="success"
                effect="light"
              >
                {{ t('chat.clarification_recommended') }}
              </el-tag>
            </span>
            <span
              v-if="detailsQuestionId === question.id && option.description"
              class="option-description"
            >
              {{ option.description }}
            </span>
            <span v-if="detailsQuestionId === question.id && option.impact" class="option-impact">
              {{ t('chat.clarification_impact') }}：{{ option.impact }}
            </span>
          </span>
        </button>
      </div>

      <div
        v-if="
          activeQuestionId === question.id &&
          detailsQuestionId === question.id &&
          question.recommendation_reason
        "
        class="recommendation-reason"
      >
        {{ t('chat.clarification_recommendation_reason') }}：{{ question.recommendation_reason }}
      </div>

      <el-input
        v-if="
          activeQuestionId === question.id &&
          question.allow_custom &&
          (!answered || !!custom[question.id]?.trim())
        "
        v-model="custom[question.id]"
        class="custom-answer"
        type="textarea"
        :rows="2"
        :disabled="!canSubmit"
        :placeholder="question.custom_placeholder || t('chat.clarification_custom_placeholder')"
        @input="onCustomInput(question)"
        @blur="completeCustomAnswer(question)"
      />
    </div>

    <div v-if="validationError" class="validation-error">{{ validationError }}</div>
    <footer v-if="!isBlocked && !answered">
      <span class="submit-hint">{{ t('chat.clarification_submit_hint') }}</span>
      <el-button type="primary" :disabled="!canSubmit" @click="submit">
        {{ t('chat.clarification_continue') }}
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

  &.blocked {
    border-color: rgba(230, 162, 60, 0.3);
    background: rgba(230, 162, 60, 0.05);
  }

  header,
  footer,
  .question-heading,
  .option-title-row {
    display: flex;
    align-items: center;
  }

  header {
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 14px;
  }

  footer {
    justify-content: space-between;
    gap: 16px;
    margin-top: 16px;
  }
}

.card-title,
.question-title {
  color: rgba(31, 35, 41, 1);
  font-weight: 600;
}

.card-title {
  font-size: 16px;
}

.header-actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 8px;
}

.card-summary,
.question-reason,
.option-description,
.option-impact,
.recommendation-reason,
.submit-hint {
  color: rgba(100, 106, 115, 1);
  font-size: 13px;
  line-height: 20px;
}

.card-summary {
  margin-top: 4px;
}

.clarification-question {
  padding: 14px 0;
  border-top: 1px solid rgba(31, 35, 41, 0.08);
}

.question-heading {
  align-items: center !important;
  gap: 8px;
  cursor: pointer;
  outline: none;

  &:focus-visible {
    border-radius: 6px;
    box-shadow: 0 0 0 2px rgba(28, 186, 144, 0.16);
  }
}

.question-main {
  flex: 1;
  min-width: 0;
}

.collapsed-answer {
  margin-top: 3px;
  overflow: hidden;
  color: var(--ed-color-primary);
  font-size: 13px;
  line-height: 20px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.details-toggle {
  padding: 2px 6px;
  color: rgba(100, 106, 115, 1);
  font-size: 12px;
  border: 0;
  background: transparent;
  cursor: pointer;

  &:hover {
    color: var(--ed-color-primary);
  }
}

.question-chevron {
  color: rgba(100, 106, 115, 0.8);
  font-size: 20px;
  line-height: 20px;
  transform: rotate(90deg);
  transition: transform 0.2s ease;

  &.expanded {
    transform: rotate(-90deg);
  }
}

.question-reason {
  margin: 8px 0 0 30px;
}

.question-index {
  display: inline-flex;
  flex: 0 0 22px;
  align-items: center;
  justify-content: center;
  height: 22px;
  border-radius: 50%;
  background: rgba(28, 186, 144, 0.12);
  color: var(--ed-color-primary);
  font-size: 12px;
  font-weight: 600;
}

.option-list {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.option {
  display: flex;
  width: 100%;
  padding: 12px;
  gap: 10px;
  text-align: left;
  border: 1px solid rgba(222, 224, 227, 1);
  border-radius: 8px;
  background: #fff;
  cursor: pointer;

  &:hover:not(:disabled),
  &.selected {
    border-color: var(--ed-color-primary);
    background: rgba(28, 186, 144, 0.05);
  }

  &:disabled {
    cursor: default;
  }
}

.option-marker {
  display: inline-flex;
  flex: 0 0 22px;
  align-items: center;
  justify-content: center;
  height: 22px;
  border-radius: 6px;
  background: rgba(100, 106, 115, 0.08);
  color: rgba(73, 78, 86, 1);
  font-size: 12px;
  font-weight: 600;
}

.selector {
  display: inline-flex;
  flex: 0 0 16px;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-top: 2px;
  border: 1px solid rgba(100, 106, 115, 0.55);
  border-radius: 50%;
}

.selector-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--ed-color-primary);
}

.option-content {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
  gap: 3px;
}

.option-title-row {
  gap: 8px;
}

.option-label {
  color: rgba(31, 35, 41, 1);
  font-size: 14px;
  font-weight: 500;
}

.option-impact,
.recommendation-reason {
  color: rgba(143, 149, 158, 1);
}

.recommendation-reason {
  margin-top: 8px;
}

.custom-answer {
  margin-top: 10px;
}

.validation-error {
  margin-top: 8px;
  color: var(--ed-color-danger);
  font-size: 13px;
}

@media (max-width: 768px) {
  .clarification-card {
    padding: 14px;

    footer {
      align-items: stretch;
      flex-direction: column;
    }
  }
}
</style>
