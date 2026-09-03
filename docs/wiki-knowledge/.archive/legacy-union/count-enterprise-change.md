---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-change@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 企业变更有多少
page_key: count-enterprise-change
domain: 企业建档
anchors:
- cust_change_cfg
---
# 企业变更有多少

问法：企业变更有多少

```ground:pattern
pattern: count-enterprise-change
question: 企业变更有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM cust_change_cfg WHERE enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_change_cfg]]
