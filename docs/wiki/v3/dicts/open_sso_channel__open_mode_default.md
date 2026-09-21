---
type: dict
title: open_sso_channel.open_mode_default
page_key: open_sso_channel__open_mode_default
belong: dicts
status: draft
anchors: [open_sso_channel.open_mode_default]
sources: ['database_profile:open_sso_channel.open_mode_default', 'database_schema:open_sso_channel.open_mode_default',
  'code_path:LocalSysOpenModeEnum.java:10', 'code_path:LocalSysOpenModeEnum.java:9']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [open_sso_channel]
---

# open_sso_channel.open_mode_default

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 初审 hold：证据不足，保留待人工确认。
物理列 `open_sso_channel.open_mode_default`，表页 [[tables/open_sso_channel]]。

## 取值

```ground:dict
dict: open_sso_channel__open_mode_default
fields: [open_sso_channel.open_mode_default]
values:
  EMBED: {trust: confirmed, label: iframe 嵌入, evidence: 'code_path:LocalSysOpenModeEnum.java:10'}
  TOP: {trust: confirmed, label: 顶层打开（已废弃，龙腾不使用）, evidence: 'code_path:LocalSysOpenModeEnum.java:9'}
triage: hold
needs_review: true
```
