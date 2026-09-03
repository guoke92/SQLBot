---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: metric
title: 已缴费CA服务费企业数
page_key: 已缴费CA服务费企业数
domain: cafee
field_targets:
- ca_fee_company.id
- ca_fee_company.certification_no
---
# 已缴费CA服务费企业数

ca_fee_company 中 pay_status=PAID 且 enable=Y 的企业数。

```ground:metric
metric: 已缴费CA服务费企业数
field: ca_fee_company.id
grain:
- ca_fee_company.certification_no
aggregation: COUNT_DISTINCT
```

## 关联
- [[ca_fee_company]]
