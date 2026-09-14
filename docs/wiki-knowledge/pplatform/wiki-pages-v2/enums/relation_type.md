---
type: enum
title: relation_type
page_key: relation_type
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




# relation_type

（权威枚举页：2 值，绑定方式 db-profile，主承载 cust_shareholder_info.relation_type；db 实测分布。）

```ground:enum
enum: relation_type
fields: [cust_shareholder_info.relation_type]
values:
  "LEGAL_PERSON":
    label: "LEGAL_PERSON"
  "SENIOR_MANAGER":
    label: "SENIOR_MANAGER"
```
