---
type: dict
title: cust_role_info.status
page_key: cust_role_info__status
belong: dicts
status: draft
anchors: [cust_role_info.status]
sources: ['database_profile:cust_role_info.status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_role_info]
---

# cust_role_info.status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_role_info.status`，表页 [[tables/cust_role_info]]。

## 取值

```ground:dict
dict: cust_role_info__status
fields: [cust_role_info.status]
values:
  ADD: {trust: proposed}
  EFFECT: {trust: proposed}
  WRITEOFF: {trust: proposed}
  FREEZE: {trust: proposed}
triage: keep
```
