---
type: dict
title: platform_product.product_status
page_key: platform_product__product_status
belong: dicts
status: draft
anchors: [platform_product.product_status]
sources: ['database_profile:platform_product.product_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [platform_product]
---

# platform_product.product_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `platform_product.product_status`，表页 [[tables/platform_product]]。

## 取值

```ground:dict
dict: platform_product__product_status
fields: [platform_product.product_status]
values:
  '1': {trust: proposed}
triage: keep
```
