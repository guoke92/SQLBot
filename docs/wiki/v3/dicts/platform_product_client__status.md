---
type: dict
title: platform_product_client.status
page_key: platform_product_client__status
belong: dicts
status: draft
anchors: [platform_product_client.status]
sources: ['database_profile:platform_product_client.status', 'database_schema:platform_product_client.status']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [platform_product_client]
---

# platform_product_client.status

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `platform_product_client.status`，表页 [[tables/platform_product_client]]。

## 取值

```ground:dict
dict: platform_product_client__status
fields: [platform_product_client.status]
values:
  Y: {trust: proposed, label: 是}
  N: {trust: proposed, label: 否, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
