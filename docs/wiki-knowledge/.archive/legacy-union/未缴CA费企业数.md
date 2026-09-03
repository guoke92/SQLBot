---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: metric
title: 未缴CA费企业数
page_key: 未缴CA费企业数
domain: ca_fee
field_targets:
- ca_fee_company.id
- ca_fee_company.id
---
# 未缴CA费企业数

按企业台账主键去重统计未缴企业

```ground:metric
metric: 未缴CA费企业数
field: ca_fee_company.id
grain:
- ca_fee_company.id
aggregation: COUNT_DISTINCT
```

## 关联
- [[ca_fee_company]]
