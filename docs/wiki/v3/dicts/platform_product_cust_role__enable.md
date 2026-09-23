---
type: dict
title: platform_product_cust_role.enable
page_key: platform_product_cust_role__enable
belong: dicts
status: draft
anchors: [platform_product_cust_role.enable]
sources: ['database_profile:platform_product_cust_role.enable', 'database_schema:platform_product_cust_role.enable']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [platform_product_cust_role]
---

# platform_product_cust_role.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `platform_product_cust_role.enable`，表页 [[tables/platform_product_cust_role]]。

## 取值

```ground:dict
dict: platform_product_cust_role__enable
fields: [platform_product_cust_role.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用}
triage: keep
```
