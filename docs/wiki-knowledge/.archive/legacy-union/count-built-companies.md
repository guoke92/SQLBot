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
title: 有效已建档企业有多少
page_key: count-built-companies
domain: 企业建档
anchors:
- cust_company_info
---
# 有效已建档企业有多少

问法：有效已建档企业有多少

```ground:pattern
pattern: count-built-companies
question: 有效已建档企业有多少
sql: "SELECT COUNT(1) AS built_company_count FROM cust_company_info WHERE cust_build_status\
  \ = 'BUILD_SUCCESS'\n  AND cust_status = 'EFFECT'\n  AND enable = 'Y'\n  AND data_type\
  \ = '1'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
