---
type: process
title: 项目立项审批状态
page_key: project-approval-status
domain: 项目报表/统计/上报
status: draft
aliases:
  - 审批状态流转
  - act_procinst_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
belong: processes
---

# 项目立项审批状态

审批状态描述一条立项单据在企微审批中的进度，落在 [[tables/wechat_project_approval_apply]] 的 `act_procinst_status`。它是「审批通过口径」的判定基础（见 [[calibers/project-ledger-approved]]），也是首笔落地时间→项目阶段联动的前置条件（见 [[rules/first-settlement-to-operation-phase]]）。

## 需求背景

统计侧只消费「审批通过」这一状态：主项目名称字典、缺方案经理提醒、阶段联动均要求 `act_procinst_status = '2'`（缺方案经理提醒口径见 [[calibers/missing-solution-manager-remind]]）。「审批中」状态用于展示与人工识别，不产生统计侧副作用。状态值由企微审批同步外部写入，系统内部仅做消费，不做状态推进。

## 版本演进

当前值域为 1（审批中）、2（审批通过）两态，未观察到 3 及以上的取值或历史迁移记录；同步链路与状态机的关系尚未有写入侧代码证据，仅能确认消费点。

```ground:state_machine
name: "项目立项审批状态"
field: wechat_project_approval_apply.act_procinst_status
states:
  - value: "1"
    label: "审批中"
    source: code_enum
  - value: "2"
    label: "审批通过"
    source: code_enum
transitions:
  - from: "1"
    event: "企微审批通过（外部同步写入）"
    to: "2"
    evidence: "code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved（仅消费 2 值，非写入点）"
```

相关：[[processes/project-data-source]]、[[processes/project-phase]]。