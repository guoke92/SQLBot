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
title: CA报数成功率
page_key: CA报数成功率
domain: CA认证与服务费
field_targets:
- ca_certification_info.id
- ca_certification_info.submit_status
---
# CA报数成功率

SUCCESS/(SUCCESS+FAIL) 行占比（按数据来源分组）

```ground:metric
metric: CA报数成功率
field: ca_certification_info.id
grain:
- ca_certification_info.submit_status
aggregation: COUNT
```

## 关联
- [[ca_certification_info]]
