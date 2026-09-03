---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-onboarding@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 正在建档审核中的企业有多少
page_key: count-building-companies
domain: 企业建档
anchors:
- cust_company_info
---
# 正在建档审核中的企业有多少

问法：正在建档审核中的企业有多少

```ground:pattern
pattern: count-building-companies
question: 正在建档审核中的企业有多少
sql: "SELECT COUNT(1) AS building_company_count FROM cust_company_info WHERE cust_build_status\
  \ = 'CUST_BUILDING'\n  AND enable = 'Y'\n  AND data_type = '1'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
