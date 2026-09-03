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
title: 某企业的管理员有哪些
page_key: list-admin-persons
domain: person
anchors:
- cust_person_info
---
# 某企业的管理员有哪些

问法：某企业的管理员有哪些

```ground:pattern
pattern: list-admin-persons
question: 某企业的管理员有哪些
sql: "SELECT id, name, user_type FROM cust_person_info WHERE ref_cust_company_info\
  \ = '<企业code>'\n  AND user_type = 'accountAdmin'\n  AND enable = 'Y'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_person_info]]
