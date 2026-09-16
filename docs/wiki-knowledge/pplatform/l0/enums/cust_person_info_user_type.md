---
type: enum
title: cust_person_info_user_type
page_key: cust_person_info_user_type
belong: enums
status: draft
aliases: []
anchors:
- cust_person_info_user_type
sources:
- database_profile:cust_person_info.user_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_person_info_user_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_person_info_user_type
fields:
- cust_person_info.user_type
values:
  accountAdmin:
    confidence: proposed
  accountNormal:
    confidence: proposed
  accountGuest:
    confidence: proposed
  ? ''
  : confidence: proposed
ambiguous: false
```
