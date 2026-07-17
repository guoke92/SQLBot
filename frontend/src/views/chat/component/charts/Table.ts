import { BaseChart, type ChartAxis, type ChartData } from '@/views/chat/component/BaseChart.ts'
import {
  copyToClipboard,
  type S2DataConfig,
  S2Event,
  type S2MountContainer,
  type S2Options,
  type SortMethod,
  TableSheet,
  type SortFuncParam,
} from '@antv/s2'
import { debounce, filter, includes } from 'lodash-es'
import { i18n } from '@/i18n'
import { formatNumber } from '@/views/chat/component/charts/utils.ts'
import '@antv/s2/dist/s2.min.css'

const { t } = i18n.global

const createSmartSortFunc = (sortMethod: string) => {
  const compareNumericString = (a: string, b: string): number => {
    const isNegA = a.startsWith('-')
    const isNegB = b.startsWith('-')

    // 负数 < 正数
    if (isNegA && !isNegB) return -1
    if (!isNegA && isNegB) return 1

    const [intA, decA = ''] = isNegA ? a.slice(1).split('.') : a.split('.')
    const [intB, decB = ''] = isNegB ? b.slice(1).split('.') : b.split('.')

    // 都是正数
    if (!isNegA && !isNegB) {
      if (intA.length !== intB.length) return intA.length - intB.length
      const intCmp = intA.localeCompare(intB)
      if (intCmp !== 0) return intCmp
      if (decA && decB) return decA.localeCompare(decB)
      return decA ? 1 : decB ? -1 : 0
    }

    // 都是负数：绝对值大的实际值小，比较结果取反
    if (intA.length !== intB.length) return -(intA.length - intB.length)
    const intCmp = intA.localeCompare(intB)
    if (intCmp !== 0) return -intCmp
    if (decA && decB) return -decA.localeCompare(decB)
    return decA ? 1 : decB ? -1 : 0
  }

  return (params: SortFuncParam) => {
    const { data, sortFieldId } = params
    if (!data || data.length === 0) return data
    const isAsc = sortMethod.toLowerCase() === 'asc'
    return [...data].sort((a: any, b: any) => {
      const valA = a[sortFieldId],
        valB = b[sortFieldId]
      if (valA == null) return isAsc ? -1 : 1
      if (valB == null) return isAsc ? 1 : -1
      const strA = String(valA),
        strB = String(valB)
      const isNumA = !isNaN(Number(strA)) && strA.trim() !== ''
      const isNumB = !isNaN(Number(strB)) && strB.trim() !== ''
      if (isNumA && !isNumB) return isAsc ? -1 : 1
      if (!isNumA && isNumB) return isAsc ? 1 : -1
      if (isNumA && isNumB) {
        const cmp = compareNumericString(strA, strB)
        return isAsc ? cmp : -cmp
      }
      const cmp = strA.localeCompare(strB)
      return isAsc ? cmp : -cmp
    })
  }
}

export class Table extends BaseChart {
  table?: TableSheet = undefined

  container: S2MountContainer | null = null

  debounceRender: any

  resizeObserver: ResizeObserver

  constructor(id: string) {
    super(id, 'table')
    this.container = document.getElementById(id)

    this.debounceRender = debounce(async (width?: number, height?: number) => {
      if (this.table) {
        this.table.changeSheetSize(width, height)
        await this.table.render(false)
      }
    }, 200)

    this.resizeObserver = new ResizeObserver(([entry] = []) => {
      const [size] = entry.borderBoxSize || []
      this.debounceRender(size.inlineSize, size.blockSize)
    })

    if (this.container?.parentElement) {
      this.resizeObserver.observe(this.container.parentElement)
    }
  }

  init(axis: Array<ChartAxis>, data: Array<ChartData>, formatNumberFields: Array<string>) {
    super.init(
      filter(axis, (a) => !a.hidden), //隐藏多指标的other-info列
      data,
      formatNumberFields
    )

    const s2DataConfig: S2DataConfig = {
      sortParams:
        this.axis?.map((a) => {
          return {
            sortFieldId: a.value,
          }
        }) ?? [],
      fields: {
        columns: this.axis?.map((a) => a.value) ?? [],
      },
      meta:
        this.axis?.map((a) => {
          return {
            field: a.value,
            name: a.name,
            formatter: (value: any) => {
              const formatted = a.formatNumber ? formatNumber(value) : value
              return String(formatted)
            },
          }
        }) ?? [],
      data: this.data,
    }

    const sortState: Record<string, string> = {}

    const handleSortClick = (params: any) => {
      const { meta } = params
      const s2 = meta.spreadsheet
      if (s2 && meta.isLeaf) {
        const fieldId = meta.field
        const currentMethod = sortState[fieldId] || 'none'
        const sortOrder = ['none', 'desc', 'asc']
        const nextMethod = sortOrder[(sortOrder.indexOf(currentMethod) + 1) % sortOrder.length]
        sortState[fieldId] = nextMethod
        if (nextMethod === 'none') {
          s2.emit(S2Event.RANGE_SORT, [{ sortFieldId: fieldId, sortMethod: 'none' as SortMethod }])
        } else {
          s2.emit(S2Event.RANGE_SORT, [
            {
              sortFieldId: fieldId,
              sortMethod: nextMethod as SortMethod,
              sortFunc: createSmartSortFunc(nextMethod),
            },
          ])
        }
        s2.render()
      }
    }

    const createTooltipEl = (text: string) => {
      const container = document.createElement('div')
      container.style.minWidth = '100px'
      container.style.maxWidth = '420px'
      container.style.display = 'flex'
      container.style.alignItems = 'center'
      container.style.padding = '8px 16px'
      container.style.cursor = 'default'
      container.style.color = '#606266'
      container.style.fontSize = '14px'
      container.style.lineHeight = '20px'
      container.style.whiteSpace = 'pre-wrap'
      container.style.wordBreak = 'break-word'
      container.appendChild(document.createTextNode(text))
      return container
    }

    const resolveColHeaderText = (cell: any): string => {
      const meta = cell?.getMeta?.() || {}
      const field = meta.field || meta.valueField || meta.value
      const dataSet = cell?.spreadsheet?.dataSet
      const fieldName =
        (field != null && dataSet?.getFieldName?.(field)) ||
        meta.label ||
        meta.value ||
        meta.fieldValue ||
        field
      return fieldName == null ? '' : String(fieldName)
    }

    // 按表头文案估算列宽，避免中文长表头被固定均分后只剩省略号且无法查看。
    const measureHeaderWidth = (text: string) => {
      let units = 0
      for (const ch of text) {
        units += /[\u0000-\u00ff]/.test(ch) ? 0.55 : 1
      }
      // 表头文字 + 排序图标/内边距；限制上下限避免极窄或占满整表。
      return Math.max(88, Math.min(280, Math.ceil(units * 14 + 40)))
    }
    const colWidthByField: Record<string, number> = {}
    for (const a of this.axis || []) {
      const header = a.name || a.value || ''
      colWidthByField[a.value] = measureHeaderWidth(String(header))
    }

    const s2Options: S2Options = {
      width: 600,
      height: 360,
      showDefaultHeaderActionIcon: false,
      headerActionIcons: [
        {
          icons: ['GlobalDesc'],
          belongsCell: 'colCell',
          displayCondition: (node: any) => node.isLeaf && sortState[node.field] === 'desc',
          onClick: handleSortClick,
        },
        {
          icons: ['GlobalAsc'],
          belongsCell: 'colCell',
          displayCondition: (node: any) => node.isLeaf && sortState[node.field] === 'asc',
          onClick: handleSortClick,
        },
        {
          icons: ['SortDown'],
          belongsCell: 'colCell',
          displayCondition: (node: any) =>
            node.isLeaf && (!sortState[node.field] || sortState[node.field] === 'none'),
          onClick: handleSortClick,
        },
      ],
      style: {
        // compact 按内容给列宽；再配合 widthByField 保证长表头至少放得下主要文案。
        layoutWidthType: 'compact',
        compactMinWidth: 88,
        compactExtraWidth: 28,
        colCell: {
          widthByField: colWidthByField,
        },
      },
      tooltip: {
        // 数据单元格 + 列头：超长时悬停可看全文（S2 仅在 isTextOverflowing 时触发列头 tip）
        operation: {
          sort: true,
        },
        colCell: {
          enable: true,
          content: (cell) => createTooltipEl(resolveColHeaderText(cell)),
        },
        dataCell: {
          enable: true,
          content: (cell) => {
            const meta = cell.getMeta()
            const formattedValue = includes(this.formatNumberFields, meta.valueField)
              ? formatNumber(meta.fieldValue)
              : meta.fieldValue
            return createTooltipEl(String(formattedValue ?? ''))
          },
        },
      },
      // 如果有省略号, 复制到的是完整文本
      interaction: {
        copy: {
          enable: true,
          withFormat: false,
          withHeader: false,
        },
        brushSelection: {
          dataCell: true,
          rowCell: true,
          colCell: true,
        },
      },
      placeholder: {
        cell: '-',
        empty: {
          icon: 'Empty',
          description: 'No Data',
        },
      },
    }

    if (this.container) {
      this.table = new TableSheet(this.container, s2DataConfig, s2Options)
      // right click
      this.table.on(S2Event.GLOBAL_COPIED, (data) => {
        ElMessage.success(t('qa.copied'))
        console.debug('copied: ', data)
      })
      this.table.getCanvasElement().addEventListener('contextmenu', (event) => {
        event.preventDefault()
      })
      this.table.on(S2Event.GLOBAL_CONTEXT_MENU, (event) => copyData(event, this.table))
      // this.table.on(S2Event.RANGE_SORT, (sortParams) => {
      //   console.log('sortParams:', sortParams)
      // })
    }
  }

  render() {
    this.table?.render()
  }

  destroy() {
    this.table?.destroy()
    this.resizeObserver?.disconnect()
  }
}

function copyData(event: any, s2?: TableSheet) {
  event.preventDefault()
  if (!s2) {
    return
  }
  const cells = s2.interaction.getCells()

  if (cells.length == 0) {
    return
  } else if (cells.length == 1) {
    const c = cells[0]
    const cellMeta = s2.facet.getCellMeta(c.rowIndex, c.colIndex)
    if (cellMeta) {
      let value = cellMeta.fieldValue
      if (value === null || value === undefined) {
        value = '-'
      }
      value = value + ''
      copyToClipboard(value).finally(() => {
        ElMessage.success(t('qa.copied'))
        console.debug('copied:', cellMeta.fieldValue)
      })
    }
    return
  } else {
    let currentRowIndex = -1
    let currentRowData: Array<string> = []
    const rowData: Array<string> = []
    for (let i = 0; i < cells.length; i++) {
      const c = cells[i]
      const cellMeta = s2.facet.getCellMeta(c.rowIndex, c.colIndex)
      if (!cellMeta) {
        continue
      }
      if (currentRowIndex == -1) {
        currentRowIndex = c.rowIndex
      }
      if (c.rowIndex !== currentRowIndex) {
        rowData.push(currentRowData.join('\t'))
        currentRowData = []
        currentRowIndex = c.rowIndex
      }
      let value = cellMeta.fieldValue
      if (value === null || value === undefined) {
        value = '-'
      }
      value = value + ''
      currentRowData.push(value)
    }
    rowData.push(currentRowData.join('\t'))
    const finalValue = rowData.join('\n')
    copyToClipboard(finalValue).finally(() => {
      ElMessage.success(t('qa.copied'))
      console.debug('copied:\n', finalValue)
    })
  }
}
