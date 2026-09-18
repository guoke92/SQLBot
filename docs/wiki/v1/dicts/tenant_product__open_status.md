---
type: dict
title: tenant_product.open_status
page_key: tenant_product__open_status
belong: dicts
status: draft
anchors: [tenant_product.open_status]
sources: ['database_profile:tenant_product.open_status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.open_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_product.open_status`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__open_status
fields: [tenant_product.open_status]
values:
  Y: {trust: proposed}
  N: {trust: proposed}
  P: {trust: proposed}
triage: keep
```
