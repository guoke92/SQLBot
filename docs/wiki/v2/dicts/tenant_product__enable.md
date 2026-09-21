---
type: dict
title: tenant_product.enable
page_key: tenant_product__enable
belong: dicts
status: draft
anchors: [tenant_product.enable]
sources: ['database_profile:tenant_product.enable']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.enable

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_product.enable`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__enable
fields: [tenant_product.enable]
values:
  Y: {trust: proposed}
triage: keep
```
