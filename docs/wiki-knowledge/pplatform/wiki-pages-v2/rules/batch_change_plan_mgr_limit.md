---
type: rule
title: 批量变更方案经理限制
page_key: batch_change_plan_mgr_limit
domain: 项目报表/统计/上报
status: draft
aliases:
  - 批量变更方案经理限制
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.validateBatchChangePlanMgrRows
contract_version: "0.1"
belong: rules
---

批量变更方案经理时，新方案经理的姓名必须在企微通讯录中存在，且必须属于 Saas 方案部，否则该行校验不通过。该校验把[[concepts/solution_manager|方案经理]]的部门归属从口头约定变成了硬约束，也解释了为什么方案经理与业务经理不能互换。

## 需求背景

需求文档未单列此规则；规则内容来自批量变更校验方法语义。

## 版本演进

v0 契约首版。影响面：批量变更导入；与[[rules/solution_manager_change_linkage|方案经理变更联动]]的联动写入顺序需保证「先校验、后联动」，否则联动会写入不合规人员。字段目标：wechat_project_approval_apply.solution_manager。

```ground:rule
name: 批量变更方案经理限制
content: 批量变更方案经理时，新方案经理姓名必须在企微通讯录存在且属于Saas方案部
impact: 批量变更导入
field_targets:
  - wechat_project_approval_apply.solution_manager
evidence: code_path:ProjectStatisticsApplication.validateBatchChangePlanMgrRows
```