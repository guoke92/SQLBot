---
type: enum
title: person_source
page_key: person_source
domain: 经办人/联系人/管理员管理
status: draft
aliases: [AMS]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# person_source

`CustPersonInfoSourceEnum` 仅 AMS=管理员。库另有 `longteng`，不在枚举内。

```ground:enum
enum: person_source
fields:
  - cust_person_info.source
values:
  "AMS":
    label: "管理员"
  "longteng": {}
```
