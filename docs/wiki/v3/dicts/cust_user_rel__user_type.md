---
type: dict
title: cust_user_rel.user_type
page_key: cust_user_rel__user_type
belong: dicts
status: draft
anchors: [cust_user_rel.user_type]
sources: ['database_profile:cust_user_rel.user_type']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_user_rel]
---

# cust_user_rel.user_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_user_rel.user_type`，表页 [[tables/cust_user_rel]]。

## 取值

```ground:dict
dict: cust_user_rel__user_type
fields: [cust_user_rel.user_type]
values:
  admin: {trust: proposed}
triage: keep
```
