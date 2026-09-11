---
type: table
title: 立项审批字段变更历史表（wechat_project_approval_apply_field_history）
page_key: table.wechat_project_approval_apply_field_history
domain: 项目报表/统计/上报
status: draft
aliases:
  - wechat_project_approval_apply_field_history
  - 立项字段历史表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 立项审批字段变更历史表（wechat_project_approval_apply_field_history）

本表记录 [[tables/wechat_project_approval_apply]] 各列的人工/批量/导入变更轨迹，是「谁在什么路径下改了什么」的审计落点。它不参与列表展示与统计口径计算，但决定了同步保护与差异写库的可追溯性。

## 需求背景

立项统计的编辑保存只对白名单列做 diff 写库，并同步写入本表；企微同步 Job 在写库前需跳过已被人工写入的保护字段，避免覆盖人工结果（见 [[rules/edit-whitelist-and-field-history]]）。因此本表需要区分变更来源：页面编辑、批量变更、模拟立项、导入，四类来源对应不同的写入路径与责任方。

## 版本演进

`change_source` 当前已有 EDIT / BATCH / MANUAL_CREATE / IMPORT 四种取值，反映写入入口由单一页面编辑扩展为批量、模拟立项与导入并存；未观察到该列的更早取值形态。

```ground:fields
table: wechat_project_approval_apply_field_history
fields:
  - name: change_source
    meaning: "字段历史来源：EDIT=页面编辑 / BATCH=批量变更 / MANUAL_CREATE=模拟立项 / IMPORT=导入"
    evidence: code
```