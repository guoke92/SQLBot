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
type: enum
title: CA总公司标识
page_key: head_company_data
domain: certification
aliases:
- 总公司
- 分公司
anchors:
- head_company_data
---
# CA总公司标识

head_company_data 区分总公司(Y)与分公司(N)；分公司场景同一企业有 N+Y 两行，各自独立 batch_no。

```ground:enum
enum: head_company_data
fields:
- ca_certification_info.head_company_data
values:
  Y:
    label: 总公司
  N:
    label: 分公司
```

## 关联
- [[ca_certification_info|ca_certification_info]]
