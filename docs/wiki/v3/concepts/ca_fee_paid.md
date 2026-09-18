---
type: concept
title: CA服务费已缴费
page_key: ca_fee_paid
belong: concepts
domain: ca_fee
status: draft
aliases: [电子签章服务费已缴, CA收费已缴]
maps_to: ca_fee_order.order_status
field_targets: [ca_fee_order.order_status, ca_fee_company.pay_status, ca_fee_company.service_end]
sources: ['code_path:CaFeeRuleEngineService.java:147', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/ca证书收费.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_order, ca_fee_company]
also_confused_with: [ca_fee_company_pay_status, ca_open_status]
adjudication: boundary
---

# CA服务费已缴费

问「当前服务期是否已缴费」优先 covering_paid_ca_fee_order，或企业宽表 service_end≥today。
宽表 pay_status 到期会写成 UNPAID。规则引擎 feeStatus 不是表字段。

## 页面链接

- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[dicts/ca_fee_company__pay_status]]
- [[dicts/ca_fee_order__order_status]]
- [[processes/ca_fee_company__pay_status]]
- [[processes/ca_fee_order__order_status]]
- [[concepts/ca_fee_company_pay_status]]
- [[concepts/ca_open_status]]
