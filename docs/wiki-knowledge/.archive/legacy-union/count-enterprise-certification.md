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
title: 企业认证有多少
page_key: count-enterprise-certification
domain: 企业建档
anchors:
- cust_certification_info
---
# 企业认证有多少

问法：企业认证有多少

```ground:pattern
pattern: count-enterprise-certification
question: 企业认证有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM cust_certification_info WHERE enable =
  'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_certification_info]]
