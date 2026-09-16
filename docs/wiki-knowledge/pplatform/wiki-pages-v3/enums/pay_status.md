---
type: enum
title: pay_status
page_key: pay_status
domain: CA证书收费
status: draft
aliases: [企业缴费状态]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeCompanyPayStatusEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [ca_fee_company_pay_status]
---

# pay_status

[[ca_fee_company]] 的 `pay_status`，企业级缴费汇总。`CaFeeCompanyPayStatusEnum`。流转见 [[ca_fee_company_pay_status]]。

订单未缴是 `order_status='PENDING'`，不是本列的 `UNPAID`。见 [[paid]]。

```ground:enum
enum: pay_status
fields: [ca_fee_company.pay_status]
values:
  "PAID":
    label: "已缴费"
  "UNPAID":
    label: "未缴费"
```
