---
type: caliber
title: 未缴费企业
page_key: unpaid_company
domain: CA证书收费
status: draft
aliases: [UNPAID 企业]
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

企业维度欠费快照，列在 [[ca_fee_company]]，含「从未缴费」与「已到期未续费」。不含白名单免缴（[[whitelist_exempt]] 应单独筛）。不要与订单 [[pending_order]] 互换。

```ground:caliber
name: 未缴费企业
predicate: "ca_fee_company.pay_status = 'UNPAID'"
scope: ca_fee_company
evidence: db
```
