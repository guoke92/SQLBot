---
type: dict
title: tenant_product.platform_product_code
page_key: tenant_product__platform_product_code
belong: dicts
status: draft
anchors: [tenant_product.platform_product_code]
sources: ['database_profile:tenant_product.platform_product_code']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.platform_product_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_product.platform_product_code`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__platform_product_code
fields: [tenant_product.platform_product_code]
values:
  ACFLOW: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
  ORDER: {trust: proposed}
  BEECREDIT: {trust: proposed}
  VOUCHER: {trust: proposed}
  DRAFTQA: {trust: proposed}
  STORAGE: {trust: proposed}
  DRAFT: {trust: proposed}
triage: hold
needs_review: true
```
