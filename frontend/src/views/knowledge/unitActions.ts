import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import { knowledgeApi, type KnowledgeUnitSummary } from '@/api/knowledge'

export type UnitAction = 'approve' | 'reject' | 'request' | 'publish' | 'unpublish'

export const ACTION_LABELS: Record<UnitAction, string> = {
  approve: '批准',
  reject: '拒绝',
  request: '请求补充',
  publish: '发布',
  unpublish: '撤销发布',
}

/** 生命周期 → 可直接执行的操作（行内按钮/批量共用同一口径）。 */
export function actionsForLifecycle(status: string): UnitAction[] {
  switch (status) {
    case 'IN_REVIEW':
      return ['approve', 'request', 'reject']
    case 'APPROVED':
      return ['publish']
    case 'PUBLISHED':
      return ['unpublish']
    case 'RETIRED':
      return ['publish']
    default:
      return []
  }
}

async function promptReason(title: string): Promise<string | null> {
  try {
    const result = await ElMessageBox.prompt(
      '请说明处理原因，内容会写入该版本的审核记录。',
      title,
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputValidator: (value) => Boolean(value.trim()) || '请填写原因',
      }
    )
    return result.value.trim()
  } catch {
    return null
  }
}

/** 直接调用后端，不弹任何确认/原因框。批量操作请先统一 confirm/prompt 再循环调用本函数。 */
export async function executeUnitAction(
  unitId: number,
  revision: number,
  action: UnitAction,
  reason = ''
): Promise<void> {
  if (action === 'approve') await knowledgeApi.approve(unitId, revision)
  if (action === 'reject') await knowledgeApi.reject(unitId, revision, reason)
  if (action === 'request') await knowledgeApi.requestChanges(unitId, revision, reason)
  if (action === 'publish') await knowledgeApi.publish(unitId, revision)
  if (action === 'unpublish') await knowledgeApi.unpublish(unitId, revision)
}

/** 对单个知识单元执行一次操作；返回是否成功完成。失败/取消均返回 false。 */
export async function runUnitAction(
  unitId: number,
  revision: number,
  action: UnitAction
): Promise<boolean> {
  if (action === 'unpublish') {
    try {
      await ElMessageBox.confirm(
        '撤销发布后，该知识单元将不再被问数召回。绑定和内容会保留，可以重新发布。',
        '撤销发布知识单元',
        { type: 'warning', confirmButtonText: '撤销发布', cancelButtonText: '取消' }
      )
    } catch {
      return false
    }
  }
  let reason = ''
  if (action === 'reject' || action === 'request') {
    const value = await promptReason(action === 'reject' ? '拒绝知识单元' : '请求补充')
    if (value === null) return false
    reason = value
  }
  try {
    await executeUnitAction(unitId, revision, action, reason)
    ElMessage.success(action === 'unpublish' ? '已撤销发布' : '操作成功')
    return true
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '操作失败')
    return false
  }
}

export interface BatchOutcome {
  success: number
  failed: number
}

/** 批量执行同一操作：仅对「当前生命周期支持该操作」的条目生效，统一确认后逐个执行并汇总。 */
export async function batchUnitActions(
  items: KnowledgeUnitSummary[],
  action: UnitAction
): Promise<BatchOutcome> {
  if (action === 'unpublish') {
    try {
      await ElMessageBox.confirm(
        '撤销发布后，选中的 ' + items.length + ' 个知识单元将不再被问数召回。',
        '批量撤销发布',
        { type: 'warning', confirmButtonText: '撤销发布', cancelButtonText: '取消' }
      )
    } catch {
      return { success: 0, failed: 0 }
    }
  }
  let reason = ''
  if (action === 'reject' || action === 'request') {
    const value = await promptReason(action === 'reject' ? '批量拒绝知识单元' : '批量请求补充')
    if (value === null) return { success: 0, failed: 0 }
    reason = value
  }
  const applicable = items.filter((item) =>
    actionsForLifecycle(item.lifecycle_status).includes(action)
  )
  if (!applicable.length) {
    ElMessage.warning('所选条目当前状态均不支持该操作')
    return { success: 0, failed: 0 }
  }
  let success = 0
  let failed = 0
  for (const item of applicable) {
    try {
      await executeUnitAction(item.unit_id, item.revision, action, reason)
      success += 1
    } catch {
      failed += 1
    }
  }
  if (failed) {
    ElMessage.warning(
      '批量' + ACTION_LABELS[action] + '：成功 ' + success + ' 项，失败 ' + failed + ' 项'
    )
  } else {
    ElMessage.success('批量' + ACTION_LABELS[action] + '完成：' + success + ' 项')
  }
  return { success, failed }
}
