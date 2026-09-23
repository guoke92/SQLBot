---
type: dict
title: cust_sftp.enable
page_key: cust_sftp__enable
belong: dicts
status: draft
anchors: [cust_sftp.enable]
sources: ['database_profile:cust_sftp.enable', 'database_schema:cust_sftp.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_sftp]
---

# cust_sftp.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_sftp.enable`，表页 [[tables/cust_sftp]]。

## 取值

```ground:dict
dict: cust_sftp__enable
fields: [cust_sftp.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
