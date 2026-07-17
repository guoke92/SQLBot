<script lang="ts" setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { datasourceApi } from '@/api/datasource'
import { encrypted, decrypted } from '@/views/ds/js/aes'
import icon_right_outlined from '@/assets/svg/icon_right_outlined.svg'
import icon_form_outlined from '@/assets/svg/icon_form_outlined.svg'
import icon_import_outlined from '@/assets/svg/icon_import_outlined.svg'
import icon_searchOutline_outlined from '@/assets/svg/icon_search-outline_outlined.svg'
import EmptyBackground from '@/views/dashboard/common/EmptyBackground.vue'
import edit from '@/assets/svg/icon_edit_outlined.svg'
import IconOpeDelete from '@/assets/svg/icon_delete.svg'
import { useI18n } from 'vue-i18n'
import ParamsForm from './ParamsForm.vue'
import UploaderRemark from '@/views/system/excel-upload/UploaderRemark.vue'
import TableRelationship from '@/views/ds/TableRelationship.vue'
import icon_mindnote_outlined from '@/assets/svg/icon_mindnote_outlined.svg'
import { Refresh } from '@element-plus/icons-vue'
import { debounce } from 'lodash-es'

interface Table {
  name: string
  host: string
  port: string
  username: string
  password: string
  database: string
  extraJdbc: string
  dbSchema: string
  filename: string
  sheets: string
  mode: string
  timeout: string
  configuration: string
  id: number
}

const props = withDefaults(
  defineProps<{
    info: Table
  }>(),
  {
    info: () => ({
      name: '-',
      host: '-',
      port: '-',
      username: '-',
      password: '-',
      database: '-',
      extraJdbc: '-',
      dbSchema: '-',
      filename: '-',
      sheets: '-',
      mode: '-',
      timeout: '-',
      configuration: '-',
      id: 0,
    }),
  }
)
const { t } = useI18n()
const paramsFormRef = ref()
const tableList = ref([] as any[])
const loading = ref(false)
const initLoading = ref(false)
const activeRelationship = ref(false)
const keywords = ref('')
const tableListWithSearch = computed(() => {
  if (!keywords.value) return tableList.value
  return tableList.value.filter((ele) =>
    ele.table_name.toLowerCase().includes(keywords.value.toLowerCase())
  )
})
const total = ref(1000)
const showNum = ref(100)
const currentTable = ref<any>({})
const ds = ref<any>({})
const btnSelect = ref('d')
const isDrag = ref(false)
const tableName = ref<any[]>([])
const pageInfo = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
})
const handleRelationship = () => {
  activeRelationship.value = !activeRelationship.value
  tableName.value = []
  currentTable.value = {}
}
const singleDragStartD = (e: DragEvent, ele: any) => {
  isDrag.value = true
  e.dataTransfer!.setData('table', JSON.stringify(ele))
}

const getTableName = (val: any) => {
  tableName.value = val
}

const singleDragEnd = () => {
  isDrag.value = false
}
const handleSizeChange = (val: number) => {
  pageInfo.currentPage = 1
  pageInfo.pageSize = val
}
const handleCurrentChange = (val: number) => {
  pageInfo.currentPage = val
}

const fieldListComputed = computed(() => {
  const { currentPage, pageSize } = pageInfo
  return fieldListTotalComputed.value.slice((currentPage - 1) * pageSize, currentPage * pageSize)
})

const fieldListTotalComputed = computed(() => {
  return fieldList.value.filter((ele: any) =>
    ele.field_name.toLowerCase().includes(fieldName.value.toLowerCase())
  )
})

const init = (reset = false) => {
  initLoading.value = true
  datasourceApi.getDs(props.info.id).then((res) => {
    ds.value = res
    fieldList.value = []
    pageInfo.total = 0
    pageInfo.currentPage = 1
    datasourceApi
      .tableList(props.info.id)
      .then((res) => {
        tableList.value = res

        if (currentTable.value?.id && reset) {
          tableList.value.forEach((ele) => {
            if (ele.id === currentTable.value?.id) {
              clickTable(ele)
            }
          })
        }
      })
      .finally(() => {
        initLoading.value = false
      })
  })
}
onMounted(() => {
  init()
})
const tableComment = ref('')
const fieldDialog = ref<boolean>(false)
const tableDialog = ref<boolean>(false)
const fieldComment = ref('')
const currentField = ref<any>({})
const previewData = ref<any>({})
const fieldList = ref<any>([])
// Conf-owned resource detail (API endpoint contract) — same concept as protocol get_resource_detail
const isApiDs = computed(() => props.info?.type === 'api')
const resourceDetail = ref<any>(null)
const apiParamValues = ref<Record<string, any>>({})
const testResult = ref<any>(null)
const testLoading = ref(false)
const showRawResponse = ref<string[]>([])

const methodTagType = (method: string) => {
  const m = (method || '').toUpperCase()
  if (m === 'GET') return 'success'
  if (m === 'POST') return ''
  if (m === 'PUT' || m === 'PATCH') return 'warning'
  if (m === 'DELETE') return 'danger'
  return 'info'
}

const buildData = () => {
  return { table: currentTable.value, fields: fieldList.value }
}

const handleSelectTableList = () => {
  paramsFormRef.value.open(props.info)
}

const editLoading = ref(false)
const saveEndpointConfig = async () => {
  if (!resourceDetail.value || !props.info?.id) return
  editLoading.value = true
  try {
    const ds = await datasourceApi.getDs(props.info.id)
    const conf = JSON.parse(decrypted(ds.configuration || ''))
    const endpoints = conf.endpoints || []
    const epName = currentTable.value?.table_name
    const idx = endpoints.findIndex(
      (e: any) => (e.name || e.path) === epName
    )
    if (idx >= 0) {
      endpoints[idx].params = (resourceDetail.value.params || []).map((p: any) => ({
        name: p.name,
        type: p.type || 'string',
        required: !!p.required,
        default: p.default ?? null,
        description: p.description || '',
        location: p.location || 'query',
        example: p.example ?? null,
        enabled: p.enabled !== false,
      }))
      endpoints[idx].response_fields = (resourceDetail.value.response_fields || []).map(
        (f: any) => ({
          name: f.name,
          type: f.type || 'string',
          description: f.description || '',
          path: f.path || '',
          enabled: f.enabled !== false,
        })
      )
    }
    conf.endpoints = endpoints
    ds.configuration = encrypted(JSON.stringify(conf))
    await datasourceApi.update(ds)
    ElMessage({ message: t('common.save_success'), type: 'success', showClose: true })
  } catch (e: any) {
    ElMessage({ message: e?.message || 'Save failed', type: 'error', showClose: true })
  } finally {
    editLoading.value = false
  }
}

const addEndpointParam = () => {
  if (!resourceDetail.value) return
  if (!resourceDetail.value.params) resourceDetail.value.params = []
  resourceDetail.value.params.push({
    name: '',
    type: 'string',
    location: 'query',
    required: false,
    default: null,
    description: '',
    enabled: true,
  })
}

const removeEndpointParam = (index: number) => {
  resourceDetail.value?.params?.splice(index, 1)
}

const addResponseField = () => {
  if (!resourceDetail.value) return
  if (!resourceDetail.value.response_fields) resourceDetail.value.response_fields = []
  resourceDetail.value.response_fields.push({
    name: '',
    type: 'string',
    path: '',
    description: '',
    enabled: true,
  })
}

const removeResponseField = (index: number) => {
  resourceDetail.value?.response_fields?.splice(index, 1)
}

const clickTable = async (table: any) => {
  if (activeRelationship.value) return
  loading.value = true
  currentTable.value = table
  fieldList.value = []
  pageInfo.total = 0
  previewData.value = []
  resourceDetail.value = null
  testResult.value = null
  apiParamValues.value = {}
  showRawResponse.value = []

  if (isApiDs.value) {
    // API: load structured resource (endpoint) detail by ds_id + table_name
    try {
      const detail: any = await datasourceApi.resourceDetail(props.info.id, {
        table_name: table.table_name,
      })
      resourceDetail.value = detail
      // Initialize param values from defaults / examples
      if (detail?.params) {
        const vals: Record<string, any> = {}
        detail.params.forEach((p: any) => {
          if (p.default != null && p.default !== '') {
            vals[p.name] = p.default
          } else if (p.example != null && p.example !== '') {
            vals[p.name] = p.example
          }
        })
        apiParamValues.value = vals
      }
    } catch (e: any) {
      console.error('Failed to load resource detail:', e)
    }
    loading.value = false
  } else {
    // SQL: existing logic
    datasourceApi
      .fieldList(table.id)
      .then((res) => {
        fieldList.value = res
        pageInfo.total = res.length
        pageInfo.currentPage = 1
        fieldName.value = ''
        datasourceApi.previewData(props.info.id, buildData()).then((res) => {
          previewData.value = res
        })
      })
      .finally(() => {
        loading.value = false
      })
  }
}

const closeTable = () => {
  tableDialog.value = false
}

const executeTest = async () => {
  if (!currentTable.value?.table_name) return
  testLoading.value = true
  testResult.value = null
  try {
    const res: any = await datasourceApi.testResource(props.info.id, {
      table_name: currentTable.value.table_name,
      params: apiParamValues.value,
    })
    testResult.value = res
    if (res?.projected_data) {
      previewData.value = {
        fields: res.projected_fields || [],
        data: res.projected_data || [],
      }
    } else {
      previewData.value = { fields: [], data: [] }
    }
  } catch (e: any) {
    testResult.value = { error: e?.message || 'Request failed', is_success: false }
  } finally {
    testLoading.value = false
  }
}
const editTable = () => {
  tableComment.value = currentTable.value.custom_comment
  tableDialog.value = true
}
const changeChecked = () => {
  datasourceApi.saveTable(currentTable.value).then(() => {
    ElMessage({
      message: t('common.save_success'),
      type: 'success',
      showClose: true,
    })
  })
}
const saveTable = () => {
  currentTable.value.custom_comment = tableComment.value
  datasourceApi.saveTable(currentTable.value).then(() => {
    closeTable()
    ElMessage({
      message: t('common.save_success'),
      type: 'success',
      showClose: true,
    })
  })
}
const closeField = () => {
  fieldDialog.value = false
}

const refresh = () => {
  emits('refresh')
  datasourceApi.tableList(props.info.id).then((res) => {
    tableList.value = res
    if (!currentTable.value.table_name) return
    const nameArr = tableList.value.map((ele: any) => ele.table_name)
    if (!nameArr.includes(currentTable.value.table_name)) {
      currentTable.value = {}
    }
  })
}

const saveField = () => {
  currentField.value.custom_comment = fieldComment.value
  datasourceApi.saveField(currentField.value).then(() => {
    closeField()
    ElMessage({
      message: t('common.save_success'),
      type: 'success',
      showClose: true,
    })
  })
}

const editField = (row: any) => {
  currentField.value = row
  fieldComment.value = currentField.value.custom_comment
  fieldDialog.value = true
}

const changeStatus = (row: any) => {
  currentField.value = row
  datasourceApi.saveField(currentField.value).then(() => {
    closeField()
    ElMessage({
      message: t('common.save_success'),
      type: 'success',
      showClose: true,
    })
  })
}

const syncFields = () => {
  loading.value = true
  datasourceApi
    .syncFields(currentTable.value.id)
    .then(() => {
      btnSelectClick('d')
      ElMessage.success(t('ds.sync_fields_success'))
      loading.value = false
    })
    .catch(() => {
      loading.value = false
      ElMessage.warning(t('ds.sync_fields_failed'))
    })
}

function downloadTemplate() {
  datasourceApi
    .exportDsSchema(props.info.id)
    .then((res) => {
      const blob = new Blob([res], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = props.info.name + '.xlsx'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    })
    .catch(async (error) => {
      if (error.response) {
        try {
          let text = await error.response.data.text()
          try {
            text = JSON.parse(text)
          } finally {
            ElMessage({
              message: text,
              type: 'error',
              showClose: true,
            })
          }
        } catch (e) {
          console.error('Error processing error response:', e)
        }
      } else {
        console.error('Other error:', error)
        ElMessage({
          message: error,
          type: 'error',
          showClose: true,
        })
      }
    })
}

const emits = defineEmits(['back', 'refresh'])
const back = () => {
  emits('back')
}

const renderHeader = ({ column }: any) => {
  //创建一个元素用于存放表头信息
  const span = document.createElement('span')
  // 将表头信息渲染到元素上
  span.innerText = column.label
  // 在界面中添加该元素
  document.body.appendChild(span)
  //获取该元素的宽度（包含内外边距等信息）
  const spanWidth = span.getBoundingClientRect().width + 20 //渲染后的 div 内左右 padding 都是 10，所以 +20
  //判断是否小于element的最小宽度，两者取最大值
  column.minWidth = column.minWidth > spanWidth ? column.minWidth : spanWidth
  // 计算完成后，删除该元素
  document.body.removeChild(span)
  return column.label
}
const fieldNameSearch = debounce(() => {
  pageInfo.currentPage = 1
  pageInfo.total = fieldListTotalComputed.value.length
}, 100)
const fieldName = ref('')
const btnSelectClick = (val: any) => {
  btnSelect.value = val
  loading.value = true

  if (val === 'd') {
    datasourceApi
      .fieldList(currentTable.value.id, { fieldName: '' })
      .then((res) => {
        fieldList.value = res
        pageInfo.total = res.length
        pageInfo.currentPage = 1
        fieldName.value = ''
      })
      .finally(() => {
        loading.value = false
      })
  } else {
    datasourceApi
      .previewData(props.info.id, buildData())
      .then((res) => {
        previewData.value = res
      })
      .finally(() => {
        loading.value = false
      })
  }
}
</script>

<template>
  <div class="data-table no-padding">
    <div class="info">
      <el-button text @click="back">{{ $t('ds.title') }}</el-button>
      <el-icon size="12">
        <icon_right_outlined></icon_right_outlined>
      </el-icon>
      <div class="name">{{ info.name }}</div>
      <div v-if="ds?.type !== 'api'" class="export-remark">
        <el-button style="margin-right: 12px" secondary @click="downloadTemplate">
          <template #icon>
            <icon_import_outlined></icon_import_outlined>
          </template>
          {{ $t('parameter.export_notes') }}
        </el-button>
        <UploaderRemark
          :upload-path="`/datasource/uploadDsSchema/${info.id}`"
          @upload-finished="init"
        ></UploaderRemark>
      </div>
    </div>
    <div class="content">
      <div class="side-list">
        <div class="select-table_top">
          {{ ds?.type === 'api' ? $t('ds.form.endpoints') : $t('ds.tables') }}

          <el-tooltip
            v-if="ds?.type !== 'api'"
            effect="dark"
            offset="10"
            :content="$t('ds.form.choose_tables')"
            placement="top"
          >
            <el-button style="margin-right: -4px" text @click="handleSelectTableList">
              <el-icon size="18">
                <icon_form_outlined></icon_form_outlined>
              </el-icon>
            </el-button>
          </el-tooltip>
        </div>
        <el-input
          v-model="keywords"
          clearable
          style="width: 232px"
          :placeholder="$t('datasource.search')"
        >
          <template #prefix>
            <el-icon>
              <icon_searchOutline_outlined class="svg-icon" />
            </el-icon>
          </template>
        </el-input>

        <div v-loading="initLoading" class="list-content">
          <el-scrollbar v-if="tableListWithSearch.length">
            <div
              v-for="ele in tableListWithSearch"
              :key="ele.table_name"
              :draggable="activeRelationship && !tableName.includes(ele.id)"
              class="model"
              :class="[
                currentTable.table_name === ele.table_name && 'isActive',
                tableName.includes(ele.id) && activeRelationship && 'disabled-table',
              ]"
              :title="ele.table_name"
              @dragstart="($event: any) => singleDragStartD($event, ele)"
              @dragend="singleDragEnd"
              @click="clickTable(ele)"
            >
              <el-icon size="16">
                <icon_form_outlined></icon_form_outlined>
              </el-icon>
              <span class="name">{{ ele.table_name }}</span>
            </div>
          </el-scrollbar>
          <EmptyBackground
            v-if="!!keywords && !tableListWithSearch.length"
            :description="$t('datasource.relevant_content_found')"
            img-type="tree"
            style="width: 100%"
          />
          <div v-else-if="!initLoading && !tableListWithSearch.length" class="no-data">
            <div class="no-data-msg">
              <div>
                {{
                  ds?.type === 'api' ? $t('ds.form.endpoints_empty') : $t('datasource.no_table')
                }}
              </div>
              <el-button
                v-if="ds?.type !== 'api'"
                type="primary"
                link
                @click="handleSelectTableList"
              >
                {{ $t('datasource.go_add') }}
              </el-button>
            </div>
          </div>
        </div>
        <div v-if="ds?.type !== 'api'" class="table-relationship">
          <div :class="activeRelationship && 'active'" class="btn" @click="handleRelationship">
            <el-icon size="16">
              <icon_mindnote_outlined></icon_mindnote_outlined>
            </el-icon>
            {{ t('training.table_relationship_management') }}
          </div>
        </div>
      </div>

      <div v-if="activeRelationship" class="relationship-content">
        <div class="title">{{ t('training.table_relationship_management') }}</div>
        <div class="content">
          <TableRelationship
            :id="info.id"
            :dragging="isDrag"
            @get-table-name="getTableName"
          ></TableRelationship>
        </div>
      </div>

      <div
        v-if="currentTable.table_name && !activeRelationship"
        v-loading="loading"
        class="info-table"
      >
        <div class="table-name">
          <div class="name">
            {{ currentTable.table_name }}
            <div
              style="
                display: inline-flex;
                align-items: center;
                margin-left: 30px;
                font-size: 14px;
                font-weight: 400;
              "
            >
              <el-switch
                v-model="currentTable.checked"
                @change="changeChecked"
                size="small"
                style="margin-right: 8px"
              />

              {{ currentTable.checked ? t('user.disable') : t('user.enable') }}
            </div>
          </div>
          <div class="notes">
            {{ $t('about.remark') }}:
            <span :title="currentTable.custom_comment" class="field-notes">{{
              currentTable.custom_comment || '-'
            }}</span>

            <el-tooltip :offset="14" effect="dark" :content="$t('datasource.edit')" placement="top">
              <el-icon style="margin-left: 8px; cursor: pointer" size="16" @click="editTable">
                <edit></edit>
              </el-icon>
            </el-tooltip>
          </div>
        </div>

        <div class="table-content">
          <div class="btn-select">
            <el-button
              :class="[btnSelect === 'd' && 'is-active']"
              text
              @click="btnSelectClick('d')"
            >
              {{ t('ds.table_schema') }}
            </el-button>
            <el-button
              :class="[btnSelect === 'q' && 'is-active']"
              text
              @click="btnSelectClick('q')"
            >
              {{ t('ds.preview') }}
            </el-button>
          </div>
          <div v-if="btnSelect === 'd'" class="field-name">
            <el-input
              v-model="fieldName"
              style="width: 240px"
              :placeholder="t('dashboard.search')"
              autocomplete="off"
              clearable
              @input="fieldNameSearch"
            />
            <el-button
              v-if="ds.type !== 'excel' && ds.type !== 'api'"
              :icon="Refresh"
              secondary
              style="margin-left: 12px"
              @click="syncFields()"
            >
              {{ t('ds.sync_fields') }}
            </el-button>
          </div>

          <div
            v-if="!loading"
            class="preview-or-schema"
            :class="btnSelect === 'q' && 'overflow-preview'"
          >
            <!-- API: Schema tab (resource detail from protocol) -->
            <template v-if="isApiDs && resourceDetail && btnSelect === 'd'">
              <div class="api-endpoint-detail">
                <div class="api-detail-header">
                  <el-tag :type="methodTagType(resourceDetail.method)" size="small" style="margin-right: 8px">
                    {{ resourceDetail.method }}
                  </el-tag>
                  <span class="api-detail-path">{{ resourceDetail.path }}</span>
                  <span v-if="resourceDetail.description" class="api-detail-desc">{{ resourceDetail.description }}</span>
                  <el-button
                    type="primary"
                    size="small"
                    style="margin-left: auto"
                    :loading="editLoading"
                    @click="saveEndpointConfig"
                  >
                    {{ t('common.save') }}
                  </el-button>
                </div>

                <div class="api-detail-section">
                  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px">
                    <h4 style="margin: 0">{{ t('ds.endpoint.input_params') }}</h4>
                    <el-button text type="primary" size="small" @click="addEndpointParam">
                      + {{ t('ds.form.add_param') }}
                    </el-button>
                  </div>
                  <el-table
                    v-if="resourceDetail.params?.length"
                    :data="resourceDetail.params"
                    border
                    size="small"
                    style="width: 100%"
                    :row-class-name="({ row }: any) => row.enabled === false ? 'is-disabled-row' : ''"
                  >
                    <el-table-column width="40" align="center">
                      <template #default="{ row }">
                        <el-checkbox v-model="row.enabled" />
                      </template>
                    </el-table-column>
                    <el-table-column :label="t('ds.endpoint.param_name')" min-width="120">
                      <template #default="{ row }">
                        <el-input v-model="row.name" size="small" :disabled="row.enabled === false" />
                      </template>
                    </el-table-column>
                    <el-table-column label="Type" width="100">
                      <template #default="{ row }">
                        <el-select v-model="row.type" size="small" :disabled="row.enabled === false">
                          <el-option label="string" value="string" />
                          <el-option label="number" value="number" />
                          <el-option label="boolean" value="boolean" />
                          <el-option label="integer" value="integer" />
                        </el-select>
                      </template>
                    </el-table-column>
                    <el-table-column label="Location" width="90">
                      <template #default="{ row }">
                        <el-select v-model="row.location" size="small" :disabled="row.enabled === false">
                          <el-option label="query" value="query" />
                          <el-option label="path" value="path" />
                          <el-option label="header" value="header" />
                          <el-option label="body" value="body" />
                        </el-select>
                      </template>
                    </el-table-column>
                    <el-table-column :label="t('ds.endpoint.required')" width="70" align="center">
                      <template #default="{ row }">
                        <el-checkbox v-model="row.required" :disabled="row.enabled === false" />
                      </template>
                    </el-table-column>
                    <el-table-column :label="t('ds.endpoint.default')" min-width="100">
                      <template #default="{ row }">
                        <el-input v-model="row.default" size="small" :disabled="row.enabled === false" />
                      </template>
                    </el-table-column>
                    <el-table-column :label="t('ds.endpoint.description')" min-width="140">
                      <template #default="{ row }">
                        <el-input v-model="row.description" size="small" :disabled="row.enabled === false" />
                      </template>
                    </el-table-column>
                    <el-table-column width="50" align="center">
                      <template #default="{ $index }">
                        <el-button text type="danger" size="small" @click="removeEndpointParam($index)">
                          <el-icon size="14"><IconOpeDelete /></el-icon>
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                  <div v-else class="api-detail-empty">
                    {{ t('ds.form.swagger_no_params') }}
                  </div>
                </div>

                <div class="api-detail-section">
                  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px">
                    <h4 style="margin: 0">{{ t('ds.endpoint.output_fields') }}</h4>
                    <el-button text type="primary" size="small" @click="addResponseField">
                      + {{ t('ds.form.add_field') }}
                    </el-button>
                  </div>
                  <el-table
                    v-if="resourceDetail.response_fields?.length"
                    :data="resourceDetail.response_fields"
                    border
                    size="small"
                    style="width: 100%"
                    :row-class-name="({ row }: any) => row.enabled === false ? 'is-disabled-row' : ''"
                  >
                    <el-table-column width="40" align="center">
                      <template #default="{ row }">
                        <el-checkbox v-model="row.enabled" />
                      </template>
                    </el-table-column>
                    <el-table-column :label="t('ds.endpoint.field_name')" min-width="120">
                      <template #default="{ row }">
                        <el-input v-model="row.name" size="small" :disabled="row.enabled === false" />
                      </template>
                    </el-table-column>
                    <el-table-column label="Type" width="100">
                      <template #default="{ row }">
                        <el-select v-model="row.type" size="small" :disabled="row.enabled === false">
                          <el-option label="string" value="string" />
                          <el-option label="number" value="number" />
                          <el-option label="boolean" value="boolean" />
                          <el-option label="integer" value="integer" />
                        </el-select>
                      </template>
                    </el-table-column>
                    <el-table-column label="Path" min-width="120">
                      <template #default="{ row }">
                        <el-input v-model="row.path" size="small" :disabled="row.enabled === false" />
                      </template>
                    </el-table-column>
                    <el-table-column :label="t('ds.endpoint.description')" min-width="140">
                      <template #default="{ row }">
                        <el-input v-model="row.description" size="small" :disabled="row.enabled === false" />
                      </template>
                    </el-table-column>
                    <el-table-column width="50" align="center">
                      <template #default="{ $index }">
                        <el-button text type="danger" size="small" @click="removeResponseField($index)">
                          <el-icon size="14"><IconOpeDelete /></el-icon>
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                  <div v-else class="api-detail-empty">
                    {{ t('ds.form.swagger_no_fields') }}
                  </div>
                </div>

                <div
                  v-if="resourceDetail.data_path || resourceDetail.code_path || resourceDetail.total_path"
                  class="api-detail-section"
                >
                  <h4>{{ t('ds.endpoint.extraction_config') }}</h4>
                  <el-descriptions :column="2" border size="small">
                    <el-descriptions-item v-if="resourceDetail.data_path" :label="t('ds.endpoint.data_path')">
                      {{ resourceDetail.data_path }}
                    </el-descriptions-item>
                    <el-descriptions-item v-if="resourceDetail.code_path" :label="t('ds.endpoint.code_path')">
                      {{ resourceDetail.code_path }}
                      <template v-if="resourceDetail.code_success_value != null">
                        = {{ resourceDetail.code_success_value }}
                      </template>
                    </el-descriptions-item>
                    <el-descriptions-item v-if="resourceDetail.total_path" :label="t('ds.endpoint.total_path')">
                      {{ resourceDetail.total_path }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </div>
            </template>

            <!-- API: Preview tab (params form + test_extract pipeline) -->
            <template v-else-if="isApiDs && resourceDetail && btnSelect === 'q'">
              <div class="api-preview-panel">
                <div v-if="resourceDetail.params?.length" class="api-params-form">
                  <h4>{{ t('ds.endpoint.request_params') }}</h4>
                  <el-form label-position="top" size="small">
                    <el-form-item
                      v-for="p in resourceDetail.params"
                      :key="p.name"
                      :label="p.name"
                      :required="p.required"
                      style="margin-bottom: 12px"
                    >
                      <template #label>
                        <span>{{ p.name }}</span>
                        <el-tag v-if="p.location" size="small" type="info" style="margin-left: 6px">{{ p.location }}</el-tag>
                        <span v-if="p.description" style="color: #8f959e; font-size: 12px; margin-left: 6px">{{ p.description }}</span>
                      </template>
                      <el-input
                        v-model="apiParamValues[p.name]"
                        :placeholder="p.description || p.type"
                        :type="p.type === 'integer' || p.type === 'number' ? 'number' : 'text'"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-form>
                  <el-button type="primary" :loading="testLoading" @click="executeTest">
                    {{ t('ds.endpoint.execute') }}
                  </el-button>
                </div>
                <div v-else class="api-params-form">
                  <el-button type="primary" :loading="testLoading" @click="executeTest">
                    {{ t('ds.endpoint.execute') }}
                  </el-button>
                </div>

                <div v-if="testResult?.error" style="margin-top: 16px">
                  <el-alert :title="testResult.error" type="error" show-icon :closable="false" />
                </div>

                <template v-if="testResult && !testResult.error">
                  <!-- Extraction pipeline info (same core as execute) -->
                  <div class="api-pipeline-info" style="margin-top: 16px">
                    <el-descriptions :column="3" border size="small">
                      <el-descriptions-item :label="t('ds.endpoint.is_success')">
                        <el-tag :type="testResult.is_success !== false ? 'success' : 'danger'" size="small">
                          {{ testResult.is_success !== false ? 'OK' : 'FAIL' }}
                        </el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item v-if="testResult.http_status != null" :label="t('ds.endpoint.http_status')">
                        <el-tag :type="testResult.http_status < 400 ? 'success' : 'danger'" size="small">
                          {{ testResult.http_status }}
                        </el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item v-if="testResult.code_value != null" :label="t('ds.endpoint.code_value')">
                        <el-tag :type="testResult.is_success !== false ? 'success' : 'danger'" size="small">
                          {{ testResult.code_value }}
                          <template v-if="testResult.code_success_value != null">
                            / {{ testResult.code_success_value }}
                          </template>
                        </el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item v-if="testResult.total != null" :label="t('ds.endpoint.total')">
                        {{ testResult.total }}
                      </el-descriptions-item>
                      <el-descriptions-item :label="t('ds.endpoint.extracted_count')">
                        {{ testResult.extracted_rows?.length || 0 }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>

                  <!-- Raw response (collapsible) -->
                  <div style="margin-top: 12px">
                    <el-collapse v-model="showRawResponse">
                      <el-collapse-item :title="t('ds.endpoint.raw_response')" name="raw">
                        <pre class="api-raw-response">{{ JSON.stringify(testResult.raw_response, null, 2) }}</pre>
                      </el-collapse-item>
                    </el-collapse>
                  </div>

                  <!-- Projected data table -->
                  <div v-if="previewData.data?.length" style="margin-top: 12px">
                    <h4>{{ t('ds.endpoint.result_data') }} ({{ previewData.data.length }})</h4>
                    <el-table :data="previewData.data" border size="small" style="width: 100%" max-height="400">
                      <el-table-column
                        v-for="c in previewData.fields"
                        :key="c"
                        :prop="c"
                        :label="c"
                        min-width="120"
                        show-overflow-tooltip
                      />
                    </el-table>
                  </div>
                </template>
              </div>
            </template>

            <!-- SQL / non-API: existing schema tab -->
            <div v-else-if="btnSelect === 'd'" class="table-content_preview">
              <el-table
                row-class-name="hover-icon_edit"
                :data="fieldListComputed"
                style="width: 100%"
              >
                <el-table-column
                  prop="field_name"
                  :label="t('datasource.field_name')"
                  width="180"
                />
                <el-table-column
                  prop="field_type"
                  :label="t('datasource.field_type')"
                  width="180"
                />
                <el-table-column
                  prop="field_comment"
                  :label="t('datasource.field_original_notes')"
                />
                <el-table-column :label="t('datasource.field_notes_1')">
                  <template #default="scope">
                    <div class="field-comment">
                      <span :title="scope.row.custom_comment" class="notes-in_table">{{
                        scope.row.custom_comment
                      }}</span>
                      <el-tooltip
                        :offset="14"
                        effect="dark"
                        :content="$t('datasource.edit')"
                        placement="top"
                      >
                        <el-icon class="action-btn" size="16" @click="editField(scope.row)">
                          <edit></edit>
                        </el-icon>
                      </el-tooltip>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column :label="t('datasource.enabled_status')" width="180">
                  <template #default="scope">
                    <div style="display: flex; align-items: center">
                      <el-switch
                        v-model="scope.row.checked"
                        size="small"
                        @change="changeStatus(scope.row)"
                      />
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div v-if="pageInfo.total && btnSelect === 'd'" class="pagination-container">
              <el-pagination
                v-model:current-page="pageInfo.currentPage"
                v-model:page-size="pageInfo.pageSize"
                :page-sizes="[10, 20, 30]"
                :background="true"
                layout="total, sizes, prev, pager, next, jumper"
                :total="pageInfo.total"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
            <template v-if="!isApiDs && btnSelect === 'q'">
              <div class="preview-num">
                {{ t('ds.pieces_in_total', { msg: total, ms: showNum }) }}
              </div>
              <div class="table-container">
                <el-table :data="previewData.data" style="width: 100%; height: 100%">
                  <el-table-column
                    v-for="(c, index) in previewData.fields"
                    :key="index"
                    :prop="c"
                    :label="c"
                    min-width="150"
                    :render-header="renderHeader"
                  />
                </el-table>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
  <el-dialog
    v-model="tableDialog"
    :title="t('datasource.table_notes')"
    width="600"
    :destroy-on-close="true"
    :close-on-click-modal="false"
    modal-class="notes-dialog"
    @closed="closeTable"
  >
    <el-input
      v-model="tableComment"
      :placeholder="$t('datasource.please_enter')"
      :autosize="{ minRows: 3.64, maxRows: 11.095 }"
      type="textarea"
      clearable
    />
    <div style="display: flex; justify-content: flex-end; margin-top: 20px">
      <el-button secondary @click="closeTable">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" @click="saveTable">{{ t('common.save') }}</el-button>
    </div>
  </el-dialog>

  <el-dialog
    v-model="fieldDialog"
    :title="t('datasource.field_notes')"
    width="600"
    :destroy-on-close="true"
    :close-on-click-modal="false"
    modal-class="notes-dialog"
    @closed="closeField"
  >
    <el-input
      v-model="fieldComment"
      :placeholder="$t('datasource.please_enter')"
      :autosize="{ minRows: 3.64, maxRows: 11.095 }"
      clearable
      type="textarea"
    />
    <div style="display: flex; justify-content: flex-end; margin-top: 20px">
      <el-button secondary @click="closeField">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" @click="saveField">{{ t('common.save') }}</el-button>
    </div>
  </el-dialog>
  <ParamsForm ref="paramsFormRef" @refresh="refresh"></ParamsForm>
</template>

<style lang="less" scoped>
.data-table {
  height: 100%;
  .info {
    height: 56px;
    width: 100%;
    padding-left: 20px;
    display: flex;
    align-items: center;
    font-family: PingFang SC;
    font-weight: 400;
    font-size: 14px;
    line-height: 22px;
    color: #646a73;
    border-bottom: 1px solid #1f232926;
    position: relative;

    .ed-button.is-text {
      height: 22px;
      line-height: 22px;
      color: #646a73;

      &:hover {
        background: var(--ed-color-primary-1a, #1cba901a);
        color: var(--ed-color-primary);
      }
      &:active {
        color: var(--ed-color-primary-dark-2);
        background: var(--ed-color-primary-33, #1cba9033);
      }
    }

    .export-remark {
      position: absolute;
      right: 24px;
      top: 12px;
    }

    .name {
      color: #1f2329;
      margin-left: 4px;
    }
  }
  .content {
    height: calc(100% - 56px);
    position: relative;
    .side-list {
      width: 280px;
      padding: 8px 16px;
      height: 100%;
      border-right: 1px solid #1f232926;
      .table-relationship {
        height: 56px;
        width: 100%;
        display: flex;
        align-items: center;
        margin-top: 20px;
        position: relative;

        &::after {
          content: '';
          width: calc(100% + 32px);
          position: absolute;
          left: -16px;
          background-color: #1f232926;
          top: 0;
          height: 1px;
        }

        .btn {
          width: 248px;
          height: 32px;
          cursor: pointer;
          border-radius: 6px;
          display: flex;
          align-items: center;
          padding-left: 8px;
          .ed-icon {
            color: #646a73;
            margin-right: 8px;
          }

          &.active {
            color: var(--ed-color-primary);
            .ed-icon {
              color: var(--ed-color-primary);
            }
            background-color: var(--ed-color-primary-1a);
          }
        }
      }
      .select-table_top {
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px;
        font-weight: 500;

        .ed-icon {
          cursor: pointer;
          color: var(--ed-color-primary);
        }
      }

      .ed-input {
        margin: 8px;
      }

      .list-content {
        height: calc(100% - 156px);
        .no-result {
          margin-top: 72px;
          font-weight: 400;
          font-size: 14px;
          line-height: 22px;
          text-align: center;
          color: #646a73;
        }
        .model {
          width: 100%;
          height: 32px;
          display: flex;
          align-items: center;
          padding-left: 8px;
          border-radius: 6px;
          cursor: pointer;

          &:not(:last-child) {
            margin-bottom: 2px;
          }

          &.disabled-table {
            background: #dee0e3 !important;
            color: #646a73;
            cursor: not-allowed;
          }

          .name {
            margin-left: 8px;
            font-weight: 500;
            font-size: 14px;
            line-height: 22px;
            max-width: 80%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          &:hover {
            background: #1f23291a;
          }

          &.isActive {
            background: var(--ed-color-primary-1a, #1cba901a);
            color: var(--ed-color-primary);
          }
        }
      }

      .no-data {
        height: 100%;
        text-align: center;
        display: flex;
        align-items: center;
        width: 100%;
        .no-data-msg {
          display: inline;
          width: 100%;
          color: var(--ed-text-color-secondary);
          font-size: var(--ed-font-size-base);
        }
      }
    }
    .relationship-content {
      position: absolute;
      right: 0;
      top: 0;
      width: calc(100% - 280px);
      height: 100%;

      .content {
        height: calc(100% - 56px);
        width: 100%;
      }

      .title {
        height: 56px;
        padding-left: 24px;
        line-height: 56px;
        font-weight: 500;
        font-size: 16px;
        border-bottom: 1px solid #1f232926;
      }
    }
    .info-table {
      position: absolute;
      right: 0;
      top: 0;
      width: calc(100% - 280px);
      height: 100%;
      .table-name {
        height: 80px;
        padding: 16px 0 0 24px;
        border-bottom: 1px solid #1f232926;

        .name {
          font-weight: 500;
          font-size: 16px;
          line-height: 24px;
          display: flex;
          align-items: center;
        }

        .ed-icon {
          position: relative;
          cursor: pointer;
          margin-top: 4px;
          margin-left: 8px;

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

        .notes {
          font-weight: 400;
          font-size: 14px;
          line-height: 22px;
          color: #646a73;
          display: flex;
          align-items: center;

          .field-notes {
            display: inline-block;
            max-width: calc(100% - 75px);
            text-overflow: ellipsis;
            white-space: nowrap;
            overflow: hidden;
          }
        }
      }

      .table-content {
        padding: 16px 24px;
        height: calc(100% - 80px);
        position: relative;

        .field-name {
          position: absolute;
          right: 24px;
          top: 16px;
          display: flex;
        }

        .btn-select {
          height: 32px;
          padding-left: 4px;
          padding-right: 4px;
          display: inline-flex;
          background: #ffffff;
          align-items: center;
          border: 1px solid #d0d3d6;
          border-radius: 6px;

          .is-active {
            background: var(--ed-color-primary-1a, #1cba901a);
          }

          .ed-button:not(.is-active) {
            color: #1f2329;
          }
          .ed-button.is-text {
            height: 24px;
            width: auto;
            padding: 0 8px;
            line-height: 24px;
          }
          .ed-button + .ed-button {
            margin-left: 4px;
          }
        }

        .preview-or-schema {
          margin-top: 16px;
          height: calc(100% - 50px);

          .table-content_preview {
            max-height: calc(100% - 50px);
            overflow-y: auto;
            margin-bottom: 16px;
          }

          .pagination-container {
            display: flex;
            justify-content: flex-end;
          }

          .hover-icon_edit:hover {
            .ed-icon {
              display: block;
            }
          }

          .field-comment {
            display: flex;
            align-items: center;
            min-height: 24px;
            .notes-in_table {
              max-width: 100%;
              display: -webkit-box;
              max-height: 66px;
              -webkit-box-orient: vertical;
              -webkit-line-clamp: 3; /* 限制行数为3 */
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .ed-icon {
              position: relative;
              cursor: pointer;
              margin-left: 8px;
              display: none;
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

          .preview-num {
            margin: 12px 0;
            font-weight: 400;
            font-size: 14px;
            line-height: 22px;
            color: #646a73;
          }

          .table-container {
            width: 100%;
            height: calc(100% - 46px);
          }
        }
      }
    }
  }
}

.api-endpoint-detail {
  padding: 16px;

  .api-detail-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #dee0e3;
  }

  .api-detail-path {
    font-size: 15px;
    font-weight: 500;
    color: #1f2329;
    font-family: monospace;
  }

  .api-detail-desc {
    font-size: 13px;
    color: #8f959e;
    margin-left: 12px;
  }

  .api-detail-section {
    margin-bottom: 20px;

    h4 {
      font-size: 14px;
      font-weight: 500;
      color: #1f2329;
      margin: 0 0 10px 0;
    }
  }

  .api-detail-empty {
    font-size: 13px;
    color: #8f959e;
    padding: 12px 0;
  }

  :deep(.is-disabled-row) {
    opacity: 0.45;
  }
}

.api-preview-panel {
  padding: 16px;

  .api-params-form {
    margin-bottom: 16px;

    h4 {
      font-size: 14px;
      font-weight: 500;
      color: #1f2329;
      margin: 0 0 12px 0;
    }
  }
}

.api-raw-response {
  background: #f5f6f7;
  border-radius: 4px;
  padding: 12px;
  font-size: 12px;
  line-height: 18px;
  max-height: 300px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}
</style>

<style lang="less">
.notes-dialog {
  .ed-textarea__inner {
    line-height: 22px;
  }
}
</style>
