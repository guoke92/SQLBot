---
type: dict
title: ca_cfca_upgrade_report.company_type
page_key: ca_cfca_upgrade_report__company_type
belong: dicts
status: draft
anchors: [ca_cfca_upgrade_report.company_type]
sources: ['database_profile:ca_cfca_upgrade_report.company_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [ca_cfca_upgrade_report]
---

# ca_cfca_upgrade_report.company_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `ca_cfca_upgrade_report.company_type`，表页 [[tables/ca_cfca_upgrade_report]]。

## 取值

```ground:dict
dict: ca_cfca_upgrade_report__company_type
fields: [ca_cfca_upgrade_report.company_type]
values:
  CORE: {trust: proposed}
  SUPPLIER: {trust: proposed}
  PLATFORM_COMPANY: {trust: proposed}
  PROJECT_COMPANY: {trust: proposed}
  PLATFORM_OPERATOR_COMPANY: {trust: proposed}
  FINANCE: {trust: proposed}
triage: keep
```
