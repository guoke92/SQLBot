---
type: rule
title: is_latest 唯一最新维护
page_key: is-latest-uniqueness
domain: 微企链立项与项目审批
status: draft
aliases:
  - 重新发起置非最新
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#doCreateApproval
contract_version: "0.1"
belong: rules
---

同一项目可以有多条上线审批记录，但只允许一条是最新：重新发起时把原审批置 `N`、新审批置 `Y`。并且只有最新记录才允许再次重新发起，否则前置校验直接抛异常（见 [[processes/project-approval-workflow-status]] 中 PENDING 的自环transition）。

取用最新审批的口径见 [[calibers/latest-approval-lookup]]，字段语义见 [[tables/tenant_project_approval]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: is_latest 唯一最新维护
subject: tenant_project_approval.is_latest
evidence: code
source_meaning: 是否该项目当前最新审批；重新发起时把原审批置 N、新审批置 Y
```