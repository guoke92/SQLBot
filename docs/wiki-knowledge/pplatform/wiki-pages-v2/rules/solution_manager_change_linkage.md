---
type: rule
title: 方案经理变更联动
page_key: solution_manager_change_linkage
domain: 项目报表/统计/上报
status: draft
aliases:
  - 方案经理变更联动
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.update
contract_version: "0.1"
belong: rules
---

修改方案经理时，系统同步更新 solution_manager_wxid（企微 userId 列表），并把改动前的方案经理合并进 old_solution_manager。三个字段必须一致变更，否则会出现「有姓名无 userId」导致消息触达失败，或丢失前手责任人的情况。

## 需求背景

需求文档未单列此规则；规则内容来自 update 方法语义，服务于[[concepts/solution_manager|方案经理]]责任人可追溯。

## 版本演进

v0 契约首版。影响面：编辑/导入/批量变更三条入口；批量变更另受[[rules/batch_change_plan_mgr_limit|批量变更方案经理限制]]约束。字段目标：solution_manager、solution_manager_wxid、old_solution_manager。

```ground:rule
name: 方案经理变更联动
content: 修改方案经理时，同步更新solution_manager_wxid，并将原方案经理合并到old_solution_manager
impact: 编辑/导入/批量变更
field_targets:
  - wechat_project_approval_apply.solution_manager
  - wechat_project_approval_apply.solution_manager_wxid
  - wechat_project_approval_apply.old_solution_manager
evidence: code_path:ProjectStatisticsApplication.update
```