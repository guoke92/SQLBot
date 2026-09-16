---
type: enum
title: cust_company_info_check_status
page_key: cust_company_info_check_status
belong: enums
status: draft
aliases: []
anchors:
- cust_company_info_check_status
sources:
- database_profile:cust_company_info.check_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_company_info_check_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_company_info_check_status
fields:
- cust_company_info.check_status
values:
  CUST_CHECK_PASS:
    confidence: proposed
  CUST_CHECK_BACKTOCUSTOM:
    confidence: proposed
  CUST_CHECK_REJECT:
    confidence: proposed
  CUST_CHECK_CHECKING:
    confidence: proposed
  CUST_CHECK_INIT:
    confidence: proposed
  EFFECT:
    confidence: proposed
ambiguous: false
```
