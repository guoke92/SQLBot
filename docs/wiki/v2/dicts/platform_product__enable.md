---
type: dict
title: platform_product.enable
page_key: platform_product__enable
belong: dicts
status: draft
anchors: [platform_product.enable]
sources: ['database_profile:platform_product.enable']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [platform_product]
---

# platform_product.enable

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `platform_product.enable`，表页 [[tables/platform_product]]。

## 取值

```ground:dict
dict: platform_product__enable
fields: [platform_product.enable]
values:
  Y: {trust: proposed}
  N: {trust: proposed}
triage: keep
```
