---
type: dict
title: tenant_setting_config.customer_card_type
page_key: tenant_setting_config__customer_card_type
belong: dicts
status: draft
anchors: [tenant_setting_config.customer_card_type]
sources: ['database_profile:tenant_setting_config.customer_card_type', 'database_schema:tenant_setting_config.customer_card_type']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_setting_config]
---

# tenant_setting_config.customer_card_type

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_setting_config.customer_card_type`，表页 [[tables/tenant_setting_config]]。

## 取值

```ground:dict
dict: tenant_setting_config__customer_card_type
fields: [tenant_setting_config.customer_card_type]
values:
  WX_WORK: {trust: proposed, label: 发送企微名片, evidence: 'database_schema:tenant_setting_config.customer_card_type'}
  WX: {trust: proposed, label: 发送微信名片, evidence: 'database_schema:tenant_setting_config.customer_card_type'}
triage: keep
```
