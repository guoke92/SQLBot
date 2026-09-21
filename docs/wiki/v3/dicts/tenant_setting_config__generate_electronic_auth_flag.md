---
type: dict
title: tenant_setting_config.generate_electronic_auth_flag
page_key: tenant_setting_config__generate_electronic_auth_flag
belong: dicts
status: draft
anchors: [tenant_setting_config.generate_electronic_auth_flag]
sources: ['database_profile:tenant_setting_config.generate_electronic_auth_flag',
  'database_schema:tenant_setting_config.generate_electronic_auth_flag']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_setting_config]
---

# tenant_setting_config.generate_electronic_auth_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_setting_config.generate_electronic_auth_flag`，表页 [[tables/tenant_setting_config]]。

## 取值

```ground:dict
dict: tenant_setting_config__generate_electronic_auth_flag
fields: [tenant_setting_config.generate_electronic_auth_flag]
values:
  N: {trust: proposed, label: 否, evidence: 'database_schema:tenant_setting_config.generate_electronic_auth_flag'}
  Y: {trust: proposed, label: 是, evidence: 'database_schema:tenant_setting_config.generate_electronic_auth_flag'}
  '0': {trust: proposed}
triage: keep
```
