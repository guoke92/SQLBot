---
type: dict
title: cust_config_mapping.enable
page_key: cust_config_mapping__enable
belong: dicts
status: draft
anchors: [cust_config_mapping.enable]
sources: ['database_profile:cust_config_mapping.enable', 'database_schema:cust_config_mapping.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_config_mapping]
---

# cust_config_mapping.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_config_mapping.enable`，表页 [[tables/cust_config_mapping]]。

## 取值

```ground:dict
dict: cust_config_mapping__enable
fields: [cust_config_mapping.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
