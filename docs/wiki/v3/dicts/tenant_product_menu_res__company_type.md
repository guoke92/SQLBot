---
type: dict
title: tenant_product_menu_res.company_type
page_key: tenant_product_menu_res__company_type
belong: dicts
status: draft
anchors: [tenant_product_menu_res.company_type]
sources: ['database_profile:tenant_product_menu_res.company_type']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_product_menu_res]
---

# tenant_product_menu_res.company_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_product_menu_res.company_type`，表页 [[tables/tenant_product_menu_res]]。

## 取值

```ground:dict
dict: tenant_product_menu_res__company_type
fields: [tenant_product_menu_res.company_type]
values:
  CORPORATION_COMPANY: {trust: proposed}
  PLATFORM_OPERATOR_COMPANY: {trust: proposed}
  CORE: {trust: proposed}
  SUPPLIER: {trust: proposed}
triage: keep
```
