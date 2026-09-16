---
type: enum
title: cust_person_info_realname_status
page_key: cust_person_info_realname_status
belong: enums
status: draft
aliases: []
anchors:
- cust_person_info_realname_status
sources:
- database_profile:cust_person_info.realname_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_person_info_realname_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_person_info_realname_status
fields:
- cust_person_info.realname_status
values:
  TO_BE_VERIFIED:
    confidence: proposed
  AUTOMATIC_AUTHENTICATION_PASSED:
    confidence: proposed
  MANUAL_AUTHENTICATION_PASSED:
    confidence: proposed
  AUTOMATIC_AUTHENTICATION_FAILED:
    confidence: proposed
  ? ''
  : confidence: proposed
ambiguous: false
```
