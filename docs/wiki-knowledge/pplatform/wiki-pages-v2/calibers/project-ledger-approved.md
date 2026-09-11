---
type: caliber
title: 项目台账审批通过口径
page_key: caliber.project-ledger-approved
domain: 项目报表/统计/上报
status: draft
aliases:
  - 审批通过口径
  - act_procinst_status=2
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 项目台账审批通过口径

以 `act_procinst_status = '2'` 作为「审批通过」的统一判定。该条件既用于生成主项目名称字典，也作为首笔落地时间触发项目阶段联动的必要前置。状态定义见 [[processes/project-approval-status]]。

## 需求背景

只有已通过企微审批的立项才允许进入统计口径与自动化流转：主项目名称下拉只列通过审批的主项目；若单据未通过审批，即使首笔落地时间被更新也不触发阶段变更（见 [[rules/first-settlement-to-operation-phase]]）。该口径与基础统计口径（[[calibers/project-statistics-list-base]]）叠加使用。

## 版本演进

审批状态当前只消费 1/2 两值，口径判定固定取 2；未见对「审批中」「驳回」等状态的独立统计口径。

```ground:caliber
name: "项目台账审批通过口径"
predicate: "wechat_project_approval_apply.act_procinst_status = '2'"
scope: "主项目名称字典；首笔落地时间→项目阶段联动的触发前置"
evidence: "code_path:ProjectStatisticsApplication.java:listDistinctMainProjectNamesFinTechSaasApproved + ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved"
```