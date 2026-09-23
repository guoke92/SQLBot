---
type: dict
title: cust_setting_config.enable
page_key: cust_setting_config__enable
belong: dicts
status: draft
anchors: [cust_setting_config.enable]
sources: ['database_profile:cust_setting_config.enable', 'database_schema:cust_setting_config.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_setting_config]
---

# cust_setting_config.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_setting_config.enable`，表页 [[tables/cust_setting_config]]。

## 取值

```ground:dict
dict: cust_setting_config__enable
fields: [cust_setting_config.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
