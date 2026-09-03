---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:person-user@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 已生效企业管理员有多少
page_key: count-effect-admins
domain: 企业建档
anchors:
- cust_person_info
---
# 已生效企业管理员有多少

问法：已生效企业管理员有多少

```ground:pattern
pattern: count-effect-admins
question: 已生效企业管理员有多少
sql: "SELECT COUNT(1) AS effect_admin_count\nFROM cust_person_info\nWHERE status =\
  \ 'EFFECT'\n  AND user_type = 'accountAdmin'\n  AND enable = 'Y'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_person_info]]
