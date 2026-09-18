---
type: dict
title: platform_product.product_status
page_key: platform_product__product_status
belong: dicts
status: draft
anchors: [platform_product.product_status]
sources: ['database_profile:platform_product.product_status', 'database_schema:platform_product.product_status',
  'code_path:ProductStatusEnum.java:24', 'code_path:ProductStatusEnum.java:20']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [platform_product]
---

# platform_product.product_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 初审 hold：证据不足，保留待人工确认。
物理列 `platform_product.product_status`，表页 [[tables/platform_product]]。

## 取值

```ground:dict
dict: platform_product__product_status
fields: [platform_product.product_status]
values:
  '1': {trust: confirmed, label: 已生效, evidence: 'code_path:ProductStatusEnum.java:24'}
  '0': {trust: confirmed, label: 待生效, evidence: 'code_path:ProductStatusEnum.java:20'}
triage: hold
needs_review: true
```
