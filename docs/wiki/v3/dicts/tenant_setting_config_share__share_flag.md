---
type: dict
title: tenant_setting_config_share.share_flag
page_key: tenant_setting_config_share__share_flag
belong: dicts
status: draft
anchors: [tenant_setting_config_share.share_flag]
sources: ['database_profile:tenant_setting_config_share.share_flag', 'database_schema:tenant_setting_config_share.share_flag']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_setting_config_share]
---

# tenant_setting_config_share.share_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_setting_config_share.share_flag`，表页 [[tables/tenant_setting_config_share]]。

## 取值

```ground:dict
dict: tenant_setting_config_share__share_flag
fields: [tenant_setting_config_share.share_flag]
values:
  N: {trust: proposed, label: 否}
  Y: {trust: proposed, label: 是, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
