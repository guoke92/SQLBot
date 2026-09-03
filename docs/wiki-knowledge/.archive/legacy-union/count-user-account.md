---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:user-account@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 用户与企业账户有多少
page_key: count-user-account
domain: user
anchors:
- cust_user_rel
---
# 用户与企业账户有多少

问法：用户与企业账户有多少

```ground:pattern
pattern: count-user-account
question: 用户与企业账户有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM cust_user_rel WHERE enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_user_rel]]
