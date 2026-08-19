<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type {
  ClarificationOption,
  ClarificationQuestion,
  ConversationInterrupt,
  ResumeAnswer,
} from '@/api/chat'

const props = defineProps<{
  interrupt: ConversationInterrupt
  disabled?: boolean
  correctable?: boolean
}>()

const emit = defineEmits<{
  submit: [
    payload: {
      interrupt: ConversationInterrupt
      answers: ResumeAnswer[]
      displayText: string
    },
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
const activeQuestionId = ref<string>()
const detailQuestionIds = reactive<Record<string, boolean>>({})
const validationError = ref('')
const editing = ref(false)
const correctionQuestionId = ref<string>()

const questions = computed(() => props.interrupt.payload.questions || [])
const answered = computed(() => props.interrupt.status === 'consumed')
const canSubmit = computed(() => (!answered.value || editing.value) && !props.disabled)

function existingAnswer(questionId: string) {
  return (props.interrupt.answers || []).find((item) => item.question_id === questionId)
}

function hasAnswer(question: ClarificationQuestion) {
  return !!selected[question.question_id] || !!custom[question.question_id]?.trim()
}

function initialize() {
  for (const key of Object.keys(selected)) delete selected[key]
  for (const key of Object.keys(custom)) delete custom[key]
  for (const key of Object.keys(detailQuestionIds)) delete detailQuestionIds[key]
  for (const question of questions.value) {
    const answer = existingAnswer(question.question_id)
    selected[question.question_id] = answer?.mode === 'option' ? answer.option_id || '' : ''
    custom[question.question_id] = answer?.mode === 'custom' ? answer.text || '' : ''
  }
  activeQuestionId.value = answered.value
    ? undefined
    : questions.value.find((item) => !hasAnswer(item))?.question_id
  validationError.value = ''
  editing.value = false
  correctionQuestionId.value = undefined
}

watch(() => props.interrupt, initialize, { immediate: true, deep: true })

function marker(index: number) {
  return String.fromCharCode(65 + index)
}

function selectedText(question: ClarificationQuestion) {
  const optionId = selected[question.question_id]
  const index = question.options.findIndex((item) => item.option_id === optionId)
  if (index >= 0) {
    const option = question.options[index]
    return `${marker(index)}. ${option.label}`
  }
  return custom[question.question_id] || ''
}

function optionFieldRef(option: ClarificationOption) {
  const items =
    option.fields && option.fields.length
      ? option.fields
      : option.field
        ? [{ name: option.field, comment: option.field_comment, table: option.table }]
        : []
  return items
    .map((item) => {
      const name = item.name?.trim()
      if (!name) return ''
      const qualified = item.table?.trim() ? `${item.table.trim()}.${name}` : name
      const comment = item.comment?.trim()
      return comment ? `${qualified}（${comment}）` : qualified
    })
    .filter(Boolean)
    .join('、')
}

function openNext(question: ClarificationQuestion) {
  const index = questions.value.findIndex((item) => item.question_id === question.question_id)
  activeQuestionId.value = questions.value
    .slice(index + 1)
    .find((item) => !hasAnswer(item))?.question_id
}

function chooseOption(question: ClarificationQuestion, optionId: string) {
  if (!canAnswer(question)) return
  if (editing.value) correctionQuestionId.value = question.question_id
  selected[question.question_id] = selected[question.question_id] === optionId ? '' : optionId
  if (selected[question.question_id]) {
    custom[question.question_id] = ''
    if (!editing.value) openNext(question)
  }
  validationError.value = ''
}

function onCustomInput(question: ClarificationQuestion) {
  if (editing.value) correctionQuestionId.value = question.question_id
  if (custom[question.question_id]?.trim()) selected[question.question_id] = ''
  validationError.value = ''
}

function canAnswer(question: ClarificationQuestion) {
  return (
    canSubmit.value &&
    (!editing.value ||
      !correctionQuestionId.value ||
      correctionQuestionId.value === question.question_id)
  )
}

function toggleCorrection() {
  if (!props.correctable || props.disabled) return
  if (editing.value) {
    initialize()
    return
  }
  editing.value = true
  activeQuestionId.value = questions.value[0]?.question_id
  validationError.value = ''
}

function toggleQuestion(id: string) {
  activeQuestionId.value = activeQuestionId.value === id ? undefined : id
}

function toggleDetails(id: string) {
  detailQuestionIds[id] = !detailQuestionIds[id]
  if (detailQuestionIds[id]) activeQuestionId.value = id
}

function submit() {
  if (!canSubmit.value) return
  if (editing.value) {
    const question = questions.value.find(
      (item) => item.question_id === correctionQuestionId.value
    )
    const previous = question ? existingAnswer(question.question_id) : undefined
    if (!question || !previous?.evidence_id) {
      validationError.value = t('chat.clarification_correction_required')
      return
    }
    const text = custom[question.question_id]?.trim()
    const optionId = selected[question.question_id]
    if (!text && !optionId) {
      validationError.value = t('chat.clarification_correction_required')
      return
    }
    const answer: ResumeAnswer = text
      ? { question_id: question.question_id, mode: 'custom', text }
      : { question_id: question.question_id, mode: 'option', option_id: optionId }
    emit('correct', {
      interrupt: props.interrupt,
      answer,
      supersedesEvidenceId: previous.evidence_id,
    })
    return
  }
  const missing = questions.value.find((item) => !hasAnswer(item))
  if (missing) {
    validationError.value = t('chat.clarification_required', {
      title: missing.question,
    })
    activeQuestionId.value = missing.question_id
    return
  }
  const answers: ResumeAnswer[] = []
  questions.value.forEach((item) => {
    const text = custom[item.question_id]?.trim()
    if (text) {
      answers.push({ question_id: item.question_id, mode: 'custom', text })
      return
    }
    const optionId = selected[item.question_id]
    if (optionId) {
      answers.push({ question_id: item.question_id, mode: 'option', option_id: optionId })
    }
  })
  const lines = questions.value
    .filter(hasAnswer)
    .map((item) => `- ${item.question}：${selectedText(item)}`)
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
        <el-tag v-if="answered" type="info" effect="plain">
          {{ t('chat.clarification_answered') }}
        </el-tag>
      </div>
    </header>

    <div
      v-for="(question, questionIndex) in questions"
      :key="question.question_id"
      class="ambiguity"
    >
      <div
        class="ambiguity-heading"
        role="button"
        tabindex="0"
        @click="toggleQuestion(question.question_id)"
      >
        <span class="question-index">{{ questionIndex + 1 }}</span>
        <div class="ambiguity-main">
          <div class="ambiguity-title">{{ question.question }}</div>
          <div
            v-if="activeQuestionId !== question.question_id && hasAnswer(question)"
            class="selected-summary"
          >
            {{ selectedText(question) }}
          </div>
        </div>
        <button
          type="button"
          class="link-button"
          @click.stop="toggleDetails(question.question_id)"
        >
          {{
            detailQuestionIds[question.question_id]
              ? t('chat.clarification_hide_details')
              : t('chat.clarification_details')
          }}
        </button>
        <span class="chevron" :class="{ expanded: activeQuestionId === question.question_id }"
          >›</span
        >
      </div>

      <div v-if="activeQuestionId === question.question_id">
        <div v-if="detailQuestionIds[question.question_id] && question.why" class="reason">
          {{ question.why }}
        </div>
        <div class="option-list">
          <button
            v-for="(option, optionIndex) in question.options"
            :key="option.option_id"
            type="button"
            class="option"
            :class="{ selected: selected[question.question_id] === option.option_id }"
            :disabled="!canAnswer(question)"
            @click="chooseOption(question, option.option_id)"
          >
            <span class="option-marker">{{ marker(optionIndex) }}</span>
            <span class="selector"
              ><span
                v-if="selected[question.question_id] === option.option_id"
                class="selector-dot"
            /></span>
            <span class="option-content">
              <span class="option-title">
                {{ option.label }}
                <el-tag v-if="option.recommended" size="small" type="success" effect="light">
                  {{ t('chat.clarification_recommended') }}
                </el-tag>
              </span>
              <span
                v-if="
                  detailQuestionIds[question.question_id] &&
                  option.meaning &&
                  option.meaning !== option.label
                "
                class="option-meaning"
              >
                {{ option.meaning }}
              </span>
              <span
                v-if="detailQuestionIds[question.question_id] && optionFieldRef(option)"
                class="option-fields"
              >
                {{ optionFieldRef(option) }}
              </span>
            </span>
          </button>
        </div>
        <el-input
          v-if="!answered || editing || custom[question.question_id]?.trim()"
          v-model="custom[question.question_id]"
          class="custom-answer"
          type="textarea"
          :rows="2"
          :disabled="!canAnswer(question)"
          :placeholder="t('chat.clarification_custom_placeholder')"
          @input="onCustomInput(question)"
          @blur="custom[question.question_id]?.trim() && !editing && openNext(question)"
        />
      </div>
    </div>

    <div v-if="validationError" class="validation-error">{{ validationError }}</div>
    <footer v-if="!answered || editing">
      <span class="secondary">{{ t('chat.clarification_submit_hint') }}</span>
      <div class="footer-actions">
        <el-button type="primary" :disabled="!canSubmit" @click="submit">
          {{
            editing ? t('chat.clarification_save_correction') : t('chat.clarification_continue')
          }}
        </el-button>
      </div>
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
.footer-actions {
  display: flex;
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
.option-meaning {
  color: #667085;
  font-size: 13px;
  line-height: 1.5;
}
.option-fields {
  margin-top: 2px;
  padding: 8px 10px;
  border-radius: 8px;
  color: #475467;
  background: rgba(31, 35, 41, 0.04);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  line-height: 1.5;
}
.secondary {
  margin-top: 6px;
  color: #667085;
  font-size: 13px;
}
.reason {
  margin: 10px 0;
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
