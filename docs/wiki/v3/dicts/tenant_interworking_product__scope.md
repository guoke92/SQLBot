---
type: dict
title: tenant_interworking_product.scope
page_key: tenant_interworking_product__scope
belong: dicts
status: draft
anchors: [tenant_interworking_product.scope]
sources: ['database_profile:tenant_interworking_product.scope', 'database_schema:tenant_interworking_product.scope',
  'code_path:ProductScopeEnum.java:17', 'code_path:ProductScopeEnum.java:18']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_interworking_product]
---

# tenant_interworking_product.scope

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_interworking_product.scope`，表页 [[tables/tenant_interworking_product]]。

## 取值

```ground:dict
dict: tenant_interworking_product__scope
fields: [tenant_interworking_product.scope]
values:
  ALL: {trust: confirmed, label: 全部, evidence: 'code_path:ProductScopeEnum.java:17'}
  SOME: {trust: confirmed, label: 特定范围, evidence: 'code_path:ProductScopeEnum.java:18'}
triage: keep
```
