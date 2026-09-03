---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:customer-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 客户配置有多少
page_key: count-customer-config
domain: 企业建档
anchors:
- cust_config_mapping
---
# 客户配置有多少

问法：客户配置有多少

```ground:pattern
pattern: count-customer-config
question: 客户配置有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM cust_config_mapping WHERE enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_config_mapping]]
