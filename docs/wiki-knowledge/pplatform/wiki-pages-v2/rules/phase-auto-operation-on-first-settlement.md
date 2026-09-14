---
type: rule
title: 首笔落地时间首次写入联动项目阶段
page_key: phase-auto-operation-on-first-settlement
domain: 微企链立项与项目审批
status: draft
aliases:
  - 持续运营自动置位
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java#applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
contract_version: "0.1"
belong: rules
---

当企微审批已通过（`act_procinst_status='2'`）、`first_settlement_time` 由空变非空、且当前阶段不是持续运营时，系统自动把项目阶段置为持续运营。三个条件缺一不可：审批未通过的记录即使填了首笔落地时间也不会推进阶段。

注意该字段 DB 注释写的是「首笔放款时间」，与业务口径「首笔落地时间」措辞不同。完整状态流转见 [[processes/project-phase]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 首笔落地时间首次写入联动项目阶段
subject: wechat_project_approval_apply.first_settlement_time
evidence: code
source_meaning: 首笔落地时间（DB 注释写『首笔放款时间』）；审批通过后由空变非空会联动项目阶段置为持续运营
```