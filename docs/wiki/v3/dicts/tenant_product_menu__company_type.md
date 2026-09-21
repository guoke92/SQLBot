---
type: dict
title: tenant_product_menu.company_type
page_key: tenant_product_menu__company_type
belong: dicts
status: draft
anchors: [tenant_product_menu.company_type]
sources: ['database_profile:tenant_product_menu.company_type']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_product_menu]
---

# tenant_product_menu.company_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_product_menu.company_type`，表页 [[tables/tenant_product_menu]]。

## 取值

```ground:dict
dict: tenant_product_menu__company_type
fields: [tenant_product_menu.company_type]
values:
  CORE: {trust: proposed}
  SUPPLIER: {trust: proposed}
  FINANCE: {trust: proposed}
  PROJECT_COMPANY: {trust: proposed}
  PLATFORM_OPERATOR_COMPANY: {trust: proposed}
  CORPORATION_COMPANY: {trust: proposed}
  PLATFORM_OPERATOR: {trust: proposed}
  DEALER: {trust: proposed}
  CORE_MANAGER: {trust: proposed}
triage: keep
```
