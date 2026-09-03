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
title: 当前冻结记录有多少
page_key: count-frozen-lifecycle
domain: 企业建档
anchors:
- cust_company_lifecycle_info
---
# 当前冻结记录有多少

问法：当前冻结记录有多少

```ground:pattern
pattern: count-frozen-lifecycle
question: 当前冻结记录有多少
sql: SELECT COUNT(*) FROM cust_company_lifecycle_info WHERE type = 'FRZ' AND enable
  = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_lifecycle_info]]
