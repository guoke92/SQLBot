---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: metric
title: CA认证记录数
page_key: CA认证记录数
domain: cafee
field_targets:
- ca_certification_info.id
---
# CA认证记录数

按主键计数。

```ground:metric
metric: CA认证记录数
field: ca_certification_info.id
grain: []
aggregation: COUNT
```

## 关联
- [[ca_certification_info]]
