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
type: pattern
title: 已缴纳CA服务费的企业有多少
page_key: count-paid-cafee-companies
domain: cafee
anchors:
- ca_fee_company
---
# 已缴纳CA服务费的企业有多少

问法：已缴纳CA服务费的企业有多少

```ground:pattern
pattern: count-paid-cafee-companies
question: 已缴纳CA服务费的企业有多少
sql: SELECT COUNT(DISTINCT certification_no) AS paid_cafee_company_count FROM ca_fee_company
  WHERE pay_status = 'PAID' AND enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[ca_fee_company]]
