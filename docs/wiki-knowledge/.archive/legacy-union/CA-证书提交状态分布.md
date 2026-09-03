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
title: CA 证书提交状态分布
page_key: CA-证书提交状态分布
domain: ca_certification
field_targets:
- ca_certification_info.id
- ca_certification_info.submit_status
---
# CA 证书提交状态分布

按提交状态统计 CA 证书认证记录数。

```ground:metric
metric: CA 证书提交状态分布
field: ca_certification_info.id
grain:
- ca_certification_info.submit_status
aggregation: COUNT
```

## 关联
- [[ca_certification_info]]
