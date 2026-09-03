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
title: 已生效集团成员有多少
page_key: count-effective-group-members
domain: 企业建档
anchors:
- cust_group_rel
---
# 已生效集团成员有多少

问法：已生效集团成员有多少

```ground:pattern
pattern: count-effective-group-members
question: 已生效集团成员有多少
sql: 'SELECT COUNT(DISTINCT cust_id) AS effective_group_member_count

  FROM cust_group_rel

  WHERE status = ''EFFECTIVE'' AND enable = ''Y'''
verification: PENDING_VALIDATION
```

## 关联
- [[cust_group_rel]]
