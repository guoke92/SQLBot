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
title: CA认证成功企业数
page_key: CA认证成功企业数
domain: certification
field_targets:
- ca_certification_info.id
- ca_certification_info.submit_status
---
# CA认证成功企业数

submit_status=SUCCESS 且 enable=Y 的 CA 认证记录数（按企业去重前为记录数）。

```ground:metric
metric: CA认证成功企业数
field: ca_certification_info.id
grain:
- ca_certification_info.submit_status
aggregation: COUNT
```

## 关联
- [[ca_certification_info]]
