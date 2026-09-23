---
type: dict
title: open_sso_channel.enable
page_key: open_sso_channel__enable
belong: dicts
status: draft
anchors: [open_sso_channel.enable]
sources: ['database_profile:open_sso_channel.enable', 'database_schema:open_sso_channel.enable']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [open_sso_channel]
---

# open_sso_channel.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `open_sso_channel.enable`，表页 [[tables/open_sso_channel]]。

## 取值

```ground:dict
dict: open_sso_channel__enable
fields: [open_sso_channel.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用}
triage: keep
```
