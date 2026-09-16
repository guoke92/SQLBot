---
type: enum
title: tenant_product_menu_company_type
page_key: tenant_product_menu_company_type
belong: enums
status: draft
aliases: []
anchors:
- tenant_product_menu_company_type
sources:
- database_profile:tenant_product_menu.company_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# tenant_product_menu_company_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: tenant_product_menu_company_type
fields:
- tenant_product_menu.company_type
values:
  CORE:
    confidence: proposed
  SUPPLIER:
    confidence: proposed
  FINANCE:
    confidence: proposed
  PROJECT_COMPANY:
    confidence: proposed
  PLATFORM_OPERATOR_COMPANY:
    confidence: proposed
  CORPORATION_COMPANY:
    confidence: proposed
  PLATFORM_OPERATOR:
    confidence: proposed
  DEALER:
    confidence: proposed
  CORE_MANAGER:
    confidence: proposed
ambiguous: false
```
