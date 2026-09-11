---
type: enum
title: node_status
page_key: node_status
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# node_status

（权威枚举页：4 值，绑定方式 setter-evidence，主承载 tenant_project_approval_flow.node_status；db 实测分布。）

```ground:enum
enum: node_status
fields: [tenant_project_approval_flow.node_status]
values:
  PENDING:
    label: 待审批
  APPROVING:
    label: 审批中
  APPROVED:
    label: 已通过
  REJECTED:
    label: 已拒绝
```
