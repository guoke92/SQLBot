---
type: caliber
title: 待支付订单
page_key: pending_order
domain: CA证书收费
status: draft
aliases: [PENDING 订单]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:ca_fee_order"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets: [ca_fee_order.order_status]
---

仍可支付的订单行，落 [[ca_fee_order]]，`order_status='PENDING'`。不是「未缴费企业」——企业未缴是 [[unpaid_company]]。库中偶发的 `PAIDING` / `UNPAID` 见 [[order_status]]。

```ground:caliber
name: 待支付订单
predicate: "ca_fee_order.order_status = 'PENDING'"
scope: ca_fee_order
evidence: code
```
