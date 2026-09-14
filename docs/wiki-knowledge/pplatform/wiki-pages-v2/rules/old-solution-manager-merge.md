---
type: rule
title: 前方案经理联动合并
page_key: old-solution-manager-merge
domain: 项目报表/统计/上报
status: draft
aliases:
  - old_solution_manager 合并
  - mergeOldSolutionManager
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:SysWxOrgCacheService
contract_version: "0.1"
belong: rules
---

# 前方案经理联动合并

方案经理发生变更时，系统把「既不在原前方案经理列表中、也不在当前方案经理中」的姓名前置合并进 old_solution_manager，从而保留历史责任人痕迹。

## 需求背景

项目交接过程中需要知道此前的方案经理是谁，因此 old_solution_manager 以姓名 CSV 累积保存（字段定义见 [[tables/wechat_project_approval_apply]]）。合并策略保证不重复、不并入现任；导入路径为例外：当前方案经理列有值且与库中不一致时，直接以导入值为准。变更本身受企微身份校验约束（见 [[rules/manager-wechat-identity-validation]]）。

## 版本演进

导入路径的「以导入值为准」例外说明该列在批量数据迁移场景下需要人工可控；合并逻辑被抽到 SysWxOrgCacheService.mergeOldSolutionManager，属从应用层下沉到缓存/组织服务层的演进。

```ground:rule
name: "前方案经理联动合并"
content: "方案经理变更时，将「既不在 existingOld、也不在 curr」的姓名前置合并入 old_solution_manager；导入路径下，若前方案经理列有值且与库中不一致，则直接以导入值为准。"
impact: "编辑保存、批量变更、导入、开发用导入"
field_targets:
  - "wechat_project_approval_apply.old_solution_manager"
evidence: "code_path:ProjectStatisticsApplication.java:update（oldSmInput 三段处理段） + SysWxOrgCacheService.mergeOldSolutionManager"
```