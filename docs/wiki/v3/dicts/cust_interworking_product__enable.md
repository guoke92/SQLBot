---
type: dict
title: cust_interworking_product.enable
page_key: cust_interworking_product__enable
belong: dicts
status: draft
anchors: [cust_interworking_product.enable]
sources: ['database_profile:cust_interworking_product.enable', 'database_schema:cust_interworking_product.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_interworking_product]
---

# cust_interworking_product.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_interworking_product.enable`，表页 [[tables/cust_interworking_product]]。

## 取值

```ground:dict
dict: cust_interworking_product__enable
fields: [cust_interworking_product.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
