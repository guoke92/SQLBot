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
title: 当前有多少条待重试的客户端同步失败
page_key: count-retryable-errors
domain: openapi
anchors:
- client_api_sync_error
---
# 当前有多少条待重试的客户端同步失败

问法：当前有多少条待重试的客户端同步失败

```ground:pattern
pattern: count-retryable-errors
question: 当前有多少条待重试的客户端同步失败
sql: 'SELECT COUNT(*) AS retryable_sync_error_count

  FROM client_api_sync_error

  WHERE enable = ''Y'''
verification: PENDING_VALIDATION
```

## 关联
- [[client_api_sync_error]]
