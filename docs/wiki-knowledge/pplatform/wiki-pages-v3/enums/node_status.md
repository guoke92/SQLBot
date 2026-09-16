---
type: enum
title: node_status
page_key: node_status
domain: 微企链立项与项目审批
status: draft
aliases: [待审批]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [node_status_flow]
---

# node_status

`ProjectApprovalNodeStatusEnum`。PENDING=待审批。

```ground:enum
enum: node_status
fields:
  - tenant_project_approval_flow.node_status
values:
  "PENDING":
    label: "待审批"
  "APPROVING":
    label: "审批中"
  "APPROVED":
    label: "已通过"
  "REJECTED":
    label: "已拒绝"
```
