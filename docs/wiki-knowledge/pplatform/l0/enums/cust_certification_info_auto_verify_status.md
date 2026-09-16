---
type: enum
title: cust_certification_info_auto_verify_status
page_key: cust_certification_info_auto_verify_status
belong: enums
status: draft
aliases: []
anchors:
- cust_certification_info_auto_verify_status
sources:
- database_profile:cust_certification_info.auto_verify_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_certification_info_auto_verify_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_certification_info_auto_verify_status
fields:
- cust_certification_info.auto_verify_status
values:
  AUTOMATIC_AUTHENTICATION_PASSED:
    confidence: proposed
  TO_BE_VERIFIED:
    confidence: proposed
  AUTOMATIC_AUTHENTICATION_FAILED:
    confidence: proposed
ambiguous: false
```
