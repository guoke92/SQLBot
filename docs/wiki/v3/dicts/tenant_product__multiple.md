---
type: dict
title: tenant_product.multiple
page_key: tenant_product__multiple
belong: dicts
status: draft
anchors: [tenant_product.multiple]
sources: ['database_profile:tenant_product.multiple', 'database_schema:tenant_product.multiple']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.multiple

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_product.multiple`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__multiple
fields: [tenant_product.multiple]
values:
  '0': {trust: proposed, label: 否}
  '1': {trust: proposed, label: 是, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
