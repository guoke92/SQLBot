---
type: dict
title: tenant_interworking_product.open_status
page_key: tenant_interworking_product__open_status
belong: dicts
status: draft
anchors: [tenant_interworking_product.open_status]
sources: ['database_profile:tenant_interworking_product.open_status', 'database_schema:tenant_interworking_product.open_status',
  'code_path:ProductOpenStatusEnum.java:23', 'code_path:ProductOpenStatusEnum.java:18']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_interworking_product]
---

# tenant_interworking_product.open_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_interworking_product.open_status`，表页 [[tables/tenant_interworking_product]]。

## 取值

```ground:dict
dict: tenant_interworking_product__open_status
fields: [tenant_interworking_product.open_status]
values:
  N: {trust: confirmed, label: 未开通, evidence: 'code_path:ProductOpenStatusEnum.java:23'}
  Y: {trust: confirmed, label: 已开通, evidence: 'code_path:ProductOpenStatusEnum.java:18'}
triage: keep
```
