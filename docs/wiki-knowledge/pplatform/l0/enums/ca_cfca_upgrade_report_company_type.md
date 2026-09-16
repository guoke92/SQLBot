---
type: enum
title: ca_cfca_upgrade_report_company_type
page_key: ca_cfca_upgrade_report_company_type
belong: enums
status: draft
aliases: []
anchors:
- ca_cfca_upgrade_report_company_type
sources:
- database_profile:ca_cfca_upgrade_report.company_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# ca_cfca_upgrade_report_company_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: ca_cfca_upgrade_report_company_type
fields:
- ca_cfca_upgrade_report.company_type
values:
  CORE:
    confidence: proposed
  SUPPLIER:
    confidence: proposed
  PLATFORM_COMPANY:
    confidence: proposed
  PROJECT_COMPANY:
    confidence: proposed
  PLATFORM_OPERATOR_COMPANY:
    confidence: proposed
  FINANCE:
    confidence: proposed
ambiguous: false
```
