---
type: concept
title: 方案经理
page_key: solution_manager
domain: 项目报表/统计/上报
status: draft
aliases:
  - 方案经理
  - solutionManager
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.update
  - code_path:ProjectStatisticsApplication.listApprovedMissingSolutionManagerForRemind
  - code_path:ProjectStatisticsApplication.validateBatchChangePlanMgrRows
contract_version: "0.1"
maps_to: wechat_project_approval_apply.solution_manager
field_targets:
  - wechat_project_approval_apply.solution_manager
  - wechat_project_approval_apply.solution_manager_wxid
  - wechat_project_approval_apply.old_solution_manager
adjudication: boundary
also_confused_with:
  - 业务经理
belong: concepts
field_targets: [wechat_project_approval_apply.solution_manager]
sources: ["enrich:wiki-admin"]
---

方案经理是立项申请上的方案责任人，落库在三联字段上：solution_manager（姓名 CSV）、solution_manager_wxid（企微 userId 的 JSON 数组字符串，用于通讯录校验与消息触达）、old_solution_manager（原方案经理姓名 CSV，用于留痕）。本页区分的是「谁是方案经理」这一问题：人员必须在企微通讯录中存在，且属 Saas 方案部。

## 需求背景

需求文档使用「方案经理」与「solutionManager」两种称法，属同一概念。它与「业务经理」之间为边界关系（adjudication=boundary）：方案经理属 Saas 方案部，业务经理属客户营销部，两者不可互相代入校验。

## 版本演进

v0 契约首版。变更与校验分别见 [[rules/solution_manager_change_linkage|方案经理变更联动]]、[[rules/batch_change_plan_mgr_limit|批量变更方案经理限制]]，缺失监控见 [[calibers/missing_solution_manager_remind|缺方案经理提醒范围]]。易混项：业务经理。

相关：[[wechat_project_approval_apply]]
