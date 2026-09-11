---
type: rule
title: 上线审批清空关联审批编号
page_key: rule/online-approval-clears-related-no
domain: 微企链立项与项目审批
status: draft
aliases:
  - related_approval_no 清空
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
---

当单据是上线审批（`is_online_approval='Y'`）时，`related_approval_no` 会被清空为空串，而不是置 NULL。这意味着「没有关联审批」在本表中存在两种可能的物理表达（空串与 NULL），读数据时应按空值统一处理。

配套的口径是：关联审批编号下拉只取 `is_online_approval='Y'` 的记录。字段语义见 [[tables/tenant_project_approval]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 上线审批清空关联审批编号
subject: tenant_project_approval.related_approval_no
evidence: code
source_meaning: 关联审批编号；is_online_approval=Y 时被清空为空串
```