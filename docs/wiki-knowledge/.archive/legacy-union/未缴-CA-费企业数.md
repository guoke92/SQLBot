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
title: 未缴 CA 费企业数
page_key: 未缴-CA-费企业数
domain: ca_fee
field_targets:
- ca_fee_company.id
- ca_fee_company.tenant_id
---
# 未缴 CA 费企业数

未缴纳 CA 费的企业台账数，按租户统计。

```ground:metric
metric: 未缴 CA 费企业数
field: ca_fee_company.id
grain:
- ca_fee_company.tenant_id
aggregation: COUNT_DISTINCT
```

## 关联
- [[ca_fee_company]]
