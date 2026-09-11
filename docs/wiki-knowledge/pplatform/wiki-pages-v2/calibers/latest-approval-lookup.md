---
type: caliber
title: 项目最新有效上线审批
page_key: caliber/latest-approval-lookup
domain: 微企链立项与项目审批
status: draft
aliases:
  - findLatestApprovalByProjectCode 口径
  - is_latest 取数口径
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#findLatestApprovalByProjectCode
contract_version: "0.1"
---

按项目查「当前该看哪一次上线审批」时，条件是未逻辑删除且被标记为最新（`is_latest='Y'`）。分页之后还会后置填充 `approvalIsAdd` / `approvalWfStatus`，用于控制列表按钮的显隐——也就是说按钮能不能点，取决于这条口径选出来的那条审批的状态，而不是历史审批的状态。

`is_latest` 的维护规则见 [[rules/is-latest-uniqueness]]，字段语义见 [[tables/tenant_project_approval]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该口径的历史变更记录。

```ground:caliber
name: 项目最新有效上线审批
predicate: "tenant_project_approval.enable = 'Y' AND tenant_project_approval.is_latest = 'Y'"
scope: 按项目 code 取最新审批；分页后置填充 approvalIsAdd/approvalWfStatus 控制按钮显隐
evidence: "code_path:ProjectApprovalApplication.java#findLatestApprovalByProjectCode"
```