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
title: 平台产品生效状态
page_key: product_status
domain: 产品与配置
aliases:
- 产品生效
- 待生效产品
- 产品上架
- 产品状态
anchors:
- product_status
---
# 平台产品生效状态

platform_product.product_status 0=待生效 → 1=已生效（单向 effective，列表只取已生效）。

```ground:enum
enum: product_status
fields:
- platform_product.product_status
values:
  '0':
    label: 待生效
  '1':
    label: 已生效
```

## 关联
- [[platform_product|platform_product]]
