---
type: dict
title: cust_change_record.enable
page_key: cust_change_record__enable
belong: dicts
status: draft
anchors: [cust_change_record.enable]
sources: ['database_profile:cust_change_record.enable', 'database_schema:cust_change_record.enable']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_change_record.enable`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__enable
fields: [cust_change_record.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用}
triage: keep
```
