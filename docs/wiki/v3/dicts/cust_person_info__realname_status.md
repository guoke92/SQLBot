---
type: dict
title: cust_person_info.realname_status
page_key: cust_person_info__realname_status
belong: dicts
status: draft
anchors: [cust_person_info.realname_status]
sources: ['database_profile:cust_person_info.realname_status']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.realname_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_person_info.realname_status`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__realname_status
fields: [cust_person_info.realname_status]
values:
  TO_BE_VERIFIED: {trust: proposed}
  AUTOMATIC_AUTHENTICATION_PASSED: {trust: proposed}
  MANUAL_AUTHENTICATION_PASSED: {trust: proposed}
  AUTOMATIC_AUTHENTICATION_FAILED: {trust: proposed}
triage: keep
```
