---
type: dict
title: cust_company_info.cust_build_status
page_key: cust_company_info__cust_build_status
belong: dicts
status: draft
anchors: [cust_company_info.cust_build_status]
sources: ['database_profile:cust_company_info.cust_build_status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.cust_build_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_company_info.cust_build_status`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__cust_build_status
fields: [cust_company_info.cust_build_status]
values:
  BUILD_SUCCESS: {trust: proposed}
  INIT: {trust: proposed}
  CUST_CONFIRM_AWAIT: {trust: proposed}
  BUILD_FAIL: {trust: proposed}
  CUST_BUILDING: {trust: proposed}
  CUST_CHANGE: {trust: proposed}
  AWAIT_CUST_CONFIRM: {trust: proposed}
  BUILD_ACTIVATE: {trust: proposed}
  BUILD_BACK: {trust: proposed}
  BUILDING: {trust: proposed}
  CUST_AUDIT_AWAIT: {trust: proposed}
  CUST_BUILD_SUCCESS: {trust: proposed}
triage: keep
```
