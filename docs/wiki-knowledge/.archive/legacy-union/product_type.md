---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:product-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 平台产品类型
page_key: product_type
domain: 产品与配置
aliases:
- 通用产品
- 互通产品
- 产品大类
anchors:
- product_type
---
# 平台产品类型

GENERAL=通用产品 / INTERWORKING=互通产品（互通走独立 TenantInterworkingProduct 域）。

```ground:enum
enum: product_type
fields:
- platform_product.product_type
values:
  GENERAL:
    label: 通用产品
  INTERWORKING:
    label: 互通产品
```

## 关联
- [[platform_product|platform_product]]
