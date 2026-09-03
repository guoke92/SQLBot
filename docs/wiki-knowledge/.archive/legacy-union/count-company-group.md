---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:company-group@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 企业集团/关联关系有多少
page_key: count-company-group
domain: 企业建档
anchors:
- cust_group_rel
---
# 企业集团/关联关系有多少

问法：企业集团/关联关系有多少

```ground:pattern
pattern: count-company-group
question: 企业集团/关联关系有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM cust_group_rel WHERE enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_group_rel]]
