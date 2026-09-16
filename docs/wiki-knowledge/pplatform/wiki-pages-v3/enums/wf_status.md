---
type: enum
title: wf_status
page_key: wf_status
domain: 微企链立项与项目审批
status: draft
aliases: [审批中]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [wf_status_flow]
---

# wf_status

`ProjectApprovalWorkflowStatusEnum`。PENDING=待发起，不是节点上的待审批。

```ground:enum
enum: wf_status
fields:
  - tenant_project_approval.wf_status
values:
  "PENDING":
    label: "待发起"
  "RUNNING":
    label: "审批中"
  "FINISHED":
    label: "审批通过"
  "TERMINATED":
    label: "审批拒绝"
```
