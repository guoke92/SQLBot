---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-auxiliary@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 冻结中的企业有多少
page_key: count-frozen-companies
domain: 企业建档
anchors:
- cust_company_lifecycle_info
---
# 冻结中的企业有多少

问法：冻结中的企业有多少

```ground:pattern
pattern: count-frozen-companies
question: 冻结中的企业有多少
sql: "SELECT COUNT(DISTINCT company_id) AS frozen_company_count\nFROM cust_company_lifecycle_info\n\
  WHERE type = 'FRZ'\n  AND enable = 'Y'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_lifecycle_info]]
