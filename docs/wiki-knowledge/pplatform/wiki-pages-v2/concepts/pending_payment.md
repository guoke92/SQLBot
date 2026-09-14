---
type: concept
title: 待缴费
page_key: pending_payment
domain: CA证书收费
status: draft
aliases:
  - 未缴费
  - PENDING
  - UNPAID
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
maps_to: ca_fee_order.order_status
field_targets:
  - ca_fee_order.order_status
adjudication: boundary
boundary: 订单级待缴是 PENDING；企业级未缴汇总是 UNPAID
also_confused_with:
  - ca_fee_company.pay_status
belong: concepts
field_targets: [ca_fee_order.order_status]
sources: ["enrich:wiki-admin"]
---

「待缴费」是口语化的复合说法，对应两个不同层级的状态字段：订单级 `ca_fee_order.order_status = 'PENDING'`（值 `PENDING`，口径 [[order_status_pending]]），与企业级 `ca_fee_company.pay_status = 'UNPAID'`（值 `UNPAID`，口径 [[company_pay_status_unpaid]]）。

**边界（易混淆）**：订单级待缴是**可操作对象**（可签署协议、可支付、可关闭）；企业级未缴是**汇总结论**（用于统计与筛选）。同一个企业可以「有未缴汇总」但「无可操作待缴订单」。

## 需求背景

三层数据模型（项目—订单—企业）自然会引出同义口语，必须在术语层固定映射，否则运营提问「这单还欠费吗」与「这家企业还欠费吗」会被混为一谈。

## 版本演进

- v0（本页）：建立术语桥与边界。

相关：[[ca_fee_order]]
