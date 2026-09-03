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
title: 建档中的企业列表
page_key: list-building-companies
domain: 企业建档
anchors:
- cust_company_info
---
# 建档中的企业列表

问法：建档中的企业列表

```ground:pattern
pattern: list-building-companies
question: 建档中的企业列表
sql: "SELECT * FROM cust_company_info WHERE enable = 'Y'\n  AND data_type = '1'\n\
  \  AND cust_build_status IN ('BUILDING', 'CUST_BUILDING')\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
