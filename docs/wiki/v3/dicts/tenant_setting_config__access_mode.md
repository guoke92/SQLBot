---
type: dict
title: tenant_setting_config.access_mode
page_key: tenant_setting_config__access_mode
belong: dicts
status: draft
anchors: [tenant_setting_config.access_mode]
sources: ['database_profile:tenant_setting_config.access_mode']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_setting_config]
---

# tenant_setting_config.access_mode

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_setting_config.access_mode`，表页 [[tables/tenant_setting_config]]。

## 取值

```ground:dict
dict: tenant_setting_config__access_mode
fields: [tenant_setting_config.access_mode]
values:
  DIRECT_INIT: {trust: proposed}
triage: hold
needs_review: true
```
