---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:interworking@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 互联互通有多少
page_key: count-interworking
domain: interworking
anchors:
- cust_interworking_product
---
# 互联互通有多少

问法：互联互通有多少

```ground:pattern
pattern: count-interworking
question: 互联互通有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM cust_interworking_product WHERE enable
  = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_interworking_product]]
