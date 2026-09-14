---
type: enum
title: product_type
page_key: product_type
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




# product_type

（权威枚举页：2 值，绑定方式 db-profile，主承载 platform_product.product_type；db 实测分布。）

```ground:enum
enum: product_type
fields: [platform_product.product_type]
values:
  "GENERAL":
    label: "GENERAL"
  "INTERWORKING":
    label: "INTERWORKING"
```
