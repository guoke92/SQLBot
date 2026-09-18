---
type: dict
title: cust_person_info.user_type
page_key: cust_person_info__user_type
belong: dicts
status: draft
anchors: [cust_person_info.user_type]
sources: ['database_profile:cust_person_info.user_type', 'database_schema:cust_person_info.user_type',
  'code_path:UserTypeEnum.java:15', 'code_path:UserTypeEnum.java:16', 'code_path:UserTypeEnum.java:17']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.user_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_person_info.user_type`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__user_type
fields: [cust_person_info.user_type]
values:
  accountAdmin: {trust: confirmed, label: 管理员, evidence: 'code_path:UserTypeEnum.java:15'}
  accountNormal: {trust: confirmed, label: 经办人, evidence: 'code_path:UserTypeEnum.java:16'}
  accountGuest: {trust: confirmed, label: 游客, evidence: 'code_path:UserTypeEnum.java:17'}
triage: keep
```
