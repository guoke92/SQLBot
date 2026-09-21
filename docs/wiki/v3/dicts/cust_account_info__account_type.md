---
type: dict
title: cust_account_info.account_type
page_key: cust_account_info__account_type
belong: dicts
status: draft
anchors: [cust_account_info.account_type]
sources: ['database_profile:cust_account_info.account_type', 'database_schema:cust_account_info.account_type',
  'code_path:AccountTypeEnum.java:15', 'code_path:AccountTypeEnum.java:18']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_account_info]
---

# cust_account_info.account_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_account_info.account_type`，表页 [[tables/cust_account_info]]。

## 取值

```ground:dict
dict: cust_account_info__account_type
fields: [cust_account_info.account_type]
values:
  BANK: {trust: proposed}
  OPERATION_FEE_ACCOUNT: {trust: proposed}
  '1': {trust: confirmed, label: 银行, evidence: 'code_path:AccountTypeEnum.java:15'}
  received: {trust: confirmed, label: 收款, evidence: 'code_path:AccountTypeEnum.java:18'}
triage: keep
```
