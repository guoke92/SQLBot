---
type: enum
title: cust_company_info_cust_build_status
page_key: cust_company_info_cust_build_status
belong: enums
status: draft
aliases: []
anchors:
- cust_company_info_cust_build_status
sources:
- database_profile:cust_company_info.cust_build_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_company_info_cust_build_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_company_info_cust_build_status
fields:
- cust_company_info.cust_build_status
values:
  BUILD_SUCCESS:
    confidence: proposed
  INIT:
    confidence: proposed
  CUST_CONFIRM_AWAIT:
    confidence: proposed
  BUILD_FAIL:
    confidence: proposed
  CUST_BUILDING:
    confidence: proposed
  CUST_CHANGE:
    confidence: proposed
  AWAIT_CUST_CONFIRM:
    confidence: proposed
  BUILD_ACTIVATE:
    confidence: proposed
  BUILD_BACK:
    confidence: proposed
  BUILDING:
    confidence: proposed
  CUST_AUDIT_AWAIT:
    confidence: proposed
  CUST_BUILD_SUCCESS:
    confidence: proposed
ambiguous: false
```
