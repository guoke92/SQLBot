---
type: enum
title: order_type
page_key: order_type
domain: CA证书收费
status: draft
aliases: [订单类型]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeOrderTypeEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# order_type

[[ca_fee_order]] 的 `order_type`：这一笔是哪类缴费单。取值来自 `CaFeeOrderTypeEnum`。

```ground:enum
enum: order_type
fields: [ca_fee_order.order_type]
values:
  "FIRST":
    label: "首次缴费"
  "RENEW":
    label: "即将到期续费"
  "RENEW_EXPIRED":
    label: "已到期续费"
  "STOCK":
    label: "存量补录"
```
