---
type: concept
title: 对接人引用体系（operation_id）
page_key: concept/operation-id-contact-reference
domain: 微企链立项与项目审批
status: draft
aliases:
  - 运营对接人
  - op_contact 语义
  - operation_id 对接人
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.op_contact
  - wechat_project_approval_apply.archives_contact
  - wechat_project_approval_apply.risk_control_contact
field_targets:
  - table: wechat_project_approval_apply
    field: op_contact
  - table: wechat_project_approval_apply
    field: op_contact_group
  - table: wechat_project_approval_apply
    field: archives_contact
  - table: wechat_project_approval_apply
    field: archives_contact_group
  - table: wechat_project_approval_apply
    field: risk_control_contact
  - table: wechat_project_approval_apply
    field: risk_control_contact_group
adjudication: 三个对接人列（运营/档案/风控）在库内存放的是运营人员 operation_id，既不是姓名、也不是 sys_user id、也不是企微 userId；对应的 *_group 列随各自对接人的 operation_id 反查刷新，属于派生冗余列，不应手工写入。
also_confused_with:
  - wechat_project_approval_apply.solution_manager_wxid（企微 userId，另一套标识体系）
  - wechat_project_approval_apply.solution_manager（姓名 CSV）
  - tenant_project_approval.initiator_user_id（sys_user id）
sources: ["enrich:wiki-admin"]
---

「对接人」在本主题里存在三套并行的人员标识：企微 userId（`solution_manager_wxid`）、sys_user id（`tenant_project_approval.initiator_user_id`）、以及运营人员 `operation_id`（`op_contact` 家族）。这三套互不通用，写统计导入或做人员匹配时最容易在此处串号。

对接人列的第二个特征是「成对出现」：每个 contact 列都配一个 group 列，group 由 contact 反查刷新而非独立录入（见 [[rules/op-contact-group-refresh]]）。因此当 contact 被改而 group 未刷新时，数据即处于不一致状态。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[concepts/solution-manager-identity]]、[[rules/op-contact-group-refresh]]。

相关：[[wechat_project_approval_apply]]
