<script lang="ts" setup>
import { ref, reactive, onMounted, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { datasourceApi } from '@/api/datasource'
import icon_upload_outlined from '@/assets/svg/icon_upload_outlined.svg'
import icon_searchOutline_outlined from '@/assets/svg/icon_search-outline_outlined.svg'
import { encrypted, decrypted } from './js/aes'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import type { FormInstance, FormRules } from 'element-plus-secondary'
import icon_form_outlined from '@/assets/svg/icon_form_outlined.svg'
import FixedSizeList from 'element-plus-secondary/es/components/virtual-list/src/components/fixed-size-list.mjs'
import { debounce } from 'lodash-es'
import { Plus } from '@element-plus/icons-vue'
import { haveSchema } from '@/views/ds/js/ds-type'
import { setSize } from '@/utils/utils'
import EmptyBackground from '@/views/dashboard/common/EmptyBackground.vue'
import icon_fileExcel_colorful from '@/assets/datasource/icon_excel.png'
import IconOpeDelete from '@/assets/svg/icon_delete.svg'
import { useCache } from '@/utils/useCache'
import ExcelDetailDialog from './ExcelDetailDialog.vue'
import icon_visible_outlined from '@/assets/embedded/icon_visible_outlined.svg'
import icon_down_outlined from '@/assets/svg/icon_down_outlined.svg'
import icon_up_outlined from '@/assets/svg/icon_up_outlined.svg'

const props = withDefaults(
  defineProps<{
    activeName: string
    activeType: string
    activeStep: number
    isDataTable: boolean
  }>(),
  {
    activeName: '',
    activeType: '',
    activeStep: 0,
    isDataTable: false,
  }
)

const dsFormRef = ref<FormInstance>()
const excelDetailDialogRef = ref<InstanceType<typeof ExcelDetailDialog>>()
const emit = defineEmits(['refresh', 'changeActiveStep', 'close'])
const isCreate = ref(true)
const isEditTable = ref(false)
const checkList = ref<any>([])
const tableList = ref<any>([])
const excelUploadSuccess = ref(false)
const tableListLoading = ref(false)
const tableListLoadingV1 = ref(false)
const checkLoading = ref(false)
const dialogTitle = ref('')
const getUploadURL = import.meta.env.VITE_API_BASE_URL + '/datasource/parseExcel'
const saveLoading = ref<boolean>(false)
const uploadLoading = ref(false)
const { t } = useI18n()
const schemaList = ref<any>([])

const rules = reactive<FormRules>({
  name: [
    {
      required: true,
      message: t('datasource.please_enter') + t('common.empty') + t('ds.name'),
      trigger: 'blur',
    },
    { min: 1, max: 50, message: t('ds.form.validate.name_length'), trigger: 'blur' },
  ],
  type: [
    {
      required: true,
      message: t('datasource.Please_select') + t('common.empty') + t('ds.type'),
      trigger: 'change',
    },
  ],
  host: [
    {
      required: true,
      message: t('datasource.please_enter') + t('common.empty') + t('ds.form.host'),
      trigger: 'blur',
    },
  ],
  port: [
    {
      required: true,
      message: t('datasource.please_enter') + t('common.empty') + t('ds.form.port'),
      trigger: 'blur',
    },
  ],
  database: [
    {
      required: true,
      message: t('datasource.please_enter') + t('common.empty') + t('ds.form.database'),
      trigger: 'blur',
    },
  ],
  mode: [{ required: true, message: 'Please choose mode', trigger: 'change' }],
  sheets: [{ required: true, message: t('user.upload_file'), trigger: 'change' }],
  dbSchema: [
    {
      required: true,
      message: t('datasource.please_enter') + t('common.empty') + 'Schema',
      trigger: 'blur',
    },
  ],
  filename: [
    {
      required: true,
      message: t('datasource.please_enter') + t('common.empty') + t('ds.form.file_path'),
      trigger: 'blur',
    },
  ],
  baseUrl: [
    {
      required: true,
      message: t('datasource.please_enter') + t('common.empty') + 'Base URL',
      trigger: 'blur',
    },
  ],
})

const dialogVisible = ref<boolean>(false)
const form = ref<any>({
  name: '',
  description: '',
  type: props.activeType,
  configuration: '',
  driver: '',
  host: '',
  port: 0,
  username: '',
  password: '',
  database: '',
  extraJdbc: '',
  dbSchema: '',
  filename: '',
  sheets: [],
  mode: 'service_name',
  timeout: 30,
  lowVersion: false,
  ssl: false,
  // API datasource fields
  baseUrl: '',
  authType: 'none',
  apiKey: '',
  apiKeyHeader: 'X-API-Key',
  bearerToken: '',
  basicUsername: '',
  basicPassword: '',
  // Cookie auth: list of {name, value}; saved as auth.cookies dict
  cookiePairs: [] as Array<{ name: string; value: string }>,
  endpoints: [] as any[],
  swaggerUrl: '',
})

const createEmptyEndpoint = () => ({
  name: '',
  path: '',
  method: 'GET',
  description: '',
  body_mode: 'object',
  data_path: '',
  code_path: '',
  code_success_value: null as any,
  total_path: '',
  params: [] as any[],
  response_fields: [] as any[],
  extra_headers: {},
  extra_query: {},
  body_template: null as string | null,
  // UI-only state (prefixed with _; stripped before conf save)
  _checked: true,
  _state: 'new' as 'saved' | 'new',
})

const createEmptyParam = () => ({
  name: '',
  type: 'string',
  required: false,
  default: null as string | null,
  description: '',
  location: 'query',
  example: null as string | null,
  enabled: true,
})

const createEmptyResponseField = () => ({
  name: '',
  type: 'string',
  description: '',
  path: '',
  enabled: true,
})

const addEndpoint = () => {
  if (!form.value.endpoints) form.value.endpoints = []
  form.value.endpoints.push(createEmptyEndpoint())
}

const removeEndpoint = (index: number) => {
  form.value.endpoints.splice(index, 1)
}

const addEndpointParam = (ep: any) => {
  if (!ep.params) ep.params = []
  ep.params.push(createEmptyParam())
}

const removeEndpointParam = (ep: any, idx: number) => {
  ep.params.splice(idx, 1)
}

const addResponseField = (ep: any) => {
  if (!ep.response_fields) ep.response_fields = []
  ep.response_fields.push(createEmptyResponseField())
}

const removeResponseField = (ep: any, idx: number) => {
  ep.response_fields.splice(idx, 1)
}

// ---- Swagger / OpenAPI → unified endpoint list ----
const swaggerInputMode = ref<'url' | 'content'>('url')
const swaggerContent = ref('')
const swaggerParsing = ref(false)
const swaggerFilterKeyword = ref('')
const swaggerFilterMethods = ref<string[]>([])
const swaggerExpandedNames = ref<string[]>([])

/** Filter + method options operate on the unified form.endpoints list. */
const endpointMethodOptions = computed(() => {
  const set = new Set<string>()
  for (const ep of form.value.endpoints || []) {
    const m = String(ep.method || 'GET').toUpperCase()
    if (m) set.add(m)
  }
  const order = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
  return Array.from(set).sort((a, b) => {
    const ia = order.indexOf(a)
    const ib = order.indexOf(b)
    if (ia === -1 && ib === -1) return a.localeCompare(b)
    if (ia === -1) return 1
    if (ib === -1) return -1
    return ia - ib
  })
})

const endpointFilteredEndpoints = computed(() => {
  const kw = (swaggerFilterKeyword.value || '').trim().toLowerCase()
  const methods = new Set(
    (swaggerFilterMethods.value || []).map((m) => String(m).toUpperCase()).filter(Boolean)
  )
  return (form.value.endpoints || []).filter((ep: any) => {
    if (methods.size && !methods.has(String(ep.method || 'GET').toUpperCase())) return false
    if (!kw) return true
    const hay = [ep.name, ep.path, ep.description, ep.method]
      .map((x: any) => String(x || '').toLowerCase())
      .join(' ')
    return hay.includes(kw)
  })
})

const endpointFilterActive = computed(
  () => !!(swaggerFilterKeyword.value.trim() || swaggerFilterMethods.value.length)
)

const endpointCheckedCount = computed(
  () => (form.value.endpoints || []).filter((ep: any) => ep._checked !== false).length
)

const endpointCheckAll = computed({
  get() {
    const visible = endpointFilteredEndpoints.value
    if (!visible.length) return false
    return visible.every((ep: any) => ep._checked !== false)
  },
  set(val: boolean) {
    handleEndpointCheckAll(val)
  },
})

const endpointIndeterminate = computed(() => {
  const visible = endpointFilteredEndpoints.value
  if (!visible.length) return false
  let n = 0
  for (const ep of visible) {
    if (ep._checked !== false) n++
  }
  return n > 0 && n < visible.length
})

const resetEndpointFilters = () => {
  swaggerFilterKeyword.value = ''
  swaggerFilterMethods.value = []
}

const applySwaggerMetaHints = (payload: any) => {
  const baseUrl = String(payload?.base_url || payload?.baseUrl || '').trim()
  const title = String(payload?.title || '').trim()
  if (baseUrl && !String(form.value.baseUrl || '').trim()) {
    form.value.baseUrl = baseUrl
  }
  if (title && !String(form.value.name || '').trim()) {
    form.value.name = title.slice(0, 50)
  }
}

const doParseSwagger = async () => {
  const isUrl = swaggerInputMode.value === 'url'
  const payload: { content?: string; url?: string } = {}
  if (isUrl) {
    if (!form.value.swaggerUrl.trim()) return
    payload.url = form.value.swaggerUrl.trim()
  } else {
    if (!swaggerContent.value.trim()) return
    payload.content = swaggerContent.value
  }
  swaggerParsing.value = true
  try {
    const res: any = await datasourceApi.parseOpenapi(payload)
    const data = res?.data && (res.data.endpoints || res.data.base_url !== undefined) ? res.data : res
    const endpoints = data?.endpoints || []
    if (!endpoints.length) {
      ElMessage.warning(t('ds.form.swagger_no_endpoints'))
      return
    }
    // Merge into form.endpoints — skip duplicates by name
    const existingNames = new Set((form.value.endpoints || []).map((ep: any) => ep.name))
    let added = 0
    let skipped = 0
    if (!form.value.endpoints) form.value.endpoints = []
    for (const ep of endpoints) {
      if (existingNames.has(ep.name || '')) {
        skipped++
        continue
      }
      form.value.endpoints.push({
        ...createEmptyEndpoint(),
        name: ep.name || '',
        path: ep.path || '',
        method: ep.method || 'GET',
        description: ep.description || '',
        body_mode: ep.body_mode || 'object',
        data_path: ep.data_path || '',
        code_path: ep.code_path || '',
        code_success_value: ep.code_success_value ?? null,
        total_path: ep.total_path || '',
        params: Array.isArray(ep.params) ? ep.params.map((p: any) => ({ ...createEmptyParam(), ...p })) : [],
        response_fields: Array.isArray(ep.response_fields)
          ? ep.response_fields.map((f: any) => ({ ...createEmptyResponseField(), ...f }))
          : [],
        extra_headers: ep.extra_headers || {},
        extra_query: ep.extra_query || {},
        body_template: ep.body_template || null,
        _checked: true,
        _state: 'new',
      })
      added++
    }
    if (added) ElMessage.success(t('ds.form.import_success', { n: added }))
    if (skipped) ElMessage.warning(t('ds.form.duplicate_endpoints_skipped', { n: skipped }))
    applySwaggerMetaHints(data)
  } catch (e: any) {
    ElMessage.error(e?.message || t('ds.form.swagger_parse_error'))
  } finally {
    swaggerParsing.value = false
  }
}

const handleSwaggerFile = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    swaggerContent.value = (e.target?.result as string) || ''
    swaggerInputMode.value = 'content'
  }
  reader.readAsText(file)
  return false
}

const handleEndpointCheckAll = (val: boolean) => {
  const visibleSet = new Set(endpointFilteredEndpoints.value.map((ep: any) => ep.name))
  for (const ep of form.value.endpoints || []) {
    if (visibleSet.has(ep.name)) {
      ep._checked = val
    }
  }
}

const toggleEndpointMethodFilter = (method: string) => {
  const m = String(method).toUpperCase()
  const cur = swaggerFilterMethods.value.slice()
  const idx = cur.indexOf(m)
  if (idx >= 0) cur.splice(idx, 1)
  else cur.push(m)
  swaggerFilterMethods.value = cur
}

const isEndpointExpanded = (name: string) => swaggerExpandedNames.value.includes(name)

const toggleEndpointExpand = (name: string) => {
  const idx = swaggerExpandedNames.value.indexOf(name)
  if (idx >= 0) {
    swaggerExpandedNames.value = swaggerExpandedNames.value.filter((n) => n !== name)
  } else {
    swaggerExpandedNames.value = [...swaggerExpandedNames.value, name]
  }
}

const methodTagType = (method: string) => {
  const m = (method || '').toUpperCase()
  if (m === 'GET') return 'success'
  if (m === 'POST') return ''
  if (m === 'PUT' || m === 'PATCH') return 'warning'
  if (m === 'DELETE') return 'danger'
  return 'info'
}

const normalizeEndpoints = (list: any[] | undefined | null) => {
  if (!Array.isArray(list)) return []
  return list.map((raw: any) => ({
    name: raw.name || '',
    path: raw.path || '',
    method: (raw.method || 'GET').toUpperCase(),
    description: raw.description || '',
    body_mode: raw.body_mode || 'object',
    data_path: raw.data_path || '',
    code_path: raw.code_path || '',
    code_success_value: raw.code_success_value ?? null,
    total_path: raw.total_path || '',
    body_template: raw.body_template ?? null,
    extra_headers: raw.extra_headers || {},
    extra_query: raw.extra_query || {},
    params: Array.isArray(raw.params)
      ? raw.params.map((p: any) => ({
          name: p.name || '',
          type: p.type || 'string',
          required: !!p.required,
          default: p.default ?? null,
          description: p.description || '',
          location: p.location || 'query',
          example: p.example ?? null,
          enabled: p.enabled !== false,
        }))
      : [],
    response_fields: Array.isArray(raw.response_fields)
      ? raw.response_fields.map((f: any) => ({
          name: f.name || '',
          type: f.type || 'string',
          description: f.description || '',
          path: f.path || '',
          enabled: f.enabled !== false,
        }))
      : [],
    // Preserve UI-only state if present
    _checked: raw._checked !== false,
    _state: raw._state || 'new',
  }))
}

/** Strip _-prefixed UI-only keys from an endpoint before sending to backend. */
const endpointToConf = (ep: any) => {
  const out: any = {}
  for (const [k, v] of Object.entries(ep)) {
    if (!k.startsWith('_')) out[k] = v
  }
  return out
}

const endpointsAsTables = () => {
  return normalizeEndpoints(form.value.endpoints)
    .filter((ep) => ep._checked !== false && ep.name && ep.path)
    .map((ep) => ({
      tableName: ep.name,
      tableComment: ep.description || `${ep.method} ${ep.path}`,
    }))
}

const close = () => {
  dialogVisible.value = false
  isCreate.value = true
  emit('changeActiveStep', 0)
  emit('close')
  isEditTable.value = false
  checkList.value = []
  tableList.value = []
  excelUploadSuccess.value = false
  saveLoading.value = false
}

const { wsCache } = useCache()
const token = wsCache.get('user.token')
const headers = ref<any>({ 'X-SQLBOT-TOKEN': `Bearer ${token}` })

const initForm = (item: any, editTable: boolean = false) => {
  isEditTable.value = false
  keywords.value = ''
  dsFormRef.value!.clearValidate()
  if (item) {
    dialogTitle.value = editTable ? t('ds.form.title.choose_tables') : t('ds.form.title.edit')
    isCreate.value = false
    form.value.id = item.id
    form.value.name = item.name
    form.value.description = item.description
    form.value.type = item.type
    form.value.configuration = item.configuration
    if (item.configuration) {
      const configuration = JSON.parse(decrypted(item.configuration))
      if (item.type === 'api') {
        form.value.baseUrl = configuration.base_url || ''
        form.value.timeout = configuration.timeout || 30
        const auth = configuration.auth || {}
        form.value.authType = auth.type || 'none'
        form.value.apiKey = auth.api_key || ''
        form.value.apiKeyHeader = auth.api_key_header || 'X-API-Key'
        form.value.bearerToken = auth.bearer_token || ''
        form.value.basicUsername = auth.basic_username || ''
        form.value.basicPassword = auth.basic_password || ''
        form.value.cookiePairs = cookiesToPairs(auth.cookies)
        form.value.swaggerUrl = configuration.swagger_url || ''
        form.value.endpoints = normalizeEndpoints(configuration.endpoints).map((ep: any) => ({
          ...ep,
          _checked: true,
          _state: 'saved',
        }))
      } else {
        form.value.host = configuration.host
        form.value.port = configuration.port
        form.value.username = configuration.username
        form.value.password = configuration.password
        form.value.database = configuration.database
        form.value.extraJdbc = configuration.extraJdbc
        form.value.dbSchema = configuration.dbSchema
        form.value.filename = configuration.filename
        form.value.sheets = configuration.sheets
        form.value.mode = configuration.mode
        form.value.timeout = configuration.timeout ? configuration.timeout : 30
        form.value.lowVersion =
          configuration.lowVersion !== null && configuration.lowVersion !== undefined
            ? configuration.lowVersion
            : true
        form.value.ssl =
          configuration.ssl !== null && configuration.ssl !== undefined ? configuration.ssl : false
      }
    }

    if (editTable) {
      dialogTitle.value =
        item.type === 'api' ? t('ds.form.confirm_endpoints') : t('ds.form.choose_tables')
      emit('changeActiveStep', 2)
      isEditTable.value = true
      isCreate.value = false
      // request tables and check tables

      tableListLoadingV1.value = true
      if (item.type === 'api') {
        // API: conf endpoints are the projection source; no free-form table picker.
        tableList.value = endpointsAsTables()
        checkList.value = tableList.value.map((ele: any) => ele.tableName)
        nextTick(() => {
          handleCheckedTablesChange([...checkList.value])
        })
        tableListLoadingV1.value = false
      } else {
        datasourceApi
          .tableList(item.id)
          .then((res: any) => {
            checkList.value = res.map((ele: any) => {
              return ele.table_name
            })
            if (item.type === 'excel') {
              tableList.value = form.value.sheets
              nextTick(() => {
                handleCheckedTablesChange([...checkList.value])
              })
            } else {
              tableListLoading.value = true
              const requestObj = buildConf()
              datasourceApi
                .getTablesByConf(requestObj)
                .then((table) => {
                  tableList.value = table
                  checkList.value = checkList.value.filter((ele: string) => {
                    return table
                      .map((ele: any) => {
                        return ele.tableName
                      })
                      .includes(ele)
                  })
                  nextTick(() => {
                    handleCheckedTablesChange([...checkList.value])
                  })
                })
                .finally(() => {
                  tableListLoading.value = false
                })
            }
          })
          .finally(() => {
            tableListLoadingV1.value = false
          })
      }
    }
  } else {
    dialogTitle.value = t('ds.form.title.add')
    isCreate.value = true
    isEditTable.value = false
    checkList.value = []
    tableList.value = []
    form.value = {
      name: '',
      description: '',
      type: 'mysql',
      configuration: '',
      driver: '',
      host: '',
      port: 0,
      username: '',
      password: '',
      database: '',
      extraJdbc: '',
      dbSchema: '',
      filename: '',
      sheets: [],
      mode: 'service_name',
      timeout: 30,
      lowVersion: false,
      ssl: false,
      baseUrl: '',
      authType: 'none',
      apiKey: '',
      apiKeyHeader: 'X-API-Key',
      bearerToken: '',
      basicUsername: '',
      basicPassword: '',
      cookiePairs: [],
      endpoints: [],
      swaggerUrl: '',
    }
  }
  dialogVisible.value = true
}

const save = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate(async (valid) => {
    if (valid) {
      if (form.value.type === 'api') {
        const endpoints = normalizeEndpoints(form.value.endpoints)
          .filter((ep) => ep._checked !== false && ep.name && ep.path)
          .map(endpointToConf)
        if (!endpoints.length) {
          ElMessage({
            message: t('ds.form.endpoints_required'),
            type: 'error',
            showClose: true,
          })
          return
        }
        form.value.endpoints = endpoints
      }

      const list =
        form.value.type === 'api'
          ? endpointsAsTables().map((ele: any) => ({
              table_name: ele.tableName,
              table_comment: ele.tableComment,
            }))
          : tableList.value
              .filter((ele: any) => {
                return checkTableList.value.includes(ele.tableName)
              })
              .map((ele: any) => {
                return { table_name: ele.tableName, table_comment: ele.tableComment }
              })

      if (form.value.type !== 'api' && checkTableList.value.length > 30) {
        const excessive = await ElMessageBox.confirm(t('common.excessive_tables_selected'), {
          tip: t('common.to_continue_saving', { msg: checkTableList.value.length }),
          confirmButtonText: t('common.save'),
          cancelButtonText: t('common.cancel'),
          confirmButtonType: 'primary',
          type: 'warning',
          customClass: 'confirm-with_icon',
          autofocus: false,
        })

        if (excessive !== 'confirm') return
      }
      saveLoading.value = true

      const requestObj = buildConf()
      if (form.value.id) {
        if (!isEditTable.value || form.value.type === 'api') {
          // API: conf is truth source; backend re-syncs CoreTable from conf.
          // only update datasource config info
          datasourceApi
            .update(requestObj)
            .then(() => {
              close()
              emit('refresh')
            })
            .finally(() => {
              saveLoading.value = false
            })
        } else {
          // save table and field
          datasourceApi
            .chooseTables(form.value.id, list)
            .then(() => {
              close()
              emit('refresh')
            })
            .finally(() => {
              saveLoading.value = false
            })
        }
      } else {
        requestObj.tables = list
        datasourceApi
          .add(requestObj)
          .then(() => {
            close()
            emit('refresh')
          })
          .finally(() => {
            saveLoading.value = false
          })
      }
    }
  })
}

const cookiesToPairs = (cookies: any): Array<{ name: string; value: string }> => {
  if (!cookies || typeof cookies !== 'object') return []
  return Object.entries(cookies)
    .filter(([name]) => !!name)
    .map(([name, value]) => ({ name: String(name), value: value == null ? '' : String(value) }))
}

const pairsToCookies = (
  pairs: Array<{ name: string; value: string }> | undefined
): Record<string, string> => {
  const out: Record<string, string> = {}
  for (const p of pairs || []) {
    const name = (p?.name || '').trim()
    if (!name) continue
    out[name] = p?.value == null ? '' : String(p.value)
  }
  return out
}

const addCookiePair = () => {
  if (!Array.isArray(form.value.cookiePairs)) form.value.cookiePairs = []
  form.value.cookiePairs.push({ name: '', value: '' })
}

const removeCookiePair = (index: number) => {
  form.value.cookiePairs.splice(index, 1)
}

const buildConf = () => {
  if (form.value.type === 'api') {
    const authConfig: any = { type: form.value.authType || 'none' }
    if (form.value.authType === 'api_key') {
      authConfig.api_key = form.value.apiKey || ''
      authConfig.api_key_header = form.value.apiKeyHeader || 'X-API-Key'
      authConfig.api_key_location = 'header'
    } else if (form.value.authType === 'bearer') {
      authConfig.bearer_token = form.value.bearerToken || ''
    } else if (form.value.authType === 'basic') {
      authConfig.basic_username = form.value.basicUsername || ''
      authConfig.basic_password = form.value.basicPassword || ''
    } else if (form.value.authType === 'cookie') {
      authConfig.cookies = pairsToCookies(form.value.cookiePairs)
    }
    form.value.configuration = encrypted(
      JSON.stringify({
        base_url: form.value.baseUrl || '',
        swagger_url: form.value.swaggerUrl || '',
        timeout: form.value.timeout || 30,
        headers: {},
        auth: authConfig,
        endpoints: normalizeEndpoints(form.value.endpoints)
          .filter((ep: any) => ep._checked !== false && ep.name && ep.path)
          .map(endpointToConf),
      })
    )
    const obj = JSON.parse(JSON.stringify(form.value))
    delete obj.baseUrl
    delete obj.authType
    delete obj.apiKey
    delete obj.apiKeyHeader
    delete obj.bearerToken
    delete obj.basicUsername
    delete obj.basicPassword
    delete obj.cookiePairs
    delete obj.timeout
    delete obj.endpoints
    delete obj.swaggerUrl
    return obj
  }
  form.value.configuration = encrypted(
    JSON.stringify({
      host: form.value.host,
      port: form.value.port,
      username: form.value.username,
      password: form.value.password,
      database: form.value.database,
      extraJdbc: form.value.extraJdbc,
      dbSchema: form.value.dbSchema,
      filename: form.value.filename,
      sheets: form.value.sheets,
      mode: form.value.mode,
      timeout: form.value.timeout,
      lowVersion: form.value.lowVersion,
      ssl: form.value.ssl,
    })
  )
  const obj = JSON.parse(JSON.stringify(form.value))
  delete obj.driver
  delete obj.host
  delete obj.port
  delete obj.username
  delete obj.password
  delete obj.database
  delete obj.extraJdbc
  delete obj.dbSchema
  delete obj.filename
  delete obj.sheets
  delete obj.mode
  delete obj.timeout
  delete obj.lowVersion
  delete obj.ssl
  return obj
}

const check = () => {
  const requestObj = buildConf()
  datasourceApi.check(requestObj).then((res: any) => {
    if (res) {
      ElMessage({
        message: t('ds.form.connect.success'),
        type: 'success',
        showClose: true,
      })
    } else {
      ElMessage({
        message: t('ds.form.connect.failed'),
        type: 'error',
        showClose: true,
      })
    }
  })
}
const getSchema = debounce(() => {
  schemaList.value = []
  const requestObj = buildConf()
  datasourceApi.getSchema(requestObj).then((res: any) => {
    schemaList.value = (res || []).map((item: any) => ({ label: item, value: item }))
  })
}, 300)

onBeforeUnmount(() => (saveLoading.value = false))

const next = debounce(async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      if (form.value.type === 'excel') {
        // next, show tables
        if (excelUploadSuccess.value) {
          emit('changeActiveStep', props.activeStep + 1)
        }
      } else if (form.value.type === 'api') {
        // API: endpoints already edited on step 1. Persist via save without a table picker.
        const endpoints = normalizeEndpoints(form.value.endpoints)
          .filter((ep) => ep._checked !== false && ep.name && ep.path)
          .map(endpointToConf)
        if (!endpoints.length) {
          ElMessage({
            message: t('ds.form.endpoints_required'),
            type: 'error',
            showClose: true,
          })
          return
        }
        form.value.endpoints = endpoints
        tableList.value = endpointsAsTables()
        checkList.value = tableList.value.map((ele: any) => ele.tableName)
        nextTick(() => {
          handleCheckedTablesChange([...checkList.value])
        })
        if (checkLoading.value) return
        const requestObj = buildConf()
        checkLoading.value = true
        datasourceApi
          .check(requestObj)
          .then((res: boolean) => {
            if (res) {
              emit('changeActiveStep', props.activeStep + 1)
            } else {
              ElMessage({
                message: t('ds.form.connect.failed'),
                type: 'error',
                showClose: true,
              })
            }
          })
          .finally(() => {
            checkLoading.value = false
          })
      } else {
        if (checkLoading.value) return
        // check status if success do next
        const requestObj = buildConf()
        checkLoading.value = true
        datasourceApi
          .check(requestObj)
          .then((res: boolean) => {
            if (res) {
              emit('changeActiveStep', props.activeStep + 1)
              // request tables
              datasourceApi.getTablesByConf(requestObj).then((res: any) => {
                tableList.value = res
              })
            } else {
              ElMessage({
                message: t('ds.form.connect.failed'),
                type: 'error',
                showClose: true,
              })
            }
          })
          .finally(() => {
            checkLoading.value = false
          })
      }
    }
  })
}, 300)

const preview = debounce(() => {
  emit('changeActiveStep', props.activeStep - 1)
}, 200)

const beforeUpload = (rawFile: any) => {
  setFile(rawFile)
  if (rawFile.size / 1024 / 1024 > 50) {
    ElMessage.error(t('common.not_exceed_50mb'))
    return false
  }
  uploadLoading.value = true
  return true
}
let fileDetail: any = null
const onSuccess = (response: any) => {
  fileDetail = response.data
  excelDetailDialogRef.value?.init(response.data)
  excelUploadSuccess.value = true
  uploadLoading.value = false
}

const openFile = () => {
  onSuccess({
    data: fileDetail,
  })
}

const saveExcel = (excel: any) => {
  form.value.filename = excel.filename
  form.value.sheets = excel.sheets
  tableList.value = excel.sheets
}

const onError = (e: any) => {
  ElMessage.error(e.toString())
  uploadLoading.value = false
}

onMounted(() => {
  setTimeout(() => {
    dsFormRef.value!.clearValidate()
  }, 100)
})

const keywords = ref('')
const tableListWithSearch = computed(() => {
  if (!keywords.value) return tableList.value
  return tableList.value.filter((ele: any) =>
    ele.tableName.toLowerCase().includes(keywords.value.toLowerCase())
  )
})

watch(keywords, () => {
  const tableNameArr = tableListWithSearch.value.map((ele: any) => ele.tableName)
  checkList.value = checkTableList.value.filter((ele) => tableNameArr.includes(ele))
  const checkedCount = checkList.value.length
  checkAll.value = checkedCount === tableListWithSearch.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < tableListWithSearch.value.length
})

watch(
  () => props.activeType,
  (val) => {
    form.value.type = val
  }
)
const fileSize = ref('-')
const clearFile = () => {
  fileSize.value = ''
  form.value.filename = ''
  form.value.sheets = []
  tableList.value = []
}

const setFile = (file: any) => {
  fileSize.value = setSize(file.size)
}

const checkAll = ref(false)
const isIndeterminate = ref(false)
const checkTableList = ref([] as any[])

const handleCheckAllChange = (val: any) => {
  checkList.value = val
    ? [
        ...new Set([
          ...tableListWithSearch.value.map((ele: any) => ele.tableName),
          ...checkList.value,
        ]),
      ]
    : []
  isIndeterminate.value = false
  const tableNameArr = tableListWithSearch.value.map((ele: any) => ele.tableName)
  checkTableList.value = val
    ? [...new Set([...tableNameArr, ...checkTableList.value])]
    : checkTableList.value.filter((ele) => !tableNameArr.includes(ele))
}

const handleCheckedTablesChange = (value: any[]) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === tableListWithSearch.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < tableListWithSearch.value.length
  const tableNameArr = tableListWithSearch.value.map((ele: any) => ele.tableName)
  checkTableList.value = [
    ...new Set([...checkTableList.value.filter((ele) => !tableNameArr.includes(ele)), ...value]),
  ]
}

const tableListSave = () => {
  save(dsFormRef.value)
}

defineExpose({
  initForm,
  tableListSave,
})
</script>

<template>
  <div
    v-loading="uploadLoading || saveLoading || checkLoading"
    class="model-form"
    :class="(!isCreate || activeStep === 2) && 'edit-form'"
  >
    <div v-if="isCreate && activeStep !== 2" class="model-name">
      {{ activeName }}
      <span v-if="form.type !== 'excel'" style="margin-left: 8px; color: #8f959e; font-size: 12px">
        <span>{{ t('ds.form.support_version') }}:&nbsp;</span>
        <span v-if="form.type === 'sqlServer'">2012+</span>
        <span v-else-if="form.type === 'oracle'">12+</span>
        <span v-else-if="form.type === 'mysql'">5.6+</span>
        <span v-else-if="form.type === 'pg'">9.6+</span>
        <span v-else-if="form.type === 'es'">7+</span>
      </span>
    </div>
    <div class="form-content">
      <el-form
        v-show="activeStep === 1"
        ref="dsFormRef"
        :model="form"
        label-position="top"
        label-width="auto"
        :rules="rules"
        @submit.prevent
      >
        <el-form-item :label="t('ds.name')" prop="name">
          <el-input
            v-model="form.name"
            clearable
            :placeholder="$t('datasource.please_enter') + $t('common.empty') + t('ds.name')"
          />
        </el-form-item>
        <el-form-item :label="t('ds.form.description')">
          <el-input
            v-model="form.description"
            :placeholder="
              $t('datasource.please_enter') + $t('common.empty') + t('ds.form.description')
            "
            :rows="2"
            show-word-limit
            maxlength="200"
            clearable
            type="textarea"
          />
        </el-form-item>
        <div v-if="form.type === 'excel'">
          <el-form-item prop="sheets" :label="t('ds.form.file')">
            <div v-if="form.filename" class="pdf-card">
              <img :src="icon_fileExcel_colorful" width="40px" height="40px" />
              <div class="file-name">
                <div class="name">{{ form.filename }}</div>
                <div class="size">{{ form.filename.split('.')[1] }} - {{ fileSize }}</div>
              </div>
              <div
                style="
                  width: 40px;
                  margin-left: auto;
                  display: flex;
                  align-items: center;
                  justify-content: space-between;
                "
              >
                <el-icon v-if="!form.id" class="action-btn" size="16" @click="openFile">
                  <icon_visible_outlined></icon_visible_outlined>
                </el-icon>
                <el-icon v-if="!form.id" class="action-btn" size="16" @click="clearFile">
                  <IconOpeDelete></IconOpeDelete>
                </el-icon>
              </div>
            </div>
            <el-upload
              v-if="form.filename && !form.id"
              class="upload-user"
              accept=".xlsx,.xls,.csv"
              :headers="headers"
              :action="getUploadURL"
              :before-upload="beforeUpload"
              :on-error="onError"
              :on-success="onSuccess"
              :show-file-list="false"
              :file-list="form.sheets"
            >
              <el-button text style="line-height: 22px; height: 22px">
                {{ $t('common.re_upload') }}
              </el-button>
            </el-upload>
            <el-upload
              v-else-if="!form.id"
              class="upload-user"
              accept=".xlsx,.xls,.csv"
              :headers="headers"
              :action="getUploadURL"
              :before-upload="beforeUpload"
              :on-success="onSuccess"
              :on-error="onError"
              :show-file-list="false"
              :file-list="form.sheets"
            >
              <el-button secondary>
                <el-icon size="16" style="margin-right: 4px">
                  <icon_upload_outlined></icon_upload_outlined>
                </el-icon>
                {{ t('user.upload_file') }}</el-button
              >
            </el-upload>
            <span v-if="!form.filename" class="not_exceed">{{ $t('common.not_exceed_50mb') }}</span>
          </el-form-item>
        </div>
        <div v-if="form.type === 'sqlite'" style="margin-top: 16px">
          <el-form-item :label="t('ds.form.file_path')" prop="filename">
            <el-input
              v-model="form.filename"
              clearable
              :placeholder="$t('datasource.please_enter') + $t('common.empty') + t('ds.form.file_path')"
            />
          </el-form-item>
        </div>
        <div v-if="form.type === 'api'" style="margin-top: 16px">
          <el-form-item label="Base URL" prop="baseUrl">
            <el-input
              v-model="form.baseUrl"
              clearable
              placeholder="https://api.example.com"
            />
          </el-form-item>
          <el-form-item :label="t('ds.form.auth_type')">
            <el-select v-model="form.authType" style="width: 100%">
              <el-option :label="t('ds.form.auth_none')" value="none" />
              <el-option label="API Key" value="api_key" />
              <el-option label="Bearer Token" value="bearer" />
              <el-option label="Basic Auth" value="basic" />
              <el-option :label="t('ds.form.auth_cookie')" value="cookie" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.authType === 'api_key'" label="API Key">
            <el-input v-model="form.apiKey" clearable show-password placeholder="API Key" />
          </el-form-item>
          <el-form-item v-if="form.authType === 'api_key'" label="API Key Header">
            <el-input v-model="form.apiKeyHeader" clearable placeholder="X-API-Key" />
          </el-form-item>
          <el-form-item v-if="form.authType === 'bearer'" label="Bearer Token">
            <el-input v-model="form.bearerToken" clearable show-password placeholder="Bearer Token" />
          </el-form-item>
          <el-form-item v-if="form.authType === 'basic'" :label="t('ds.form.username')">
            <el-input v-model="form.basicUsername" clearable :placeholder="t('ds.form.username')" />
          </el-form-item>
          <el-form-item v-if="form.authType === 'basic'" :label="t('ds.form.password')">
            <el-input v-model="form.basicPassword" clearable show-password :placeholder="t('ds.form.password')" />
          </el-form-item>
          <el-form-item v-if="form.authType === 'cookie'" :label="t('ds.form.auth_cookie')">
            <div class="cookie-auth">
              <p class="cookie-auth__hint">{{ t('ds.form.auth_cookie_hint') }}</p>
              <div
                v-for="(pair, idx) in form.cookiePairs"
                :key="idx"
                class="cookie-auth__row"
              >
                <el-input
                  v-model="pair.name"
                  clearable
                  :placeholder="t('ds.form.cookie_name')"
                  class="cookie-auth__name"
                />
                <el-input
                  v-model="pair.value"
                  clearable
                  show-password
                  :placeholder="t('ds.form.cookie_value')"
                  class="cookie-auth__value"
                />
                <el-button text type="danger" @click="removeCookiePair(idx)">
                  {{ t('common.delete') }}
                </el-button>
              </div>
              <el-button type="primary" link @click="addCookiePair">
                + {{ t('ds.form.add_cookie') }}
              </el-button>
            </div>
          </el-form-item>
          <el-form-item :label="t('ds.form.timeout')">
            <el-input-number v-model="form.timeout" :min="1" :max="300" />
          </el-form-item>

          <!-- Swagger / OpenAPI source config (optional, collapsible) -->
          <el-collapse class="swagger-collapse">
            <el-collapse-item :title="t('ds.form.swagger_section')" name="swagger">
              <p class="swagger-section__hint">{{ t('ds.form.swagger_section_hint') }}</p>
              <el-tabs v-model="swaggerInputMode" class="swagger-import__tabs">
                <el-tab-pane :label="t('ds.form.swagger_url')" name="url">
                  <el-input
                    v-model="form.swaggerUrl"
                    clearable
                    :placeholder="t('ds.form.swagger_url_hint')"
                  >
                    <template #prepend>URL</template>
                    <template #append>
                      <el-button
                        type="primary"
                        :loading="swaggerParsing"
                        :disabled="!form.swaggerUrl.trim()"
                        @click="doParseSwagger"
                      >
                        {{ t('ds.form.parse') }}
                      </el-button>
                    </template>
                  </el-input>
                </el-tab-pane>
                <el-tab-pane :label="t('ds.form.swagger_content')" name="content">
                  <el-input
                    v-model="swaggerContent"
                    type="textarea"
                    :rows="5"
                    :placeholder="t('ds.form.swagger_paste_hint')"
                  />
                  <div class="swagger-import__content-actions">
                    <el-upload
                      :show-file-list="false"
                      :before-upload="handleSwaggerFile"
                      accept=".json,.yaml,.yml"
                    >
                      <el-button secondary size="small">
                        <el-icon size="14" style="margin-right: 4px">
                          <icon_upload_outlined />
                        </el-icon>
                        {{ t('ds.form.swagger_upload') }}
                      </el-button>
                    </el-upload>
                    <el-button
                      type="primary"
                      size="small"
                      :loading="swaggerParsing"
                      :disabled="!swaggerContent.trim()"
                      @click="doParseSwagger"
                    >
                      {{ t('ds.form.parse') }}
                    </el-button>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </el-collapse-item>
          </el-collapse>

          <!-- Unified endpoint list (swagger-parsed + manual) -->
          <div class="api-endpoints">
            <div class="api-endpoints__header">
              <span class="api-endpoints__title">
                {{ t('ds.form.endpoints') }}
                <template v-if="form.endpoints && form.endpoints.length">
                  ({{ endpointCheckedCount }}/{{ form.endpoints.length }})
                </template>
              </span>
              <el-button type="primary" text @click="addEndpoint">
                {{ t('ds.form.add_endpoint') }}
              </el-button>
            </div>

            <!-- Toolbar: search + method filters + check-all -->
            <div v-if="form.endpoints && form.endpoints.length" class="endpoint-toolbar">
              <div class="endpoint-toolbar__row">
                <el-checkbox
                  v-model="endpointCheckAll"
                  :indeterminate="endpointIndeterminate"
                  class="endpoint-toolbar__check-all"
                >
                  {{ t('datasource.select_all') }}
                </el-checkbox>
                <el-input
                  v-model="swaggerFilterKeyword"
                  clearable
                  size="small"
                  class="endpoint-toolbar__search"
                  :placeholder="t('ds.form.swagger_filter_placeholder')"
                >
                  <template #prefix>
                    <el-icon><icon_searchOutline_outlined /></el-icon>
                  </template>
                </el-input>
              </div>
              <div v-if="endpointMethodOptions.length" class="endpoint-toolbar__methods">
                <el-check-tag
                  v-for="m in endpointMethodOptions"
                  :key="m"
                  :checked="swaggerFilterMethods.includes(m)"
                  class="endpoint-toolbar__method-tag"
                  @change="() => toggleEndpointMethodFilter(m)"
                >
                  {{ m }}
                </el-check-tag>
                <span v-if="endpointFilterActive" class="endpoint-toolbar__filter-hint">
                  {{ t('ds.form.swagger_filter_shown', { n: endpointFilteredEndpoints.length }) }}
                </span>
              </div>
            </div>

            <!-- Empty state -->
            <div v-if="!form.endpoints || !form.endpoints.length" class="api-endpoints__empty">
              {{ t('ds.form.endpoints_empty') }}
            </div>
            <EmptyBackground
              v-else-if="!endpointFilteredEndpoints.length"
              class="endpoint-list__empty"
              img-type="noneWhite"
              :description="t('ds.form.swagger_filter_empty')"
            />

            <!-- Endpoint rows -->
            <div v-else class="endpoint-list">
              <div
                v-for="(ep, epIndex) in endpointFilteredEndpoints"
                :key="ep.name || epIndex"
                class="endpoint-item"
                :class="{ 'is-expanded': isEndpointExpanded(ep.name) }"
              >
                <div
                  class="endpoint-item__row"
                  @click="toggleEndpointExpand(ep.name)"
                >
                  <el-checkbox v-model="ep._checked" class="endpoint-item__checkbox" @click.stop />
                  <el-tag
                    size="small"
                    :type="methodTagType(ep.method)"
                    class="endpoint-item__method"
                  >
                    {{ ep.method || 'GET' }}
                  </el-tag>
                  <span class="endpoint-item__name">{{ ep.name || '(unnamed)' }}</span>
                  <span class="endpoint-item__path">{{ ep.path }}</span>
                  <span v-if="ep.description" class="endpoint-item__desc">{{ ep.description }}</span>
                  <el-tag
                    v-if="ep._state === 'saved'"
                    size="small"
                    type="info"
                    class="endpoint-item__state"
                  >
                    {{ t('ds.form.endpoint_saved') }}
                  </el-tag>
                  <el-tag
                    v-else
                    size="small"
                    type="warning"
                    class="endpoint-item__state"
                  >
                    {{ t('ds.form.endpoint_new') }}
                  </el-tag>
                  <el-button
                    text
                    type="primary"
                    size="small"
                    class="endpoint-item__edit-btn"
                    @click.stop.prevent="toggleEndpointExpand(ep.name)"
                  >
                    <el-icon size="12" style="margin-right: 2px">
                      <icon_up_outlined v-if="isEndpointExpanded(ep.name)" />
                      <icon_down_outlined v-else />
                    </el-icon>
                    {{ t('common.edit') }}
                  </el-button>
                  <el-button
                    text
                    type="danger"
                    class="endpoint-item__delete-btn"
                    @click.stop="removeEndpoint(form.endpoints.indexOf(ep))"
                  >
                    <el-icon size="14"><IconOpeDelete /></el-icon>
                  </el-button>
                </div>

                <!-- Expanded detail / edit form -->
                <div v-if="isEndpointExpanded(ep.name)" class="endpoint-detail">
                  <el-form-item :label="t('ds.form.endpoint_name')" class="endpoint-detail__field">
                    <el-input v-model="ep.name" clearable placeholder="list_users" />
                  </el-form-item>
                  <div class="endpoint-detail__row">
                    <el-form-item :label="t('ds.form.endpoint_method')" class="endpoint-detail__field">
                      <el-select v-model="ep.method" style="width: 120px">
                        <el-option label="GET" value="GET" />
                        <el-option label="POST" value="POST" />
                        <el-option label="PUT" value="PUT" />
                        <el-option label="PATCH" value="PATCH" />
                        <el-option label="DELETE" value="DELETE" />
                      </el-select>
                    </el-form-item>
                    <el-form-item :label="t('ds.form.endpoint_path')" class="endpoint-detail__field endpoint-detail__field--wide">
                      <el-input v-model="ep.path" clearable placeholder="/v1/users/{id}" />
                    </el-form-item>
                  </div>
                  <el-form-item :label="t('ds.form.endpoint_desc')" class="endpoint-detail__field">
                    <el-input v-model="ep.description" clearable :placeholder="t('ds.form.endpoint_desc')" />
                  </el-form-item>
                  <el-form-item :label="t('ds.form.data_path')" class="endpoint-detail__field">
                    <el-input v-model="ep.data_path" clearable placeholder="data.items" />
                  </el-form-item>

                  <!-- Params sub-table -->
                  <div class="api-subblock">
                    <div class="api-subblock__header">
                      <span>{{ t('ds.form.params') }} ({{ (ep.params || []).length }})</span>
                      <el-button text type="primary" @click="addEndpointParam(ep)">
                        {{ t('ds.form.add_param') }}
                      </el-button>
                    </div>
                    <el-table
                      v-if="ep.params && ep.params.length"
                      :data="ep.params"
                      size="small"
                      border
                      class="api-field-table"
                      :row-class-name="({ row }) => row.enabled === false ? 'is-disabled-row' : ''"
                    >
                      <el-table-column width="40" align="center">
                        <template #default="{ row }">
                          <el-checkbox v-model="row.enabled" />
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('ds.form.param_name')" min-width="120">
                        <template #default="{ row }">
                          <el-input v-model="row.name" size="small" :placeholder="t('ds.form.param_name')" :disabled="!row.enabled" />
                        </template>
                      </el-table-column>
                      <el-table-column label="Location" width="100">
                        <template #default="{ row }">
                          <el-select v-model="row.location" size="small" :disabled="!row.enabled">
                            <el-option label="query" value="query" />
                            <el-option label="path" value="path" />
                            <el-option label="header" value="header" />
                            <el-option label="body" value="body" />
                          </el-select>
                        </template>
                      </el-table-column>
                      <el-table-column label="Type" width="100">
                        <template #default="{ row }">
                          <el-select v-model="row.type" size="small" :disabled="!row.enabled">
                            <el-option label="string" value="string" />
                            <el-option label="number" value="number" />
                            <el-option label="boolean" value="boolean" />
                            <el-option label="integer" value="integer" />
                          </el-select>
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('ds.form.required')" width="70" align="center">
                        <template #default="{ row }">
                          <el-checkbox v-model="row.required" :disabled="!row.enabled" />
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('ds.form.param_default')" min-width="100">
                        <template #default="{ row }">
                          <el-input v-model="row.default" size="small" :placeholder="t('ds.form.param_default')" :disabled="!row.enabled" />
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('ds.form.field_desc')" min-width="120">
                        <template #default="{ row }">
                          <el-input v-model="row.description" size="small" :placeholder="t('ds.form.field_desc')" :disabled="!row.enabled" />
                        </template>
                      </el-table-column>
                      <el-table-column width="50" align="center">
                        <template #default="{ $index }">
                          <el-button text type="danger" size="small" @click="removeEndpointParam(ep, $index)">
                            <el-icon size="14"><IconOpeDelete /></el-icon>
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                    <div v-else class="api-subblock__empty">
                      {{ t('ds.form.swagger_no_params') }}
                    </div>
                  </div>

                  <!-- Response fields sub-table -->
                  <div class="api-subblock">
                    <div class="api-subblock__header">
                      <span>{{ t('ds.form.response_fields') }} ({{ (ep.response_fields || []).length }})</span>
                      <el-button text type="primary" @click="addResponseField(ep)">
                        {{ t('ds.form.add_field') }}
                      </el-button>
                    </div>
                    <el-table
                      v-if="ep.response_fields && ep.response_fields.length"
                      :data="ep.response_fields"
                      size="small"
                      border
                      class="api-field-table"
                      :row-class-name="({ row }) => row.enabled === false ? 'is-disabled-row' : ''"
                    >
                      <el-table-column width="40" align="center">
                        <template #default="{ row }">
                          <el-checkbox v-model="row.enabled" />
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('ds.form.field_name')" min-width="120">
                        <template #default="{ row }">
                          <el-input v-model="row.name" size="small" :placeholder="t('ds.form.field_name')" :disabled="!row.enabled" />
                        </template>
                      </el-table-column>
                      <el-table-column label="Type" width="100">
                        <template #default="{ row }">
                          <el-select v-model="row.type" size="small" :disabled="!row.enabled">
                            <el-option label="string" value="string" />
                            <el-option label="number" value="number" />
                            <el-option label="boolean" value="boolean" />
                            <el-option label="integer" value="integer" />
                          </el-select>
                        </template>
                      </el-table-column>
                      <el-table-column label="Path" min-width="120">
                        <template #default="{ row }">
                          <el-input v-model="row.path" size="small" :placeholder="t('ds.form.field_path')" :disabled="!row.enabled" />
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('ds.form.field_desc')" min-width="140">
                        <template #default="{ row }">
                          <el-input v-model="row.description" size="small" :placeholder="t('ds.form.field_desc')" :disabled="!row.enabled" />
                        </template>
                      </el-table-column>
                      <el-table-column width="50" align="center">
                        <template #default="{ $index }">
                          <el-button text type="danger" size="small" @click="removeResponseField(ep, $index)">
                            <el-icon size="14"><IconOpeDelete /></el-icon>
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                    <div v-else class="api-subblock__empty">
                      {{ t('ds.form.swagger_no_fields') }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="form.type !== 'excel' && form.type !== 'sqlite' && form.type !== 'api'" style="margin-top: 16px">
          <el-form-item
            :label="form.type !== 'es' ? t('ds.form.host') : t('ds.form.address')"
            prop="host"
          >
            <el-input
              v-model="form.host"
              clearable
              :placeholder="
                $t('datasource.please_enter') +
                $t('common.empty') +
                (form.type !== 'es' ? t('ds.form.host') : t('ds.form.address'))
              "
            />
          </el-form-item>
          <el-form-item v-if="form.type !== 'es'" :label="t('ds.form.port')" prop="port">
            <el-input
              v-model="form.port"
              clearable
              :placeholder="$t('datasource.please_enter') + $t('common.empty') + t('ds.form.port')"
            />
          </el-form-item>
          <el-form-item :label="t('ds.form.username')">
            <el-input
              v-model="form.username"
              clearable
              :placeholder="
                $t('datasource.please_enter') + $t('common.empty') + t('ds.form.username')
              "
            />
          </el-form-item>
          <el-form-item :label="t('ds.form.password')">
            <el-input
              v-model="form.password"
              clearable
              :placeholder="
                $t('datasource.please_enter') + $t('common.empty') + t('ds.form.password')
              "
              type="password"
              show-password
            />
          </el-form-item>
          <el-form-item
            v-if="form.type !== 'dm' && form.type !== 'es'"
            :label="t('ds.form.database')"
            prop="database"
          >
            <el-input
              v-model="form.database"
              clearable
              :placeholder="
                $t('datasource.please_enter') + $t('common.empty') + t('ds.form.database')
              "
            />
          </el-form-item>
          <el-form-item
            v-if="form.type === 'oracle'"
            :label="t('ds.form.connect_mode')"
            prop="mode"
          >
            <el-radio-group v-model="form.mode">
              <el-radio value="service_name">{{ t('ds.form.mode.service_name') }}</el-radio>
              <el-radio value="sid">{{ t('ds.form.mode.sid') }}</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item
            v-if="form.type === 'sqlServer'"
            :label="t('ds.form.low_version')"
            prop="low_version"
          >
            <el-checkbox v-model="form.lowVersion" :label="t('ds.form.low_version')" />
          </el-form-item>
          <el-form-item v-if="form.type === 'mysql' || form.type === 'doris'" :label="t('ds.form.ssl')" prop="ssl">
            <el-switch v-model="form.ssl" />
          </el-form-item>
          <el-form-item v-if="form.type !== 'es'" :label="t('ds.form.extra_jdbc')">
            <el-input
              v-model="form.extraJdbc"
              clearable
              :placeholder="
                $t('datasource.please_enter') + $t('common.empty') + t('ds.form.extra_jdbc')
              "
            />
          </el-form-item>
          <el-form-item v-if="haveSchema.includes(form.type)" class="schema-label" prop="dbSchema">
            <template #label>
              <span class="name">Schema<i class="required" /></span>
              <el-button text size="small" @click="getSchema">
                <template #icon>
                  <Icon name="icon_add_outlined">
                    <Plus class="svg-icon" />
                  </Icon>
                </template>
                {{ t('datasource.get_schema') }}
              </el-button>
            </template>
            <el-select
              v-model="form.dbSchema"
              filterable
              :placeholder="$t('datasource.please_enter') + $t('common.empty') + 'Schema'"
            >
              <el-option
                v-for="item in schemaList"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.type !== 'es'" :label="t('ds.form.timeout')" prop="timeout">
            <el-input-number
              v-model="form.timeout"
              clearable
              :min="0"
              :max="300"
              controls-position="right"
            />
          </el-form-item>
        </div>
      </el-form>
      <div
        v-show="activeStep === 2"
        v-loading="tableListLoading || tableListLoadingV1"
        class="select-data_table"
      >
        <div class="title">
          <template v-if="form.type === 'api'">
            {{ $t('ds.form.confirm_endpoints') }} ({{ tableList.length }})
          </template>
          <template v-else>
            {{ $t('ds.form.choose_tables') }} ({{ checkTableList.length }}/ {{ tableList.length }})
          </template>
        </div>
        <div v-if="form.type === 'api'" class="api-confirm-tip">
          {{ $t('ds.form.confirm_endpoints_tip') }}
        </div>
        <el-input
          v-if="form.type !== 'api'"
          v-model="keywords"
          clearable
          style="width: 100%; margin-bottom: 16px"
          :placeholder="$t('datasource.search')"
        >
          <template #prefix>
            <el-icon>
              <icon_searchOutline_outlined class="svg-icon" />
            </el-icon>
          </template>
        </el-input>
        <div class="container">
          <template v-if="form.type === 'api'">
            <EmptyBackground
              v-if="!tableList.length"
              :description="$t('ds.form.endpoints_empty')"
              img-type="tree"
              style="width: 100%"
            />
            <div v-else class="api-endpoint-confirm-list">
              <div v-for="item in tableList" :key="item.tableName" class="list-item_primary api-endpoint-confirm-item">
                <el-icon size="16" style="margin-right: 8px">
                  <icon_form_outlined></icon_form_outlined>
                </el-icon>
                <div class="api-endpoint-confirm-meta">
                  <div class="name">{{ item.tableName }}</div>
                  <div v-if="item.tableComment" class="desc">{{ item.tableComment }}</div>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="select-all">
              <el-checkbox
                v-model="checkAll"
                :indeterminate="isIndeterminate"
                @change="handleCheckAllChange"
              >
                {{ t('datasource.select_all') }}
              </el-checkbox>
            </div>
            <EmptyBackground
              v-if="!!keywords && !tableListWithSearch.length"
              :description="$t('datasource.relevant_content_found')"
              img-type="tree"
              style="width: 100%"
            />
            <el-checkbox-group
              v-else
              v-model="checkList"
              style="position: relative"
              @change="handleCheckedTablesChange"
            >
              <FixedSizeList
                :item-size="32"
                :data="tableListWithSearch"
                :total="tableListWithSearch.length"
                :width="800"
                :height="460"
                :scrollbar-always-on="true"
                class-name="ed-select-dropdown__list"
                layout="vertical"
              >
                <template #default="{ index, style }">
                  <div class="list-item_primary" :style="style">
                    <el-checkbox :label="tableListWithSearch[index].tableName">
                      <el-icon size="16" style="margin-right: 8px">
                        <icon_form_outlined></icon_form_outlined>
                      </el-icon>
                      {{ tableListWithSearch[index].tableName }}</el-checkbox
                    >
                  </div>
                </template>
              </FixedSizeList>
            </el-checkbox-group>
          </template>
        </div>
      </div>
    </div>
    <div class="draw-foot">
      <el-button secondary @click="close">{{ t('common.cancel') }}</el-button>
      <el-button v-show="form.type !== 'excel' && !isDataTable" secondary @click="check">
        {{ t('ds.check') }}
      </el-button>
      <el-button v-show="activeStep !== 0 && isCreate" secondary @click="preview">
        {{ t('ds.previous') }}
      </el-button>
      <el-button v-show="activeStep === 1 && isCreate" type="primary" @click="next(dsFormRef)">
        {{ t('common.next') }}
      </el-button>
      <el-button v-show="activeStep === 2 || !isCreate" type="primary" @click="save(dsFormRef)">
        {{ t('common.save') }}
      </el-button>
    </div>
  </div>
  <ExcelDetailDialog ref="excelDetailDialogRef" @finish="saveExcel" />
</template>

<style lang="less" scoped>
.model-form {
  width: calc(100% - 280px);
  position: absolute;
  right: 0;
  top: 56px;
  height: 100%;
  padding-bottom: 120px;
  overflow-y: auto;
  .model-name {
    height: 56px;
    width: 100%;
    padding-left: 24px;
    border-bottom: 1px solid #1f232926;
    font-weight: 500;
    font-size: 16px;
    line-height: 24px;
    display: flex;
    align-items: center;
  }

  .form-content {
    width: 800px;
    margin: 0 auto;
    padding-top: 24px;

    .upload-user {
      height: 32px;
      .ed-upload {
        width: 100% !important;
      }
    }

    .not_exceed {
      font-weight: 400;
      font-size: 14px;
      line-height: 22px;
      color: #8f959e;
      display: inline-block;
      width: 100%;
    }

    .pdf-card {
      width: 100%;
      height: 58px;
      display: flex;
      align-items: center;
      padding: 0 16px 0 12px;
      border: 1px solid #dee0e3;
      border-radius: 6px;

      .file-name {
        margin-left: 8px;
        .name {
          font-weight: 400;
          font-size: 14px;
          line-height: 22px;
        }

        .size {
          font-weight: 400;
          font-size: 12px;
          line-height: 20px;
          color: #8f959e;
        }
      }

      .ed-icon {
        position: relative;
        cursor: pointer;
        color: #646a73;

        &::after {
          content: '';
          background-color: #1f23291a;
          position: absolute;
          border-radius: 6px;
          width: 24px;
          height: 24px;
          transform: translate(-50%, -50%);
          top: 50%;
          left: 50%;
          display: none;
        }

        &:hover {
          &::after {
            display: block;
          }
        }
      }
    }

    .ed-form-item--default {
      margin-bottom: 16px;

      &.is-error {
        margin-bottom: 40px;
      }
    }
  }

  :deep(.draw-foot) {
    position: fixed;
    bottom: 0;
    right: 0;
    width: calc(100% - 280px);
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    border-top: 1px solid #1f232926;
    padding-right: 24px;
    background-color: #fff;
    z-index: 10;
  }

  &.edit-form {
    width: 100%;

    :deep(.draw-foot) {
      width: 100%;
    }
  }
  .select-data_table {
    padding-bottom: 24px;
    .title {
      font-weight: 500;
      font-size: 16px;
      line-height: 24px;
      margin: 0 0 16px 0;
    }
    .container {
      border: 1px solid #dee0e3;
      border-radius: 6px;
      overflow: hidden;

      .select-all {
        background: #f5f6f7;
        height: 40px;
        padding-left: 12px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #dee0e3;
      }

      :deep(.ed-checkbox__label) {
        display: inline-flex;
        align-items: center;
      }

      :deep(.ed-vl__window) {
        scrollbar-width: none;
      }
    }
  }
}

.schema-label {
  ::v-deep(.ed-form-item__label) {
    display: flex !important;
    justify-content: space-between;
    padding-right: 0;

    &::after {
      display: none;
    }

    .name {
      .required::after {
        content: '*';
        color: #f54a45;
        margin-left: 2px;
      }
    }
  }
}

.api-endpoints {
  margin-top: 16px;
  .api-endpoints__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .api-endpoints__title {
    font-weight: 500;
    font-size: 14px;
  }
  .api-endpoints__empty {
    color: #8f959e;
    font-size: 13px;
    margin-bottom: 8px;
  }
}

.cookie-auth {
  width: 100%;
  .cookie-auth__hint {
    margin: 0 0 8px;
    font-size: 12px;
    line-height: 20px;
    color: #8f959e;
  }
  .cookie-auth__row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }
  .cookie-auth__name {
    width: 180px;
    flex-shrink: 0;
  }
  .cookie-auth__value {
    flex: 1;
    min-width: 0;
  }
}

.swagger-collapse {
  margin-top: 8px;
  border: none;
  :deep(.ed-collapse-item__header) {
    font-weight: 500;
    font-size: 14px;
    color: #1f2329;
  }
  :deep(.ed-collapse-item__wrap) {
    border-bottom: none;
  }
}
.swagger-section__hint {
  margin: 0 0 10px;
  font-size: 12px;
  line-height: 20px;
  color: #8f959e;
}
.swagger-import__tabs {
  margin-top: 4px;
}
.swagger-import__content-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.endpoint-toolbar {
  margin-bottom: 8px;
  .endpoint-toolbar__row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }
  .endpoint-toolbar__check-all {
    flex-shrink: 0;
  }
  .endpoint-toolbar__search {
    flex: 1;
    max-width: 320px;
  }
  .endpoint-toolbar__methods {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
  }
  .endpoint-toolbar__method-tag {
    cursor: pointer;
  }
  .endpoint-toolbar__filter-hint {
    font-size: 12px;
    color: #8f959e;
    margin-left: 4px;
  }
}

.endpoint-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.endpoint-list__empty {
  padding: 24px 0;
}

.endpoint-item {
  border: 1px solid #dee0e3;
  border-radius: 6px;
  background: #fff;
  transition: background-color 0.2s;
  &:hover {
    background-color: #f9fafb;
  }
  &.is-expanded {
    background: #fff;
    border-color: #c0c4cc;
  }
  .endpoint-item__row {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    min-height: 40px;
    cursor: pointer;
  }
  .endpoint-item__checkbox {
    flex-shrink: 0;
  }
  .endpoint-item__method {
    flex-shrink: 0;
    text-transform: uppercase;
  }
  .endpoint-item__name {
    font-weight: 500;
    font-size: 13px;
    color: #1f2329;
    flex-shrink: 0;
  }
  .endpoint-item__path {
    font-size: 12px;
    color: #646a73;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .endpoint-item__desc {
    font-size: 12px;
    color: #8f959e;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .endpoint-item__state {
    flex-shrink: 0;
  }
  .endpoint-item__expand-btn {
    flex-shrink: 0;
    padding: 2px;
  }
  .endpoint-item__edit-btn {
    flex-shrink: 0;
    padding: 2px;
    font-size: 12px;
  }
  .endpoint-item__delete-btn {
    flex-shrink: 0;
    padding: 2px;
  }
}

.endpoint-detail {
  padding: 12px 12px 4px;
  border-top: 1px dashed #dee0e3;
  background: #f7f8fa;
  border-radius: 0 0 6px 6px;
  .endpoint-detail__row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
  .endpoint-detail__field {
    margin-bottom: 12px;
    flex: 1;
    min-width: 200px;
    &--wide {
      flex: 2;
    }
  }
}

.api-subblock {
  margin: 8px 0 12px;
  .api-subblock__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
    font-size: 13px;
    color: #646a73;
  }
  .api-subblock__empty {
    font-size: 12px;
    color: #8f959e;
    margin-bottom: 8px;
  }
}
.api-inline-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
  .ed-input {
    width: 140px;
  }
}
.api-field-table {
  margin-bottom: 12px;
  :deep(.ed-table__row) {
    &.is-disabled-row {
      opacity: 0.5;
    }
  }
  :deep(.ed-input.is-disabled .ed-input__inner) {
    color: #a8abb2;
  }
}
.api-confirm-tip {
  color: #8f959e;
  font-size: 13px;
  margin-bottom: 12px;
}
.api-endpoint-confirm-list {
  max-height: 460px;
  overflow-y: auto;
  border: 1px solid #dee0e3;
  border-radius: 6px;
  padding: 4px 0;
}
.api-endpoint-confirm-item {
  display: flex;
  align-items: flex-start;
  padding: 10px 16px;
  height: auto;
  min-height: 32px;
  .api-endpoint-confirm-meta {
    .name {
      font-size: 14px;
      line-height: 22px;
      color: #1f2329;
    }
    .desc {
      font-size: 12px;
      line-height: 20px;
      color: #8f959e;
    }
  }
}

.api-endpoints__header {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
