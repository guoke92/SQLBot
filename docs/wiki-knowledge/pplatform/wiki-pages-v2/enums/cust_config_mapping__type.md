---
type: enum
title: type
page_key: cust_config_mapping__type
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

（权威枚举页：3 值，绑定方式 db-profile，主承载 cust_config_mapping.type；db 实测分布。）

```ground:enum
enum: cust_config_mapping__type
fields: [cust_config_mapping.type]
values:
  "CHANGE_ITEM":
    label: "CHANGE_ITEM"
  "COMPANY_MEDIA":
    label: "COMPANY_MEDIA"
  "COMPANY_TYPE_MAPPING":
    label: "COMPANY_TYPE_MAPPING"
```
