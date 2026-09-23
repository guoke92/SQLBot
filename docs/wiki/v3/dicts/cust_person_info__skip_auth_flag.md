---
type: dict
title: cust_person_info.skip_auth_flag
page_key: cust_person_info__skip_auth_flag
belong: dicts
status: draft
anchors: [cust_person_info.skip_auth_flag]
sources: ['database_profile:cust_person_info.skip_auth_flag', 'database_schema:cust_person_info.skip_auth_flag']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.skip_auth_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_person_info.skip_auth_flag`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__skip_auth_flag
fields: [cust_person_info.skip_auth_flag]
values:
  N: {trust: proposed, label: 否}
  Y: {trust: proposed, label: 是}
triage: keep
```
