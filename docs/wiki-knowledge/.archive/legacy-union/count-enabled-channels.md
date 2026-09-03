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
title: 当前有多少个有效 OpenAPI 渠道
page_key: count-enabled-channels
domain: openapi
anchors:
- cust_access_secret
---
# 当前有多少个有效 OpenAPI 渠道

问法：当前有多少个有效 OpenAPI 渠道

```ground:pattern
pattern: count-enabled-channels
question: 当前有多少个有效 OpenAPI 渠道
sql: 'SELECT COUNT(DISTINCT channel) AS enabled_channel_count

  FROM cust_access_secret

  WHERE enable = ''Y'''
verification: PENDING_VALIDATION
```

## 关联
- [[cust_access_secret]]
