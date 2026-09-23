---
type: dict
title: tenant_setting_config.access_mode
page_key: tenant_setting_config__access_mode
belong: dicts
status: draft
anchors: [tenant_setting_config.access_mode]
sources: ['database_profile:tenant_setting_config.access_mode', 'database_schema:tenant_setting_config.access_mode',
  'code_path:DirectInitAccessModes.java:10']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_setting_config]
---

# tenant_setting_config.access_mode

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_setting_config.access_mode`，表页 [[tables/tenant_setting_config]]。

## 取值

```ground:dict
dict: tenant_setting_config__access_mode
fields: [tenant_setting_config.access_mode]
values:
  DIRECT_INIT: {trust: confirmed, label: 方案2直推, evidence: 'code_path:DirectInitAccessModes.java:10'}
triage: keep
```
