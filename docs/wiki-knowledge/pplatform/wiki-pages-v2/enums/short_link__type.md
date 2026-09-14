---
type: enum
title: type
page_key: short_link__type
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




# type

（权威枚举页：2 值，绑定方式 db-profile，主承载 short_link.type；db 实测分布。）

```ground:enum
enum: short_link__type
fields: [short_link.type]
values:
  "FILE":
    label: "FILE"
  "NORMAL":
    label: "NORMAL"
```
