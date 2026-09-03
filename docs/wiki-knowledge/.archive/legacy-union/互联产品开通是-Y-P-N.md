---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:interworking@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 互联产品开通是 Y/P/N
page_key: 互联产品开通是-Y-P-N
domain: interworking
field_targets:
- tenant_interworking_product.open_status
---
# 互联产品开通是 Y/P/N

互联产品 open_status 只用 Y/P/N，与企业申请表 OPENED 是两套口径。

```ground:rule
rule: interworking-open-is-ynp
field_targets:
- tenant_interworking_product.open_status
impact: query_constraint
content: 互联产品 open_status 只用 Y/P/N，与企业申请表 OPENED 是两套口径。
scope: 已开通互联产品、开通中互联产品
```

## 关联
- [[tenant_interworking_product]]
