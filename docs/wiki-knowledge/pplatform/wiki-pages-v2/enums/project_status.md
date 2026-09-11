---
type: enum
title: project_status
page_key: project_status
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

# project_status

（权威枚举页：3 值，绑定方式 setter-evidence，主承载 tenant_project.project_status；db 实测分布。）

```ground:enum
enum: project_status
fields: [tenant_project.project_status]
values:
  0:
    label: 待生效
  1:
    label: 已生效
  2:
    label: 已失效
```
