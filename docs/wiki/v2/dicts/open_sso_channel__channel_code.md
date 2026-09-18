---
type: dict
title: open_sso_channel.channel_code
page_key: open_sso_channel__channel_code
belong: dicts
status: draft
anchors: [open_sso_channel.channel_code]
sources: ['database_profile:open_sso_channel.channel_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [open_sso_channel]
---

# open_sso_channel.channel_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `open_sso_channel.channel_code`，表页 [[tables/open_sso_channel]]。

## 取值

```ground:dict
dict: open_sso_channel__channel_code
fields: [open_sso_channel.channel_code]
values:
  longteng: {trust: proposed}
  jingke: {trust: proposed}
triage: hold
needs_review: true
```
