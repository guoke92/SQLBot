---
type: enum
title: source
page_key: cust_person_info__source
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












# source

（权威枚举页：1 值，绑定方式 setter-evidence，主承载 cust_person_info.source；db 实测分布，基线外 1 值。）

```ground:enum
enum: cust_person_info__source
fields: [cust_person_info.source]
values:
  "AMS":
    label: "管理员"
  "longteng":
    label: "longteng"
    note: "db 分布存在但代码枚举未声明（REVIEW）"
```
