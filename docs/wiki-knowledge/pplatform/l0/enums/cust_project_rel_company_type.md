---
type: enum
title: cust_project_rel_company_type
page_key: cust_project_rel_company_type
belong: enums
status: draft
aliases: []
anchors:
- cust_project_rel_company_type
sources:
- database_profile:cust_project_rel.company_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_project_rel_company_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_project_rel_company_type
fields:
- cust_project_rel.company_type
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
  PLATFORM_OPREATOR_COMPANY:
    confidence: proposed
ambiguous: false
```
