---
type: caliber
title: 已缴费企业
page_key: paid_company
domain: CA证书收费
status: draft
aliases: [PAID 企业]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:ca_fee_company"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets: [ca_fee_company.pay_status]
---

统计「当前无欠费」的企业，列在 [[ca_fee_company]]。企业对偶见 [[unpaid_company]]。不要用订单 `order_status='PAID'` 替代，见 [[paid]]。

```ground:caliber
name: 已缴费企业
predicate: "ca_fee_company.pay_status = 'PAID'"
scope: ca_fee_company
evidence: db
```
