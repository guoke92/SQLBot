---
type: dict
title: platform_product_cust_role.product_code
page_key: platform_product_cust_role__product_code
belong: dicts
status: draft
anchors: [platform_product_cust_role.product_code]
sources: ['database_profile:platform_product_cust_role.product_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [platform_product_cust_role]
---

# platform_product_cust_role.product_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `platform_product_cust_role.product_code`，表页 [[tables/platform_product_cust_role]]。

## 取值

```ground:dict
dict: platform_product_cust_role__product_code
fields: [platform_product_cust_role.product_code]
values:
  VOUCHER: {trust: proposed}
  STORAGE: {trust: proposed}
  CROSSBORDER: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
  ORDER: {trust: proposed}
  ACCOUNT_PRODUCT: {trust: proposed}
  ACFLOW: {trust: proposed}
  AMS: {trust: proposed}
  BEECREDIT: {trust: proposed}
  DEALER: {trust: proposed}
  DRAFTQA: {trust: proposed}
  DRAFT: {trust: proposed}
triage: keep
```
