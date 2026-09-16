---
type: enum
title: cust_person_info_cust_build_status
page_key: cust_person_info_cust_build_status
belong: enums
status: draft
aliases: []
anchors:
- cust_person_info_cust_build_status
sources:
- database_profile:cust_person_info.cust_build_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_person_info_cust_build_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_person_info_cust_build_status
fields:
- cust_person_info.cust_build_status
values:
  CUST_CONFIRM_AWAIT:
    confidence: proposed
  BUILD_FAIL:
    confidence: proposed
  BUILD_SUCCESS:
    confidence: proposed
  CUST_BUILDING:
    confidence: proposed
  INIT:
    confidence: proposed
ambiguous: false
```
