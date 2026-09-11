---
type: process
title: 项目阶段（立项统计）
page_key: process.project-phase
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目阶段流转
  - project_phase
  - projectPhase
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
contract_version: "0.1"
---

# 项目阶段（立项统计）

项目阶段落在 [[tables/wechat_project_approval_apply]] 的 `project_phase`，用于表达立项单据当前处于实施、持续运营还是挂起。它与项目台账维度的「项目状态 project_status」不是同一概念，二者的分域说明见 [[concepts/project-phase]]。

## 需求背景

统计侧需要区分「实施阶段」与「持续运营」以支持运营口径统计；当审批已通过且首笔落地时间被更新为非空时，系统自动把阶段推进到 OPERATION（见 [[rules/first-settlement-to-operation-phase]]）。该联动在编辑保存、导入、开发用导入三条写入路径均生效。挂起（HANG）作为人工/历史状态存在，任何非 OPERATION 阶段在满足条件时都会被覆盖为 OPERATION。

## 版本演进

历史值 `TERMINATION`（终止）在读取时被归一为 `HANG`，说明阶段值域曾发生收敛；「立项阶段」只作为展示态存在，不入库。归一逻辑由 normalizeLegacyProjectPhaseCode 承担。

```ground:state_machine
name: "项目阶段（项目立项统计）"
field: wechat_project_approval_apply.project_phase
states:
  - value: "IMPLEMENTATION"
    label: "实施阶段"
    source: code_enum
  - value: "OPERATION"
    label: "持续运营"
    source: code_enum
  - value: "HANG"
    label: "挂起"
    source: code_enum
  - value: "TERMINATION"
    label: "终止（历史值，读取时归一为 HANG）"
    source: code_enum
transitions:
  - from: "IMPLEMENTATION"
    event: "审批通过 + 首笔落地时间被更新为非空 + 当前阶段非 OPERATION"
    to: "OPERATION"
    evidence: "code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved"
  - from: "HANG"
    event: "同上（任何非 OPERATION 阶段均被覆盖）"
    to: "OPERATION"
    evidence: "code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved"
  - from: "TERMINATION"
    event: "读取归一化 normalizeLegacyProjectPhaseCode"
    to: "HANG"
    evidence: "code_path:ProjectStatisticsApplication.java:normalizeLegacyProjectPhaseCode"
```