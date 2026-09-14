---
type: rule
title: 首笔落地时间变更联动项目阶段为持续运营
page_key: first-settlement-to-operation-phase
domain: 项目报表/统计/上报
status: draft
aliases:
  - 首笔落地联动
  - applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
contract_version: "0.1"
belong: rules
---

# 首笔落地时间变更联动项目阶段为持续运营

当立项已审批通过、且首笔落地时间被更新为新的非空值时，系统自动把项目阶段置为 OPERATION（持续运营）。这是立项统计侧唯一的自动阶段推进规则。

## 需求背景

业务上「首笔落地」意味着项目从实施进入持续运营，因此不需要人工改阶段。规则设定了三重前置：审批通过（见 [[calibers/project-ledger-approved]]）、新值非空、当前阶段非 OPERATION（避免重复写）。首笔落地时间被清空为 null 时**不**触发，这与该列「非空覆盖 / null 清空」的编辑例外语义相配套（见 [[tables/wechat_project_approval_apply]]）。规则在编辑保存、导入、开发用导入三条写入路径均生效，状态定义见 [[processes/project-phase]]。

## 版本演进

规则在正式链路与开发用导入链路各有一份实现（ProjectStatisticsApplication 与 ProjectStatisticsDevImportApplication），属双实现；「非 OPERATION 才覆盖」的保护条件表明该规则曾考虑过阶段被回退/挂起后的重入场景。

```ground:rule
name: "首笔落地时间变更联动项目阶段为持续运营"
content: "当 act_procinst_status='2' 且首笔落地时间发生变化且新值非空且当前项目阶段非 OPERATION 时，自动将 project_phase 置为 OPERATION。首笔落地时间清空（null）场景不触发。"
impact: "编辑保存 / 导入 / 开发用导入 三条写入路径均生效"
field_targets:
  - "wechat_project_approval_apply.project_phase"
  - "wechat_project_approval_apply.first_settlement_time"
evidence: "code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved + code_path:ProjectStatisticsDevImportApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved"
```