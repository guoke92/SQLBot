/**
 * 为数值添加千分符，保持原有小数位数不变
 * 纯字符串处理，避免精度丢失
 * 支持：正负整数、小数、字符串格式的数值
 */
function formatNumber(value) {
  if (value === null || value === undefined || value === '') {
    return value
  }

  let str
  if (typeof value === 'string') {
    str = value.trim()
  } else if (typeof value === 'number') {
    str = String(value)
  } else {
    return value
  }

  const match = str.match(/^([+-])?(\d+)(\.(\d+))?$/)
  if (!match) {
    return value
  }

  const sign = match[1] || ''
  const intPart = match[2]
  const decPart = match[3] || ''

  const formattedInt = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',')

  return sign + formattedInt + decPart
}

function getAxesWithFilter(axes) {
  const groups = {
    x: [],
    y: [],
    series: [],
    multiQuota: [],
    multiQuotaName: undefined,
    multiMetricWithSeries: false,
  }

  // 分组
  axes.forEach((axis) => {
    if (axis.type === 'x') groups.x.push(axis)
    else if (axis.type === 'y') groups.y.push(axis)
    else if (axis.type === 'series') groups.series.push(axis)
    else if (axis.type === 'other-info') groups.multiQuotaName = axis.value
  })

  // 应用过滤规则
  if (groups.series.length > 0) {
    if (groups.y.length > 1) {
      groups.multiMetricWithSeries = true
    } else {
      groups.y = groups.y.slice(0, 1)
    }
  } else {
    const multiQuotaY = groups.y.filter((item) => item['multi-quota'] === true)
    groups.multiQuota = multiQuotaY.map((item) => item.value)
    if (multiQuotaY.length > 0) {
      groups.y = multiQuotaY
    }
  }

  return groups
}

function processMultiMetricWithSeries(x, y, series, data) {
  const list = []
  const seriesColumn = series[0]
  for (const datum of data) {
    const seriesValue = String(datum[seriesColumn.value] ?? '')
    for (const metric of y) {
      const item = {}
      for (const xAxis of x) {
        item[xAxis.value] = datum[xAxis.value]
      }
      item.sqlbot_metric_val = datum[metric.value]
      item.sqlbot_combined_series = `${seriesValue}-${metric.name || metric.value}`
      item.sqlbot_axis_format = metric.formatNumber
      list.push(item)
    }
  }
  return {
    data: list,
    y: [{ name: 'sqlbot_metric_val', value: 'sqlbot_metric_val', type: 'y' }],
    series: [
      {
        name: seriesColumn.name,
        value: 'sqlbot_combined_series',
        type: 'series',
      },
    ],
  }
}

function processMultiQuotaData(
  x,
  y,
  multiQuota,
  multiQuotaName = 'sqlbot_auto_series',
  data,
) {
  const _list = []
  const _map = {}
  y.forEach((axis) => {
    _map[axis.value] = axis.name
  })
  for (const datum of data) {
    multiQuota.forEach((quota) => {
      const _data = {}
      for (const xAxis of x) {
        _data[xAxis.value] = datum[xAxis.value]
      }
      _data['sqlbot_auto_quota'] = datum[quota]
      _data['sqlbot_auto_series'] = _map[quota]
      _list.push(_data)
    })
  }

  return {
    data: _list,
    y: [{ name: 'sqlbot_auto_quota', value: 'sqlbot_auto_quota', type: 'y' }],
    series: [{ name: multiQuotaName, value: 'sqlbot_auto_series', type: 'series' }],
  }
}

function checkIsPercent(valueAxes, data) {
  const result = {
    isPercent: false,
    data: [],
  }

  // 深拷贝原始数据
  for (let i = 0; i < data.length; i++) {
    result.data.push({ ...data[i] })
  }

  // 检查是否有任何一个轴包含百分比数据
  for (const valueAxis of valueAxes) {
    const notEmptyData = data.filter(
      (d) =>
        d &&
        d[valueAxis.value] !== null &&
        d[valueAxis.value] !== undefined &&
        d[valueAxis.value] !== '' &&
        d[valueAxis.value] !== 0 &&
        d[valueAxis.value] !== '0',
    )

    if (notEmptyData.length > 0) {
      const v = notEmptyData[0][valueAxis.value] + ''
      if (v.trim().endsWith('%')) {
        result.isPercent = true
        break // 找到一个百分比轴就结束检查
      }
    }
  }

  // 如果发现任何百分比轴，处理所有轴的所有百分比数据
  if (result.isPercent) {
    for (let i = 0; i < data.length; i++) {
      for (const valueAxis of valueAxes) {
        const value = data[i][valueAxis.value]
        if (value !== null && value !== undefined && value !== '') {
          const strValue = String(value).trim()
          if (strValue.endsWith('%')) {
            const formatValue = strValue.replace('%', '')
            const numValue = Number(formatValue)
            result.data[i][valueAxis.value] = isNaN(numValue) ? 0 : numValue
          }
        }
      }
    }
  }

  return result
}

module.exports = {
  checkIsPercent,
  formatNumber,
  getAxesWithFilter,
  processMultiMetricWithSeries,
  processMultiQuotaData,
}
