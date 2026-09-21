---
type: dict
title: tenant_product.platform_product_id
page_key: tenant_product__platform_product_id
belong: dicts
status: draft
anchors: [tenant_product.platform_product_id]
sources: ['database_profile:tenant_product.platform_product_id']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.platform_product_id

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_product.platform_product_id`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__platform_product_id
fields: [tenant_product.platform_product_id]
values:
  '10': {trust: proposed}
  '2': {trust: proposed}
  '3': {trust: proposed}
  '5': {trust: proposed}
  '8': {trust: proposed}
  '26': {trust: proposed}
  '7': {trust: proposed}
  '27': {trust: proposed}
triage: hold
needs_review: true
```
