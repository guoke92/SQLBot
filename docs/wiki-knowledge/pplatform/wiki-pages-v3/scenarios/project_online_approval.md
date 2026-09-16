---
type: scenario
title: 项目上线审批
page_key: project_online_approval
domain: 微企链立项与项目审批
status: draft
aliases: [上线审批]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:微企链立项与项目审批"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [tenant_project_approval]
field_targets:
  - tenant_project_approval.wf_status
---

# 项目上线审批

问「上线审批中 / 审批通过后生效项目」时进入本场景。主档 [[tenant_project_approval]]，节点在 [[tenant_project_approval_flow]]。通过后会把 [[tenant_project]] 推到已生效。

`wf_status` 的 PENDING 是「待发起」，节点 `node_status` 的 PENDING 是「待审批」。`tenant_project_approval_flow_comment` 无 Java 引用，本窗不展开。

```ground:scenario
scenario: project_online_approval
hubs:
- table: tenant_project_approval
  role: master
  grain: 一笔上线审批
  window:
  - id
  - enable
  - create_time
  - update_time
  - approval_no
  - sp_no
  - wf_status
  - is_add
  - is_latest
  - flow_code
- table: tenant_project_approval_flow
  role: node
  grain: 审批一个节点
  window:
  - id
  - enable
  - create_time
  - update_time
  - node_status
shared:
- table: tenant_project
  role: project
  window:
  - id
  - enable
  - create_time
  - update_time
  - project_status
  - project_approval_id
  - wechat_audit_no
lifecycle:
- enum: wf_status
  process: wf_status_flow
- enum: node_status
  process: node_status_flow
```
