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
title: 未缴CA费的企业有多少
page_key: count-unpaid-ca-fee-companies
domain: ca_fee
anchors:
- ca_fee_company
---
# 未缴CA费的企业有多少

问法：未缴CA费的企业有多少

```ground:pattern
pattern: count-unpaid-ca-fee-companies
question: 未缴CA费的企业有多少
sql: 'SELECT COUNT(DISTINCT id) AS unpaid_ca_fee_company_count

  FROM ca_fee_company WHERE pay_status = ''UNPAID'' AND enable = ''Y'''
verification: PENDING_VALIDATION
```

## 关联
- [[ca_fee_company]]
