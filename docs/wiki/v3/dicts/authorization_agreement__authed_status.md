---
type: dict
title: authorization_agreement.authed_status
page_key: authorization_agreement__authed_status
belong: dicts
status: draft
anchors: [authorization_agreement.authed_status]
sources: ['database_profile:authorization_agreement.authed_status']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [authorization_agreement]
---

# authorization_agreement.authed_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `authorization_agreement.authed_status`，表页 [[tables/authorization_agreement]]。

## 取值

```ground:dict
dict: authorization_agreement__authed_status
fields: [authorization_agreement.authed_status]
values:
  N: {trust: proposed}
  Y: {trust: proposed}
triage: keep
```
