---
type: dict
title: tenant_product_menu_res.enable
page_key: tenant_product_menu_res__enable
belong: dicts
status: draft
anchors: [tenant_product_menu_res.enable]
sources: ['database_profile:tenant_product_menu_res.enable', 'database_schema:tenant_product_menu_res.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_product_menu_res]
---

# tenant_product_menu_res.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_product_menu_res.enable`，表页 [[tables/tenant_product_menu_res]]。

## 取值

```ground:dict
dict: tenant_product_menu_res__enable
fields: [tenant_product_menu_res.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
