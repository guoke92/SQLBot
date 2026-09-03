---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:op-user-coverage@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 运营用户覆盖有多少
page_key: count-op-user-coverage
domain: operation
anchors:
- operation_user
---
# 运营用户覆盖有多少

问法：运营用户覆盖有多少

```ground:pattern
pattern: count-op-user-coverage
question: 运营用户覆盖有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM operation_user WHERE enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[operation_user]]
