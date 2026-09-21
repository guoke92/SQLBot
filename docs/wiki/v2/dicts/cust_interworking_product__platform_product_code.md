---
type: dict
title: cust_interworking_product.platform_product_code
page_key: cust_interworking_product__platform_product_code
belong: dicts
status: draft
anchors: [cust_interworking_product.platform_product_code]
sources: ['database_profile:cust_interworking_product.platform_product_code']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_interworking_product]
---

# cust_interworking_product.platform_product_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_interworking_product.platform_product_code`，表页 [[tables/cust_interworking_product]]。

## 取值

```ground:dict
dict: cust_interworking_product__platform_product_code
fields: [cust_interworking_product.platform_product_code]
values:
  HTCP1: {trust: proposed}
  HTCP2: {trust: proposed}
  HTCP13: {trust: proposed}
  HTCP14: {trust: proposed}
  AMS: {trust: proposed}
  HTCP5: {trust: proposed}
triage: hold
needs_review: true
```
