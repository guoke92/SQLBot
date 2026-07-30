import { computed, ref, toValue, type MaybeRefOrGetter } from 'vue'
import { dictionaryApi, type DictionaryFieldConfig } from '@/api/dictionary'

const getConfiguredId = (config: DictionaryFieldConfig): number | null => {
  return config.configured ? config.id : null
}

export const useDictionaryConfigs = (
  datasourceId: MaybeRefOrGetter<number>,
  tableId: MaybeRefOrGetter<number | undefined>,
  available: MaybeRefOrGetter<boolean>
) => {
  const configs = ref<DictionaryFieldConfig[]>([])
  const busyFieldIds = ref(new Set<number>())
  const error = ref<string>()
  let loadSequence = 0

  const byField = computed(() => new Map(configs.value.map((config) => [config.field_id, config])))

  const setBusy = (ids: number[], busy: boolean) => {
    const next = new Set(busyFieldIds.value)
    ids.forEach((id) => (busy ? next.add(id) : next.delete(id)))
    busyFieldIds.value = next
  }

  const load = async () => {
    const sequence = ++loadSequence
    const dsId = toValue(datasourceId)
    const currentTableId = toValue(tableId)
    if (!dsId || !currentTableId || !toValue(available)) {
      if (sequence === loadSequence) {
        configs.value = []
        error.value = undefined
      }
      return
    }
    if (sequence === loadSequence) {
      configs.value = []
      error.value = undefined
    }
    try {
      const result = await dictionaryApi.list(dsId, currentTableId)
      if (
        sequence === loadSequence &&
        dsId === toValue(datasourceId) &&
        currentTableId === toValue(tableId)
      ) {
        configs.value = result
        error.value = undefined
      }
    } catch (reason) {
      if (sequence === loadSequence) {
        configs.value = []
        error.value = reason instanceof Error ? reason.message : String(reason)
      }
    }
  }

  const updateEnabled = async (config: DictionaryFieldConfig, enabled: boolean) => {
    setBusy([config.field_id], true)
    error.value = undefined
    try {
      const configId = getConfiguredId(config)
      if (configId === null) {
        if (enabled) {
          await dictionaryApi.create(toValue(datasourceId), {
            field_id: config.field_id,
            enabled: true,
            max_values: config.max_values,
          })
        }
      } else {
        await dictionaryApi.update(configId, { enabled })
      }
      await load()
      if (error.value) throw new Error(error.value)
    } catch (reason) {
      error.value = reason instanceof Error ? reason.message : String(reason)
      throw reason
    } finally {
      setBusy([config.field_id], false)
    }
  }

  const refresh = async (selected: DictionaryFieldConfig[]) => {
    const fieldIds = selected.map((config) => config.field_id)
    setBusy(fieldIds, true)
    error.value = undefined
    try {
      const ids = selected.flatMap((config) => {
        const configId = getConfiguredId(config)
        return configId === null ? [] : [configId]
      })
      if (!ids.length) return []
      const results = await dictionaryApi.refresh(ids)
      await load()
      if (error.value) throw new Error(error.value)
      return results
    } catch (reason) {
      error.value = reason instanceof Error ? reason.message : String(reason)
      throw reason
    } finally {
      setBusy(fieldIds, false)
    }
  }

  return {
    configs,
    error,
    byField,
    busyFieldIds,
    load,
    updateEnabled,
    refresh,
  }
}
