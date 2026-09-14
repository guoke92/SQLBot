---
type: concept
title: 已缴费
page_key: paid_payment
domain: CA证书收费
status: draft
aliases:
  - PAID
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
maps_to: ca_fee_company.pay_status
field_targets:
  - ca_fee_company.pay_status
adjudication: boundary
boundary: 企业已缴费是汇总状态；订单已缴费是单笔订单状态
also_confused_with:
  - ca_fee_order.order_status
belong: concepts
field_targets: [ca_fee_company.pay_status]
sources: ["enrich:wiki-admin"]
---

「已缴费」主映射取企业维度 `ca_fee_company.pay_status = 'PAID'`（口径 [[company_pay_status_paid]]），订单维度 `ca_fee_order.order_status = 'PAID'` 是其单笔来源（口径 [[order_status_paid]]，状态机见 [[ca_fee_order_status]]）。

**边界（易混淆）**：企业已缴费是**汇总状态**，可能由服务期内的历史订单支撑；订单已缴费是**单笔事实**，决定该订单不可回退为未缴（见 [[ledger_edit_limit]]）。企业级状态还会因服务到期回落为 `UNPAID`（见 [[renewal_remind_expire]]），此时历史订单仍为 `PAID`。

## 需求背景

台账展示与缴费校验分别需要企业级与订单级结论，混用会造成「已缴企业被要求再缴」或「历史订单被篡改」两类问题。

## 版本演进

- v0（本页）：建立术语桥与边界。

相关：[[ca_fee_company]]
