---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee-collection@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 企业缴费状态
page_key: pay_status
domain: CA认证与服务费
aliases:
- 已缴费企业
- 未缴费企业
- 欠费企业
anchors:
- pay_status
---
# 企业缴费状态

ca_fee_company.pay_status：PAID 已缴费（在服务期内）/ UNPAID 未缴费。 注意服务到期任务会把 PAID 翻回 UNPAID。

```ground:enum
enum: pay_status
fields:
- ca_fee_company.pay_status
values:
  PAID:
    label: 已缴费
  UNPAID:
    label: 未缴费
```

## 关联
- [[ca_fee_company|ca_fee_company]]
