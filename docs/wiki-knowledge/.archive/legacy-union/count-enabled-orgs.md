---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:org-manage@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 启用的机构有多少
page_key: count-enabled-orgs
domain: org
anchors:
- org_manage
---
# 启用的机构有多少

问法：启用的机构有多少

```ground:pattern
pattern: count-enabled-orgs
question: 启用的机构有多少
sql: 'SELECT COUNT(1) AS enabled_org_count

  FROM org_manage

  WHERE enable = ''Y'''
verification: PENDING_VALIDATION
```

## 关联
- [[org_manage]]
