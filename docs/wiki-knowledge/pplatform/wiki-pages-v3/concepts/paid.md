---
type: concept
title: 已缴费
page_key: paid
domain: CA证书收费
status: draft
aliases: [PAID, 已缴]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:ca_fee_company"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: concepts
maps_to: ca_fee_company.pay_status
field_targets: [ca_fee_company.pay_status]
adjudication: boundary
boundary: 企业已缴费是汇总状态；订单已缴费是单笔订单状态
also_confused_with: [ca_fee_order.order_status]
---

「已缴费企业」落在 [[ca_fee_company]] 的 `pay_status='PAID'`（口径 [[paid_company]]），不要落到订单 [[ca_fee_order]] 的 `order_status='PAID'`。

企业级会因到期回落为 `UNPAID`（[[ca_fee_company_pay_status]]），历史订单仍为 `PAID`。待缴订单用 [[pending_order]]。裁决见 [[pay_status_not_order_status]]。
