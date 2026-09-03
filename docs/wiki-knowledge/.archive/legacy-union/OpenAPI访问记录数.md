---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:openapi-access@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: metric
title: OpenAPI访问记录数
page_key: OpenAPI访问记录数
domain: openapi
field_targets:
- cust_access_secret.id
---
# OpenAPI访问记录数

按主键计数。

```ground:metric
metric: OpenAPI访问记录数
field: cust_access_secret.id
grain: []
aggregation: COUNT
```

## 关联
- [[cust_access_secret]]
