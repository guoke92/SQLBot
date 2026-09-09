---
type: rule
title: 服务到期处理
page_key: service_expiry_process
belong: rules
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.pay_status, ca_fee_company.renew_remind_sent, ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

# 服务到期处理

业务定位：当企业服务期结束时，自动执行一系列状态更新和待办生成，确保续费流程衔接。

## 需求背景

服务到期后，需完结即将到期待办、关闭续费待缴单、标记企业为未缴费，并生成已过期续费订单和待办。该规则保证服务状态准确，驱动续费闭环。

## 版本演进

当前逻辑集中处理，未来可能拆分事件或增加通知渠道。

```ground:rule
name: 服务到期处理
content: service_end < today 时完结即将到期待办、关闭 RENEW 待缴单、标记公司 UNPAID、按需生成 RENEW_EXPIRED 并发送已过期待办
impact: 续费和服务期状态更新
field_targets: ["ca_fee_company.pay_status", "ca_fee_company.renew_remind_sent", "ca_fee_order.order_status"]
evidence: code:CaFeeRenewalService.processServiceExpired
```

[[ca_fee_company_pay_status]] · [[ca_fee_company]] · [[ca_fee_order]]