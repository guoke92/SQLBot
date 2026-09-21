---
type: dict
title: cust_person_info.cust_build_status
page_key: cust_person_info__cust_build_status
belong: dicts
status: draft
anchors: [cust_person_info.cust_build_status]
sources: ['database_profile:cust_person_info.cust_build_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.cust_build_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_person_info.cust_build_status`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__cust_build_status
fields: [cust_person_info.cust_build_status]
values:
  CUST_CONFIRM_AWAIT: {trust: proposed}
  BUILD_SUCCESS: {trust: proposed}
  BUILD_FAIL: {trust: proposed}
  CUST_BUILDING: {trust: proposed}
  INIT: {trust: proposed}
triage: keep
```
