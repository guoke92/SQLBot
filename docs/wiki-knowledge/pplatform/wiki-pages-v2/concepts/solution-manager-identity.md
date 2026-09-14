---
type: concept
title: 方案经理身份联动（姓名 CSV / 企微 userId / 历史值）
page_key: solution-manager-identity
domain: 微企链立项与项目审批
status: draft
aliases:
  - 方案经理标识
  - old_solution_manager
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.solution_manager
  - wechat_project_approval_apply.solution_manager_wxid
  - wechat_project_approval_apply.old_solution_manager
  - tenant_project_approval.solution_manager_id
  - tenant_project_approval.solution_manager_name
field_targets:
  - table: wechat_project_approval_apply
    field: solution_manager
  - table: wechat_project_approval_apply
    field: solution_manager_wxid
  - table: wechat_project_approval_apply
    field: old_solution_manager
  - table: tenant_project_approval
    field: solution_manager_id
  - table: tenant_project_approval
    field: solution_manager_name
adjudication: 方案经理在库内是多值：姓名以逗号分隔 CSV 存放（solution_manager / solution_manager_name），身份以 JSON 数组字符串存放（solution_manager_wxid / solution_manager_id），姓名由企微 userId 反查得到；变更时旧姓名由 mergeOldSolutionManager 合并进 old_solution_manager。姓名与 id 必须联动维护，不可单独更新。
also_confused_with:
  - wechat_project_approval_apply.op_contact（存 operation_id，另一套标识）
  - tenant_project_approval.initiator_user_id（sys_user id，单值）
sources: ["enrich:wiki-admin"]
belong: concepts
---

方案经理字段家族体现了「先有 id、后反查姓名」的落库顺序：写库时先确定企微 userId 数组，再由 userId 反查姓名组成 CSV。`old_solution_manager` 保留了历史姓名的合并结果，用于回答「这个人曾经是不是方案经理」。

由此推导出一条运维事实：方案经理缺失是可以被检测出来的，统计页有基于 `apply_start_time` 的缺失提醒（见 [[rules/solution-manager-missing-reminder]]）。身份体系的全景见 [[concepts/operation-id-contact-reference]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[tables/tenant_project_approval]]。

相关：[[wechat_project_approval_apply]]
