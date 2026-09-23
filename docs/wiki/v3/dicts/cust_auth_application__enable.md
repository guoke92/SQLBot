---
type: dict
title: cust_auth_application.enable
page_key: cust_auth_application__enable
belong: dicts
status: draft
anchors: [cust_auth_application.enable]
sources: ['database_profile:cust_auth_application.enable', 'database_schema:cust_auth_application.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_auth_application]
---

# cust_auth_application.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_auth_application.enable`，表页 [[tables/cust_auth_application]]。

## 取值

```ground:dict
dict: cust_auth_application__enable
fields: [cust_auth_application.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
