---
type: enum
title: project_type
page_key: project_type
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


# project_type

（权威枚举页：2 值，绑定方式 db-profile，主承载 tenant_project_approval.project_type；db 实测分布。）

```ground:enum
enum: project_type
fields: [tenant_project_approval.project_type]
values:
  "REGULAR":
    label: "REGULAR"
  "STANDARD":
    label: "STANDARD"
```
