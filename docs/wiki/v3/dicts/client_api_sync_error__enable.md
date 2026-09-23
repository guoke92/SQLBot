---
type: dict
title: client_api_sync_error.enable
page_key: client_api_sync_error__enable
belong: dicts
status: draft
anchors: [client_api_sync_error.enable]
sources: ['database_profile:client_api_sync_error.enable', 'database_schema:client_api_sync_error.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [client_api_sync_error]
---

# client_api_sync_error.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `client_api_sync_error.enable`，表页 [[tables/client_api_sync_error]]。

## 取值

```ground:dict
dict: client_api_sync_error__enable
fields: [client_api_sync_error.enable]
values:
  N: {trust: proposed, label: 停用}
  Y: {trust: proposed, label: 启用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
