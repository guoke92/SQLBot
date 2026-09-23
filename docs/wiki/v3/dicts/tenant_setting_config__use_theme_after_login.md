---
type: dict
title: tenant_setting_config.use_theme_after_login
page_key: tenant_setting_config__use_theme_after_login
belong: dicts
status: draft
anchors:
- tenant_setting_config.use_theme_after_login
sources:
- database_profile:tenant_setting_config.use_theme_after_login
- database_schema:tenant_setting_config.use_theme_after_login
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- tenant_setting_config
---
# tenant_setting_config.use_theme_after_login

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `tenant_setting_config.use_theme_after_login`，表页 [[tables/tenant_setting_config]]。

## 取值

```ground:dict
dict: tenant_setting_config__use_theme_after_login
fields:
- tenant_setting_config.use_theme_after_login
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
triage: keep
```
