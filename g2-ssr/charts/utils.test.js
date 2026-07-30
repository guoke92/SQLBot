const assert = require('node:assert/strict')
const test = require('node:test')

const {
  getAxesWithFilter,
  processMultiMetricWithSeries,
} = require('./utils')

test('series with multiple metrics keeps every metric for SSR rendering', () => {
  const axes = [
    { name: '月份', value: 'month', type: 'x' },
    { name: '系统', value: 'system', type: 'series' },
    { name: '任务数', value: 'tasks', type: 'y' },
    { name: '需求数', value: 'stories', type: 'y' },
  ]
  const grouped = getAxesWithFilter(axes)

  assert.equal(grouped.multiMetricWithSeries, true)
  assert.equal(grouped.y.length, 2)

  const transformed = processMultiMetricWithSeries(
    grouped.x,
    grouped.y,
    grouped.series,
    [{ month: '2026-03', system: 'AIO', tasks: 2, stories: 1 }],
  )

  assert.deepEqual(transformed.data, [
    {
      month: '2026-03',
      sqlbot_metric_val: 2,
      sqlbot_combined_series: 'AIO-任务数',
      sqlbot_axis_format: undefined,
    },
    {
      month: '2026-03',
      sqlbot_metric_val: 1,
      sqlbot_combined_series: 'AIO-需求数',
      sqlbot_axis_format: undefined,
    },
  ])
  assert.equal(transformed.y[0].value, 'sqlbot_metric_val')
  assert.equal(transformed.series[0].value, 'sqlbot_combined_series')
})
