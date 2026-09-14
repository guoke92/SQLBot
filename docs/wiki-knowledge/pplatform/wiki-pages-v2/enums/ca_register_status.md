---
type: enum
title: ca_register_status
page_key: ca_register_status
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




# ca_register_status

（权威枚举页：3 值，绑定方式 db-profile，主承载 cust_company_info.ca_register_status；db 实测分布。）

```ground:enum
enum: ca_register_status
fields: [cust_company_info.ca_register_status]
values:
  "N":
    label: "否"
  "P":
    label: "P"
  "Y":
    label: "是"
```
