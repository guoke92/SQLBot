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
title: 待客户认证的企业有多少
page_key: count-pending-cust-confirm
domain: 企业建档
anchors:
- cust_company_info
---
# 待客户认证的企业有多少

问法：待客户认证的企业有多少

```ground:pattern
pattern: count-pending-cust-confirm
question: 待客户认证的企业有多少
sql: SELECT COUNT(DISTINCT id) AS pending_cust_confirm_count FROM cust_company_info
  WHERE cust_build_status = 'CUST_CONFIRM_AWAIT'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
