---
type: rule
title: 平台产品列表过滤
page_key: platform-product-list-filter
domain: 平台产品配置
status: draft
aliases: [产品列表过滤, listTenantProduct 过滤]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductController.listTenantProduct
contract_version: "0.1"
belong: rules
---

非 AGW 端调用时，产品列表按当前租户已开通产品列表过滤，并通过 Nacos 配置 `platform.limit.product.support` 白名单进一步过滤，返回过滤后的产品列表。

该规则组合了两个口径：租户已开通范围见 [[calibers/tenant-open-product]]，白名单判定见 [[calibers/platform-product-whitelist]]；字段落点为 [[tables/tenant_product]] 与 [[tables/platform_product]] 的 `product_code`。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `PlatformProductController.listTenantProduct` 的代码证据。

```ground:rule
name: 平台产品列表过滤
content: "非 AGW 端调用时，按当前租户已开通产品列表过滤，并通过 Nacos 配置 platform.limit.product.support 白名单过滤。"
impact: "返回过滤后的产品列表。"
field_targets:
  - tenant_product
  - platform_product.product_code
evidence: PlatformProductController.listTenantProduct
```

## 关联

- 口径：[[calibers/tenant-open-product]]、[[calibers/platform-product-whitelist]]
- 表：[[tables/tenant_product]]、[[tables/platform_product]]
- 术语：[[concepts/productCode]]