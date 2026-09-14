---
type: enum
title: order_type
page_key: order_type
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




# order_type

（权威枚举页：4 值，绑定方式 db-profile，主承载 ca_fee_order.order_type；db 实测分布。）

```ground:enum
enum: order_type
fields: [ca_fee_order.order_type]
values:
  "FIRST":
    label: "FIRST"
  "RENEW":
    label: "RENEW"
  "RENEW_EXPIRED":
    label: "RENEW_EXPIRED"
  "STOCK":
    label: "STOCK"
```
