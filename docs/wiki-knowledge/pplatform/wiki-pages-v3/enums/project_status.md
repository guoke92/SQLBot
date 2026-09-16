---
type: enum
title: project_status
page_key: project_status
domain: 租户产品/互通产品/租户项目
status: draft
aliases: [已生效项目]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [project_status_flow]
---

# project_status

`ProjectStatusEnum` dictKey：`'0'` 待生效 / `'1'` 已生效 / `'2'` 已失效（枚举名 INVLIAD）。

```ground:enum
enum: project_status
fields:
  - tenant_project.project_status
values:
  "0":
    label: "待生效"
  "1":
    label: "已生效"
  "2":
    label: "已失效"
```
