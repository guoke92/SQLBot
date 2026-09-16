---
type: scenario
title: 企微立项统计
page_key: wechat_project_stats
domain: 微企链立项与项目审批
status: draft
aliases: [立项统计, 微企链立项]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:微企链立项与项目审批"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [wechat_project_approval_apply]
field_targets:
  - wechat_project_approval_apply.act_procinst_status
  - wechat_project_approval_apply.sp_no
---

# 企微立项统计

问「立项统计 / 真实立项 vs 模拟立项」时进入本场景。主档是 [[wechat_project_approval_apply]]，不是上线审批单 [[tenant_project_approval]]。两边用 `sp_no` / `wechat_audit_no` 对齐，不当成同一张表。

SaaS 统计范围代码写死：`sp_type='金融科技业务'` 且 `system_delivery` 为 SaaS 或 Saas+本地化；可见审批态 `act_procinst_status` 为 `'1'`（审批中）或 `'2'`（已通过）。

```ground:scenario
scenario: wechat_project_stats
hubs:
- table: wechat_project_approval_apply
  role: master
  grain: 一条立项（sp_no）
  window:
  - id
  - enable
  - create_time
  - update_time
  - sp_no
  - sp_type
  - act_procinst_status
  - project_phase
  - data_source
  - first_settlement_time
  - project_id
- table: wechat_project_approval_field_history
  role: history
  grain: 字段一次改写
  window:
  - id
  - enable
  - create_time
  - update_time
  - apply_id
  - field_name
  - old_value
  - new_value
  - change_source
lifecycle: []
shared: []
```
