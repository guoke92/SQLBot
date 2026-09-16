---
type: rule
title: 企业缴费状态不是订单状态
page_key: pay_status_not_order_status
domain: CA证书收费
status: draft
aliases: [PAID 不要混层]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeOrderService.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - ca_fee_company.pay_status
  - ca_fee_order.order_status
---

问「已缴费 / 未缴费」时先分粒度：

- 企业 → [[paid_company]] / [[unpaid_company]]，列 [[ca_fee_company]].pay_status
- 订单 → [[pending_order]] 或订单 PAID，列 [[ca_fee_order]].order_status

禁止 `pay_status='PENDING'`，禁止用订单 PAID 去数已缴费企业。术语桥见 [[paid]]。

```ground:rule
name: 企业缴费状态不是订单状态
content: 企业 pay_status 为 PAID/UNPAID；订单 order_status 运行时写入 PENDING/PAID/CLOSED（枚举另有 EXPIRED，未落地）。同名 PAID 不是同一键。
impact: 混用会导致已缴企业被再催缴，或待缴订单被当成企业欠费口径。
field_targets: [ca_fee_company.pay_status, ca_fee_order.order_status]
evidence: "code_path:CaFeeOrderService.java:450"
```
