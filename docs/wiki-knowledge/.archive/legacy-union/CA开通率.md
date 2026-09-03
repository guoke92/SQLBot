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
title: CA开通率
page_key: CA开通率
domain: CA认证与服务费
field_targets:
- ca_certification_info.cust_id
- ca_certification_info.data_source
---
# CA开通率

ca_register_status=Y 企业数 / enable=Y 企业数

```ground:metric
metric: CA开通率
field: ca_certification_info.cust_id
grain:
- ca_certification_info.data_source
aggregation: COUNT
```

## 关联
- [[ca_certification_info]]
