---
type: enum
title: cust_account_info_account_type
page_key: cust_account_info_account_type
belong: enums
status: draft
aliases: []
anchors:
- cust_account_info_account_type
sources:
- database_profile:cust_account_info.account_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_account_info_account_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_account_info_account_type
fields:
- cust_account_info.account_type
values:
  BANK:
    confidence: proposed
  OPERATION_FEE_ACCOUNT:
    confidence: proposed
  '1':
    confidence: proposed
  received:
    confidence: proposed
ambiguous: false
```
