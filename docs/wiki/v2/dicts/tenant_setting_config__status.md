---
type: dict
title: tenant_setting_config.status
page_key: tenant_setting_config__status
belong: dicts
status: draft
anchors: [tenant_setting_config.status]
sources: ['database_profile:tenant_setting_config.status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_setting_config]
---

# tenant_setting_config.status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_setting_config.status`，表页 [[tables/tenant_setting_config]]。

## 取值

```ground:dict
dict: tenant_setting_config__status
fields: [tenant_setting_config.status]
values:
  N: {trust: proposed}
  Y: {trust: proposed}
triage: keep
```
