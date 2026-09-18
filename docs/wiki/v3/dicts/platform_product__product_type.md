---
type: dict
title: platform_product.product_type
page_key: platform_product__product_type
belong: dicts
status: draft
anchors: [platform_product.product_type]
sources: ['database_profile:platform_product.product_type', 'database_schema:platform_product.product_type',
  'code_path:PlatformProductTypeEnum.java:24', 'code_path:PlatformProductTypeEnum.java:20',
  'code_path:PlatformProductTypeEnum.java:28']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [platform_product]
---

# platform_product.product_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `platform_product.product_type`，表页 [[tables/platform_product]]。

## 取值

```ground:dict
dict: platform_product__product_type
fields: [platform_product.product_type]
values:
  INTERWORKING: {trust: confirmed, label: 互通产品, evidence: 'code_path:PlatformProductTypeEnum.java:24'}
  GENERAL: {trust: confirmed, label: 通用产品, evidence: 'code_path:PlatformProductTypeEnum.java:20'}
  '2': {trust: confirmed, label: 全部产品, evidence: 'code_path:PlatformProductTypeEnum.java:28'}
triage: keep
```
