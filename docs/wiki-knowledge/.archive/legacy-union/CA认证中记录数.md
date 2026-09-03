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
title: CA认证中记录数
page_key: CA认证中记录数
domain: certification
field_targets:
- ca_certification_info.id
- ca_certification_info.submit_status
---
# CA认证中记录数

submit_status=PENDING 的 CA 认证记录数。

```ground:metric
metric: CA认证中记录数
field: ca_certification_info.id
grain:
- ca_certification_info.submit_status
aggregation: COUNT
```

## 关联
- [[ca_certification_info]]
