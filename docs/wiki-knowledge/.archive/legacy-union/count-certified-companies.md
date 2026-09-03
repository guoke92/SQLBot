---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 有多少企业认证通过
page_key: count-certified-companies
domain: 企业建档
anchors:
- cust_certification_info
---
# 有多少企业认证通过

问法：有多少企业认证通过

```ground:pattern
pattern: count-certified-companies
question: 有多少企业认证通过
sql: SELECT COUNT(DISTINCT ref_cust_company_info) AS certified_company_count FROM
  cust_certification_info WHERE auto_verify_status = 'AUTOMATIC_AUTHENTICATION_PASSED'
  OR manual_verify_status = 'MANUAL_AUTHENTICATION_PASSED'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_certification_info]]
