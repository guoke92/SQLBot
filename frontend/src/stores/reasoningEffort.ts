import { defineStore } from 'pinia'
import { store } from '@/stores/index.ts'
import { chatApi, type LlmCapabilities, type ReasoningEffortLevel } from '@/api/chat'

/** Wire levels: none/low/high/max. UI shows 关闭/低/中/高. */
export type ReasoningEffortChoice = ReasoningEffortLevel

interface ReasoningEffortState {
  /** Explicit per-chat pick; null means follow model default. */
  choice: ReasoningEffortChoice | null
  pending: ReasoningEffortChoice | null
  chatId: number | undefined
  overrides: Record<string, ReasoningEffortChoice>
  defaultEffort: ReasoningEffortLevel | null
  modelName: string
  loaded: boolean
}

const isLevel = (value: unknown): value is ReasoningEffortLevel =>
  value === 'none' || value === 'low' || value === 'high' || value === 'max'

export const reasoningEffortStore = defineStore('reasoningEffortStore', {
  state: (): ReasoningEffortState => ({
    choice: null,
    pending: null,
    chatId: undefined,
    overrides: {},
    defaultEffort: null,
    modelName: '',
    loaded: false,
  }),
  getters: {
    /** Always send an explicit level when the user picked one. */
    requestEffort(): ReasoningEffortLevel | undefined {
      return this.choice ?? undefined
    },
    effectiveEffort(): ReasoningEffortLevel | null {
      return this.choice ?? this.defaultEffort
    },
  },
  actions: {
    _remember(chatId: number, choice: ReasoningEffortChoice | null) {
      const key = String(chatId)
      if (choice == null) {
        delete this.overrides[key]
        return
      }
      this.overrides[key] = choice
    },
    setActiveChat(chatId: number | undefined) {
      const previousId = this.chatId
      this.chatId = chatId
      if (chatId == null) {
        this.choice = null
        return
      }
      const key = String(chatId)
      if (this.pending != null && previousId == null && this.overrides[key] == null) {
        this._remember(chatId, this.pending)
      }
      this.pending = null
      this.choice = this.overrides[key] ?? null
    },
    setChoice(choice: ReasoningEffortChoice) {
      this.choice = choice
      if (this.chatId != null) {
        this._remember(this.chatId, choice)
        this.pending = null
        return
      }
      this.pending = choice
    },
    async loadCapabilities() {
      try {
        const response = await chatApi.llmCapabilities()
        const data = ((response as any)?.data || response) as LlmCapabilities
        const effort = data?.default_effort
        this.defaultEffort = isLevel(effort) ? effort : null
        this.modelName = data?.model_name || ''
      } catch {
        this.defaultEffort = null
      } finally {
        this.loaded = true
      }
    },
  },
})

export const useReasoningEffortStore = () => reasoningEffortStore(store)
