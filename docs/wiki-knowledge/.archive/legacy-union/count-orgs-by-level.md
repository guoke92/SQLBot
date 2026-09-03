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
title: 各机构层级分别有多少机构
page_key: count-orgs-by-level
domain: org
anchors:
- org_manage
---
# 各机构层级分别有多少机构

问法：各机构层级分别有多少机构

```ground:pattern
pattern: count-orgs-by-level
question: 各机构层级分别有多少机构
sql: 'SELECT org_level, COUNT(1) AS org_count

  FROM org_manage

  GROUP BY org_level'
verification: PENDING_VALIDATION
```

## 关联
- [[org_manage]]
