---
type: dict
title: cust_account_info.account_type
page_key: cust_account_info__account_type
belong: dicts
status: draft
anchors: [cust_account_info.account_type]
sources: ['database_profile:cust_account_info.account_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_account_info]
---

# cust_account_info.account_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_account_info.account_type`，表页 [[tables/cust_account_info]]。

## 取值

```ground:dict
dict: cust_account_info__account_type
fields: [cust_account_info.account_type]
values:
  BANK: {trust: proposed}
  OPERATION_FEE_ACCOUNT: {trust: proposed}
  '1': {trust: proposed}
  received: {trust: proposed}
triage: keep
```
