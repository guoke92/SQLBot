---
type: dict
title: cust_app_channel_config.name
page_key: cust_app_channel_config__name
belong: dicts
status: draft
anchors: [cust_app_channel_config.name]
sources: ['database_profile:cust_app_channel_config.name']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_app_channel_config]
---

# cust_app_channel_config.name

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_app_channel_config.name`，表页 [[tables/cust_app_channel_config]]。

## 取值

```ground:dict
dict: cust_app_channel_config__name
fields: [cust_app_channel_config.name]
values:
  longteng: {trust: proposed}
  jingke: {trust: proposed}
triage: hold
needs_review: true
```
