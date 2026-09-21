---
type: dict
title: tenant_setting_config.source
page_key: tenant_setting_config__source
belong: dicts
status: draft
anchors: [tenant_setting_config.source]
sources: ['database_profile:tenant_setting_config.source']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_setting_config]
---

# tenant_setting_config.source

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_setting_config.source`，表页 [[tables/tenant_setting_config]]。

## 取值

```ground:dict
dict: tenant_setting_config__source
fields: [tenant_setting_config.source]
values:
  ACFLOW: {trust: proposed}
  pplatform: {trust: proposed}
triage: hold
needs_review: true
```
