---
type: dict
title: cust_interworking_product.agree_authorization_flag
page_key: cust_interworking_product__agree_authorization_flag
belong: dicts
status: draft
anchors: [cust_interworking_product.agree_authorization_flag]
sources: ['database_profile:cust_interworking_product.agree_authorization_flag', 'database_schema:cust_interworking_product.agree_authorization_flag']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_interworking_product]
---

# cust_interworking_product.agree_authorization_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_interworking_product.agree_authorization_flag`，表页 [[tables/cust_interworking_product]]。

## 取值

```ground:dict
dict: cust_interworking_product__agree_authorization_flag
fields: [cust_interworking_product.agree_authorization_flag]
values:
  N: {trust: proposed, label: 否}
  Y: {trust: proposed, label: 是, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
