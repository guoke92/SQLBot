---
type: enum
title: file_type
page_key: file_type
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




# file_type

（权威枚举页：5 值，绑定方式 db-profile，主承载 project_file_info.file_type；db 实测分布。）

```ground:enum
enum: file_type
fields: [project_file_info.file_type]
values:
  "approve":
    label: "approve"
  "check":
    label: "check"
  "collate":
    label: "collate"
  "cust":
    label: "cust"
  "other":
    label: "other"
```
