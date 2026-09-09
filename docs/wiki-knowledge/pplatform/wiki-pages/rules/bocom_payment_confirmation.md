---
type: rule
title: 交e保支付确认
page_key: bocom_payment_confirmation
belong: rules
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_order.bocom_txn_sts, ca_fee_order.order_status, ca_fee_order.pay_amount]
scope:
  databases: [lowcode_pplatform]
---

交e保支付确认规则限制仅 PENDING 且 pay_method=BOCOM 的订单可以确认打款。系统查询账户余额不低于订单应缴年费后执行划扣，成功则调用 markPaid 更新订单状态。

## 需求背景

必须确保支付成功后订单状态更新为已缴费，并记录实缴金额与交e保交易响应状态，避免未支付订单被错误标记。

## 版本演进

v0.1 草稿：来自 CaFeePaymentApplication.confirmBocomPaid 的代码证据。

```ground:rule
name: 交e保支付确认
content: "仅PENDING且pay_method=BOCOM订单可确认打款；查账户余额>=annual_fee后划扣，成功则markPaid"
impact: "确保支付成功更新订单状态"
field_targets:
  - ca_fee_order.order_status
  - ca_fee_order.pay_amount
  - ca_fee_order.bocom_txn_sts
evidence: code_path:CaFeePaymentApplication.confirmBocomPaid
```

相关：[[ca_fee_order]]、[[ca_fee_order_order_status]]、[[bocom-provider]]