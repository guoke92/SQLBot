---
type: dict
title: tenant_product.max_financing_amount_flag
page_key: tenant_product__max_financing_amount_flag
belong: dicts
status: draft
anchors: [tenant_product.max_financing_amount_flag]
sources: ['database_profile:tenant_product.max_financing_amount_flag', 'database_schema:tenant_product.max_financing_amount_flag']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.max_financing_amount_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_product.max_financing_amount_flag`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__max_financing_amount_flag
fields: [tenant_product.max_financing_amount_flag]
values:
  N: {trust: proposed, label: 否}
  Y: {trust: proposed, label: 是}
  '0': {trust: proposed, label: 否}
  '1': {trust: proposed, label: 是}
triage: keep
```
