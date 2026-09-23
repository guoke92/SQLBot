---
type: dict
title: platform_product.multiple_project_flag
page_key: platform_product__multiple_project_flag
belong: dicts
status: draft
anchors: [platform_product.multiple_project_flag]
sources: ['database_profile:platform_product.multiple_project_flag', 'database_schema:platform_product.multiple_project_flag']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [platform_product]
---

# platform_product.multiple_project_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `platform_product.multiple_project_flag`，表页 [[tables/platform_product]]。

## 取值

```ground:dict
dict: platform_product__multiple_project_flag
fields: [platform_product.multiple_project_flag]
values:
  Y: {trust: proposed, label: 是}
  N: {trust: proposed, label: 否}
triage: keep
```
