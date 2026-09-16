---
type: enum
title: cust_company_info_cust_source
page_key: cust_company_info_cust_source
belong: enums
status: draft
aliases: []
anchors:
- cust_company_info_cust_source
sources:
- database_profile:cust_company_info.cust_source
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_company_info_cust_source

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_company_info_cust_source
fields:
- cust_company_info.cust_source
values:
  PPLATFORM:
    confidence: proposed
  MIGRATORY:
    confidence: proposed
  PLATFORM_PUSH:
    confidence: proposed
  PLATFORM:
    confidence: proposed
ambiguous: false
```
