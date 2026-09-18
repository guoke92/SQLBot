---
type: dict
title: tenant_setting_config_share.source
page_key: tenant_setting_config_share__source
belong: dicts
status: draft
anchors: [tenant_setting_config_share.source]
sources: ['database_profile:tenant_setting_config_share.source']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_setting_config_share]
---

# tenant_setting_config_share.source

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_setting_config_share.source`，表页 [[tables/tenant_setting_config_share]]。

## 取值

```ground:dict
dict: tenant_setting_config_share__source
fields: [tenant_setting_config_share.source]
values:
  ACFLOW: {trust: proposed}
triage: hold
needs_review: true
```
