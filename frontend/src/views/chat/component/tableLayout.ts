// AntV S2 uses a 30px default height for both column headers and data rows.
// Keep the embedded chat table viewport calculation in one place so single-step,
// multi-step and prediction results follow the same rule. Fullscreen fills its viewport.
const TABLE_CELL_HEIGHT = 30
const TABLE_VIEWPORT_MAX_HEIGHT = 352
const TABLE_VIEWPORT_CHROME_HEIGHT = 2
const EMPTY_TABLE_VIEWPORT_HEIGHT = 160

export function getTableViewportHeight(rowCount: number): number {
  const normalizedRowCount = Math.max(0, Math.floor(rowCount))
  if (normalizedRowCount === 0) {
    return EMPTY_TABLE_VIEWPORT_HEIGHT
  }

  const contentHeight = (normalizedRowCount + 1) * TABLE_CELL_HEIGHT + TABLE_VIEWPORT_CHROME_HEIGHT
  return Math.min(TABLE_VIEWPORT_MAX_HEIGHT, contentHeight)
}
