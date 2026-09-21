---
type: dict
title: cust_account_info.auth_state
page_key: cust_account_info__auth_state
belong: dicts
status: draft
anchors: [cust_account_info.auth_state]
sources: ['database_profile:cust_account_info.auth_state']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_account_info]
---

# cust_account_info.auth_state

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_account_info.auth_state`，表页 [[tables/cust_account_info]]。

## 取值

```ground:dict
dict: cust_account_info__auth_state
fields: [cust_account_info.auth_state]
values:
  APPLY_00: {trust: proposed}
  APPLY_40: {trust: proposed}
  APPLY_20: {trust: proposed}
triage: keep
```
