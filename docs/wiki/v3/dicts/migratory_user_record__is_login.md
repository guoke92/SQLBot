---
type: dict
title: migratory_user_record.is_login
page_key: migratory_user_record__is_login
belong: dicts
status: draft
anchors: [migratory_user_record.is_login]
sources: ['database_profile:migratory_user_record.is_login']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [migratory_user_record]
---

# migratory_user_record.is_login

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `migratory_user_record.is_login`，表页 [[tables/migratory_user_record]]。

## 取值

```ground:dict
dict: migratory_user_record__is_login
fields: [migratory_user_record.is_login]
values:
  N: {trust: proposed}
  Y: {trust: proposed}
triage: hold
needs_review: true
```
