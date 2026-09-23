---
type: dict
title: cust_access_secret.enable
page_key: cust_access_secret__enable
belong: dicts
status: draft
anchors: [cust_access_secret.enable]
sources: ['database_profile:cust_access_secret.enable', 'database_schema:cust_access_secret.enable']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_access_secret]
---

# cust_access_secret.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_access_secret.enable`，表页 [[tables/cust_access_secret]]。

## 取值

```ground:dict
dict: cust_access_secret__enable
fields: [cust_access_secret.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用}
triage: keep
```
