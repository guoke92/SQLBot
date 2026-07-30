<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ClarificationAnswer, ClarificationQuestion, IntentContext } from '@/api/chat'

const props = defineProps<{
  recordId?: number
  context: IntentContext
  disabled?: boolean
  answered?: boolean
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

const isBlocked = computed(() => props.context.status === 'blocked')
const canSubmit = computed(
  () =>
    !!props.recordId &&
    props.context.status === 'needs_clarification' &&
    !props.disabled &&
    !props.answered
)

function initializeQuestions(questions: ClarificationQuestion[]) {
  for (const key of Object.keys(selected)) delete selected[key]
  for (const key of Object.keys(custom)) delete custom[key]
  for (const question of questions) {
    selected[question.id] = [...(question.recommended_option_ids || [])]
    custom[question.id] = ''
  }
  validationError.value = ''
}

watch(
  () => props.context.questions,
  (questions) => initializeQuestions(questions || []),
  { immediate: true }
)

function chooseOption(question: ClarificationQuestion, optionId: string) {
  if (!canSubmit.value) return
  const values = selected[question.id] || []
  if (question.selection_type === 'multiple') {
    selected[question.id] = values.includes(optionId)
      ? values.filter((id) => id !== optionId)
      : [...values, optionId]
  } else {
    selected[question.id] = [optionId]
    custom[question.id] = ''
  }
  validationError.value = ''
}

function onCustomInput(question: ClarificationQuestion) {
  if (question.selection_type === 'single' && custom[question.id]?.trim()) {
    selected[question.id] = []
  }
  validationError.value = ''
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
        <div v-if="context.summary" class="card-summary">{{ context.summary }}</div>
      </div>
      <el-tag v-if="answered" type="info" effect="plain">
        {{ t('chat.clarification_answered') }}
      </el-tag>
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
      <div class="question-heading">
        <span class="question-index">{{ questionIndex + 1 }}</span>
        <div>
          <div class="question-title">{{ question.title }}</div>
          <div v-if="question.reason" class="question-reason">{{ question.reason }}</div>
        </div>
      </div>

      <div v-if="question.options.length" class="option-list">
        <button
          v-for="option in question.options"
          :key="option.id"
          type="button"
          class="option"
          :class="{ selected: selected[question.id]?.includes(option.id) }"
          :disabled="!canSubmit"
          @click="chooseOption(question, option.id)"
        >
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
            <span v-if="option.description" class="option-description">
              {{ option.description }}
            </span>
            <span v-if="option.impact" class="option-impact">
              {{ t('chat.clarification_impact') }}：{{ option.impact }}
            </span>
          </span>
        </button>
      </div>

      <div v-if="question.recommendation_reason" class="recommendation-reason">
        {{ t('chat.clarification_recommendation_reason') }}：{{ question.recommendation_reason }}
      </div>

      <el-input
        v-if="question.allow_custom"
        v-model="custom[question.id]"
        class="custom-answer"
        type="textarea"
        :rows="2"
        :disabled="!canSubmit"
        :placeholder="question.custom_placeholder || t('chat.clarification_custom_placeholder')"
        @input="onCustomInput(question)"
      />
    </div>

    <div v-if="validationError" class="validation-error">{{ validationError }}</div>
    <footer v-if="!isBlocked">
      <span class="submit-hint">{{ t('chat.clarification_submit_hint') }}</span>
      <el-button type="primary" :disabled="!canSubmit" @click="submit">
        {{ answered ? t('chat.clarification_answered') : t('chat.clarification_continue') }}
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
  align-items: flex-start !important;
  gap: 8px;
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
