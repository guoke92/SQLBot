---
type: dict
title: migratory_user_record.is_login
page_key: migratory_user_record__is_login
belong: dicts
status: draft
anchors: [migratory_user_record.is_login]
sources: ['database_profile:migratory_user_record.is_login', 'database_schema:migratory_user_record.is_login']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [migratory_user_record]
---

# migratory_user_record.is_login

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `migratory_user_record.is_login`，表页 [[tables/migratory_user_record]]。

## 取值

```ground:dict
dict: migratory_user_record__is_login
fields: [migratory_user_record.is_login]
values:
  N: {trust: proposed, label: 否}
  Y: {trust: proposed, label: 是}
triage: keep
```
