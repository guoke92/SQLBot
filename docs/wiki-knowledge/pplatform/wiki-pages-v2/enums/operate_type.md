---
type: enum
title: operate_type
page_key: operate_type
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: enums
---




# operate_type

（权威枚举页：5 值，绑定方式 db-profile，主承载 tenant_project_approval_flow_node.operate_type；db 实测分布。）

```ground:enum
enum: operate_type
fields: [tenant_project_approval_flow_node.operate_type]
values:
  "back":
    label: "back"
  "delegate":
    label: "delegate"
  "pass":
    label: "pass"
  "reject":
    label: "reject"
  "revoke":
    label: "revoke"
```
