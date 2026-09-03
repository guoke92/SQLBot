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
title: 有效 OpenAPI 渠道密钥有多少
page_key: count-enabled-access-secrets
domain: openapi
anchors:
- cust_access_secret
---
# 有效 OpenAPI 渠道密钥有多少

问法：有效 OpenAPI 渠道密钥有多少

```ground:pattern
pattern: count-enabled-access-secrets
question: 有效 OpenAPI 渠道密钥有多少
sql: 'SELECT COUNT(1) AS enabled_access_secret_count

  FROM cust_access_secret

  WHERE enable = ''Y''

  '
verification: PENDING_VALIDATION
```

## 关联
- [[cust_access_secret]]
