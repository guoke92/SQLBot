---
type: enum
title: cust_role_info_role_type
page_key: cust_role_info_role_type
belong: enums
status: draft
aliases: []
anchors:
- cust_role_info_role_type
sources:
- database_profile:cust_role_info.role_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_role_info_role_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_role_info_role_type
fields:
- cust_role_info.role_type
values:
  SUPPLIER:
    confidence: proposed
  CORE:
    confidence: proposed
  FINANCE:
    confidence: proposed
  PROJECT_COMPANY:
    confidence: proposed
  CORPORATION_COMPANY:
    confidence: proposed
  PLATFORM_OPERATOR_COMPANY:
    confidence: proposed
  DEALER:
    confidence: proposed
  CORE_MANAGER:
    confidence: proposed
  FACTOR_COMPANY:
    confidence: proposed
  ? ''
  : confidence: proposed
  '"SUPPLIER"':
    confidence: proposed
  '"CORE"':
    confidence: proposed
  CORE_ADMIN:
    confidence: proposed
  CORE_SUB:
    confidence: proposed
ambiguous: false
```
