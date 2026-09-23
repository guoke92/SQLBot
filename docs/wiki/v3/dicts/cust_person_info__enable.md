---
type: dict
title: cust_person_info.enable
page_key: cust_person_info__enable
belong: dicts
status: draft
anchors: [cust_person_info.enable]
sources: ['database_profile:cust_person_info.enable', 'database_schema:cust_person_info.enable']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_person_info.enable`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__enable
fields: [cust_person_info.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用}
triage: keep
```
