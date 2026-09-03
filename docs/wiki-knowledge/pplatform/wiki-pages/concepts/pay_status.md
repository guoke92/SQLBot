---
type: concept
title: 缴费状态
page_key: pay_status
domain: ca_cert_fee
status: published
aliases: ["支付状态"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "ca_fee_company.pay_status"
field_targets: ["ca_fee_company.pay_status"]
adjudication: boundary
also_confused_with: ["ca_fee_order.order_status", "CaFeeFeeStatusEnum.feeStatus"]
boundary: "company 维度汇总缴费状态；order 维度订单状态；feeStatus 规则引擎评估状态，三者不可混用"
scope:
  databases: [lowcode_pplatform]
---

# 缴费状态

业务定位：企业维度的汇总缴费状态，用于表示企业整体是否已缴纳当前周期的 CA 服务费。

## 需求背景

缴费状态容易与订单状态（`order_status`）和规则引擎评估状态（`feeStatus`）混淆。本概念明确划界：缴费状态仅指 `ca_fee_company.pay_status`，反映企业台账层面的汇总结果。

## 版本演进

当前仅包含 PAID/UNPAID 两个值，后续可能细分部分缴费、欠费等状态。

[[ca_fee_company]] · [[ca_fee_company_pay_status]] · [[pay_status]]