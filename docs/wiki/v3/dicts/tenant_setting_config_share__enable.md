---
type: dict
title: tenant_setting_config_share.enable
page_key: tenant_setting_config_share__enable
belong: dicts
status: draft
anchors: [tenant_setting_config_share.enable]
sources: ['database_profile:tenant_setting_config_share.enable', 'database_schema:tenant_setting_config_share.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_setting_config_share]
---

# tenant_setting_config_share.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_setting_config_share.enable`，表页 [[tables/tenant_setting_config_share]]。

## 取值

```ground:dict
dict: tenant_setting_config_share__enable
fields: [tenant_setting_config_share.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
