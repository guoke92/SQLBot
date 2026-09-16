---
type: enum
title: tenant_product_open_status
page_key: tenant_product_open_status
belong: enums
status: draft
aliases: []
anchors:
- tenant_product_open_status
sources:
- database_profile:tenant_product.open_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# tenant_product_open_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: tenant_product_open_status
fields:
- tenant_product.open_status
values:
  Y:
    confidence: proposed
  N:
    confidence: proposed
  P:
    confidence: proposed
ambiguous: false
```
