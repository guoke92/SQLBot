---
type: enum
title: source
page_key: cust_person_info__source
belong: enums
domain: 基线
status: draft
aliases: []
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# source

（权威枚举页：1 值，绑定方式 setter-evidence，主承载 cust_person_info.source；db 实测分布。）

```ground:enum
enum: cust_person_info__source
fields: [cust_person_info.source]
values:
  AMS:
    label: 管理员
```
