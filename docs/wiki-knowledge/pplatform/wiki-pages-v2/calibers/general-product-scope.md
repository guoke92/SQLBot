---
type: caliber
title: 通用产品范围
page_key: calibers/general-product-scope
domain: 平台产品配置
status: draft
aliases: [通用产品口径, GENERAL 产品范围]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductController.listPlatformProduct
contract_version: "0.1"
---

「通用产品范围」定义平台产品列表查询中如何界定通用产品。其判定条件为 [[tables/platform_product]] 的 `product_type = 'GENERAL'`，与 INTERWORKING（互通产品）相对。

该口径是后续多条规则的共同前提：只有「多项目 + 通用产品」才会触发 [[rules/goto-product-project-status-check]]，只有「多角色 + 通用产品」才会触发 [[rules/goto-product-company-type-check]]。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `PlatformProductController.listPlatformProduct` 的代码证据。

```ground:caliber
name: 通用产品范围
predicate: "platform_product.product_type = 'GENERAL'"
scope: "查询平台产品列表"
evidence: PlatformProductController.listPlatformProduct
```

## 关联

- 表：[[tables/platform_product]]
- 术语：[[concepts/productCode]]、[[concepts/custRoleCombine]]
- 规则：[[rules/goto-product-project-status-check]]、[[rules/goto-product-company-type-check]]