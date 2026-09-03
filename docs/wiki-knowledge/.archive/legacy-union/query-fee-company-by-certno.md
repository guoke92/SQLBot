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
type: pattern
title: 按统码查企业缴费台账
page_key: query-fee-company-by-certno
domain: CA认证与服务费
anchors:
- ca_fee_company
---
# 按统码查企业缴费台账

问法：按统码查企业缴费台账

```ground:pattern
pattern: query-fee-company-by-certno
question: 按统码查企业缴费台账
sql: SELECT * FROM ca_fee_company WHERE certification_no = ? AND enable = 'Y' LIMIT
  1
verification: PENDING_VALIDATION
```

## 关联
- [[ca_fee_company]]
