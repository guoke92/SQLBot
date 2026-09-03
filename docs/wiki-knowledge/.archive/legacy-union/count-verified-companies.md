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
title: 已通过实名认证的企业有多少
page_key: count-verified-companies
domain: 企业建档
anchors:
- cust_certification_info
---
# 已通过实名认证的企业有多少

问法：已通过实名认证的企业有多少

```ground:pattern
pattern: count-verified-companies
question: 已通过实名认证的企业有多少
sql: "SELECT COUNT(DISTINCT ref_cust_company_info) AS verified_company_count\nFROM\
  \ cust_certification_info\nWHERE auto_verify_status = 'AUTOMATIC_AUTHENTICATION_PASSED'\n\
  \  OR manual_verify_status = 'MANUAL_AUTHENTICATION_PASSED'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_certification_info]]
