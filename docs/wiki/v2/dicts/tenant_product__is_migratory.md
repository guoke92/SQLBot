---
type: dict
title: tenant_product.is_migratory
page_key: tenant_product__is_migratory
belong: dicts
status: draft
anchors: [tenant_product.is_migratory]
sources: ['database_profile:tenant_product.is_migratory']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.is_migratory

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_product.is_migratory`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__is_migratory
fields: [tenant_product.is_migratory]
values:
  N: {trust: proposed}
  Y: {trust: proposed}
triage: hold
needs_review: true
```
