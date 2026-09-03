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
title: 有效已建档的企业有多少
page_key: count-active-companies
domain: 企业建档
anchors:
- cust_company_info
---
# 有效已建档的企业有多少

问法：有效已建档的企业有多少

```ground:pattern
pattern: count-active-companies
question: 有效已建档的企业有多少
sql: "SELECT COUNT(DISTINCT id) AS built_company_count FROM cust_company_info WHERE\
  \ data_type = '1'\n  AND enable = 'Y'\n  AND ((cust_build_status = 'BUILD_SUCCESS'\
  \ AND cust_status = 'EFFECT')\n    OR (cust_build_status = 'CUST_CHANGE' AND cust_status\
  \ = 'CHANGE'))\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
