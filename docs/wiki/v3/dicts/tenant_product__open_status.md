---
type: dict
title: tenant_product.open_status
page_key: tenant_product__open_status
belong: dicts
status: draft
anchors: [tenant_product.open_status]
sources: ['database_profile:tenant_product.open_status', 'database_schema:tenant_product.open_status',
  'code_path:ProductOpenStatusEnum.java:18', 'code_path:ProductOpenStatusEnum.java:23',
  'code_path:ProductOpenStatusEnum.java:19']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.open_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_product.open_status`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__open_status
fields: [tenant_product.open_status]
values:
  Y: {trust: confirmed, label: 已开通, evidence: 'code_path:ProductOpenStatusEnum.java:18'}
  N: {trust: confirmed, label: 未开通, evidence: 'code_path:ProductOpenStatusEnum.java:23'}
  P: {trust: confirmed, label: 开通中, evidence: 'code_path:ProductOpenStatusEnum.java:19'}
triage: keep
```
