---
type: dict
title: platform_product_cust_role.company_type_code
page_key: platform_product_cust_role__company_type_code
belong: dicts
status: draft
anchors: [platform_product_cust_role.company_type_code]
sources: ['database_profile:platform_product_cust_role.company_type_code']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [platform_product_cust_role]
---

# platform_product_cust_role.company_type_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `platform_product_cust_role.company_type_code`，表页 [[tables/platform_product_cust_role]]。

## 取值

```ground:dict
dict: platform_product_cust_role__company_type_code
fields: [platform_product_cust_role.company_type_code]
values:
  CORE: {trust: proposed}
  SUPPLIER: {trust: proposed}
  PLATFORM_OPERATOR_COMPANY: {trust: proposed}
  FINANCE: {trust: proposed}
  PROJECT_COMPANY: {trust: proposed}
  CORPORATION_COMPANY: {trust: proposed}
  CORE_MANAGER: {trust: proposed}
  DEALER: {trust: proposed}
triage: hold
needs_review: true
```
