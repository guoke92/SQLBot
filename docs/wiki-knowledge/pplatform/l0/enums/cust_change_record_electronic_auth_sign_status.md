---
type: enum
title: cust_change_record_electronic_auth_sign_status
page_key: cust_change_record_electronic_auth_sign_status
belong: enums
status: draft
aliases: []
anchors:
- cust_change_record_electronic_auth_sign_status
sources:
- database_profile:cust_change_record.electronic_auth_sign_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_change_record_electronic_auth_sign_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_change_record_electronic_auth_sign_status
fields:
- cust_change_record.electronic_auth_sign_status
values:
  SIGNED:
    confidence: proposed
  VOIDED:
    confidence: proposed
  PENDING:
    confidence: proposed
ambiguous: false
```
