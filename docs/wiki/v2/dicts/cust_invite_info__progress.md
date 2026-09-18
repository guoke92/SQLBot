---
type: dict
title: cust_invite_info.progress
page_key: cust_invite_info__progress
belong: dicts
status: draft
anchors: [cust_invite_info.progress]
sources: ['database_profile:cust_invite_info.progress']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_invite_info]
---

# cust_invite_info.progress

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_invite_info.progress`，表页 [[tables/cust_invite_info]]。

## 取值

```ground:dict
dict: cust_invite_info__progress
fields: [cust_invite_info.progress]
values:
  INIT: {trust: proposed}
  CUST_CONFIRM_AWAIT: {trust: proposed}
  BUILD_SUCCESS: {trust: proposed}
  CUST_BUILDING: {trust: proposed}
  CUST_CHANGE: {trust: proposed}
  BUILD_FAIL: {trust: proposed}
  AWAIT_CUST_CONFIRM: {trust: proposed}
triage: keep
```
