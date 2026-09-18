---
type: dict
title: tenant_product.is_migratory
page_key: tenant_product__is_migratory
belong: dicts
status: draft
anchors: [tenant_product.is_migratory]
sources: ['database_profile:tenant_product.is_migratory', 'database_schema:tenant_product.is_migratory']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.is_migratory

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_product.is_migratory`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__is_migratory
fields: [tenant_product.is_migratory]
values:
  N: {trust: proposed, label: 未迁移, evidence: 'database_schema:tenant_product.is_migratory'}
  Y: {trust: proposed, label: 迁移, evidence: 'database_schema:tenant_product.is_migratory'}
triage: keep
```
