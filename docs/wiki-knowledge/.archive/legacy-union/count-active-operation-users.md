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
title: 在职运营人员有多少
page_key: count-active-operation-users
domain: operation
anchors:
- operation_user
---
# 在职运营人员有多少

问法：在职运营人员有多少

```ground:pattern
pattern: count-active-operation-users
question: 在职运营人员有多少
sql: 'SELECT COUNT(DISTINCT id) AS active_operation_user_count

  FROM operation_user

  WHERE deleted = ''N'' AND enable = ''Y'''
verification: PENDING_VALIDATION
```

## 关联
- [[operation_user]]
