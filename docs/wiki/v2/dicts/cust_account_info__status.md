---
type: dict
title: cust_account_info.status
page_key: cust_account_info__status
belong: dicts
status: draft
anchors: [cust_account_info.status]
sources: ['database_profile:cust_account_info.status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_account_info]
---

# cust_account_info.status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_account_info.status`，表页 [[tables/cust_account_info]]。

## 取值

```ground:dict
dict: cust_account_info__status
fields: [cust_account_info.status]
values:
  INIT: {trust: proposed}
triage: keep
```
