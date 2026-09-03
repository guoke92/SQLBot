---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:openapi-access@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: OpenAPI访问有多少
page_key: count-openapi-access
domain: openapi
anchors:
- cust_access_secret
---
# OpenAPI访问有多少

问法：OpenAPI访问有多少

```ground:pattern
pattern: count-openapi-access
question: OpenAPI访问有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM cust_access_secret WHERE enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_access_secret]]
