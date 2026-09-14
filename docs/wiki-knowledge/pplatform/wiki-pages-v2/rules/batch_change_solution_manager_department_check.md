---
type: rule
title: 方案经理批量变更部门校验
page_key: batch_change_solution_manager_department_check
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:validateBatchChangePlanMgrRows
contract_version: "0.1"
belong: rules
---

批量变更方案经理时的归属校验与留痕规则。

```ground:rule
name: 方案经理批量变更部门校验
content: 批量变更方案经理时，新方案经理姓名必须在「SaaS方案部」人员名单内，spNo 必须存在，变更写入字段历史（source=BATCH）。
impact: 保证方案经理归属正确。
field_targets:
  - wechat_project_approval_apply.solution_manager
  - wechat_project_approval_apply.sp_no
evidence: code_path:ProjectStatisticsApplication.java:validateBatchChangePlanMgrRows
```

## 需求背景

方案经理在企微侧为姓名多值列并配套企微 ID 列，见 [[concepts/solution_manager]]；变更同时会维护前方案经理列，字段释义见 [[wechat_project_approval_apply]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。