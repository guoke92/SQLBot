---
type: rule
title: 服务到期处理
page_key: service_expiry_processing
belong: rules
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.pay_status, ca_fee_company.renew_remind_sent, ca_fee_order.order_status, ca_fee_order.order_type]
scope:
  databases: [lowcode_pplatform]
---

服务到期处理规则在定时任务扫描到 service_end < today 的企业时触发：若企业仍为 PAID 则标记为 UNPAID，关闭 RENEW 订单，创建 RENEW_EXPIRED 订单并发送续费待办。

## 需求背景

需要在服务到期后自动将企业状态转为未缴费，并生成新的续费订单，推动续费流程。

## 版本演进

v0.1 草稿：来自 CaFeeScheduledJobHandler.caFeeServiceExpireJob 与 CaFeeRenewalService.processServiceExpired 的代码证据。

```ground:rule
name: 服务到期处理
content: "定时任务扫描service_end < today的企业，若仍PAID则标记UNPAID，关闭RENEW订单，创建RENEW_EXPIRED订单并发送待办"
impact: "到期自动转为未缴费，生成续费订单"
field_targets:
  - ca_fee_company.pay_status
  - ca_fee_company.renew_remind_sent
  - ca_fee_order.order_status
  - ca_fee_order.order_type
evidence: code_path:CaFeeScheduledJobHandler.caFeeServiceExpireJob + CaFeeRenewalService.processServiceExpired
```

相关：[[ca_fee_company]]、[[ca_fee_order]]、[[ca_fee_company_pay_status]]、[[unpaid_company]]