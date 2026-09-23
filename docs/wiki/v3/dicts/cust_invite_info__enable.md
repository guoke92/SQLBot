---
type: dict
title: cust_invite_info.enable
page_key: cust_invite_info__enable
belong: dicts
status: draft
anchors: [cust_invite_info.enable]
sources: ['database_profile:cust_invite_info.enable', 'database_schema:cust_invite_info.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_invite_info]
---

# cust_invite_info.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_invite_info.enable`，表页 [[tables/cust_invite_info]]。

## 取值

```ground:dict
dict: cust_invite_info__enable
fields: [cust_invite_info.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
