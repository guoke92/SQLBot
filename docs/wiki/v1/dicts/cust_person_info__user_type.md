---
type: dict
title: cust_person_info.user_type
page_key: cust_person_info__user_type
belong: dicts
status: draft
anchors: [cust_person_info.user_type]
sources: ['database_profile:cust_person_info.user_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.user_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_person_info.user_type`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__user_type
fields: [cust_person_info.user_type]
values:
  accountAdmin: {trust: proposed}
  accountNormal: {trust: proposed}
  accountGuest: {trust: proposed}
triage: keep
```
