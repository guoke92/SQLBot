---
type: dict
title: tenant_setting_config.need_hfive
page_key: tenant_setting_config__need_hfive
belong: dicts
status: draft
anchors: [tenant_setting_config.need_hfive]
sources: ['database_profile:tenant_setting_config.need_hfive', 'database_schema:tenant_setting_config.need_hfive']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_setting_config]
---

# tenant_setting_config.need_hfive

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_setting_config.need_hfive`，表页 [[tables/tenant_setting_config]]。

## 取值

```ground:dict
dict: tenant_setting_config__need_hfive
fields: [tenant_setting_config.need_hfive]
values:
  N: {trust: proposed, label: 否}
  Y: {trust: proposed, label: 是}
triage: keep
```
