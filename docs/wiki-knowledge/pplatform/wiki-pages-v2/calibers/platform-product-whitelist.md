---
type: caliber
title: 平台产品白名单过滤
page_key: platform-product-whitelist
domain: 平台产品配置
status: draft
aliases: [白名单过滤口径, platformLimitProductSupport]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductController.filterLimitProduct
  - code:ClientAppController.listOpenProductByCompanyId
contract_version: "0.1"
belong: calibers
---

「平台产品白名单过滤」定义产品列表对外返回时的收口方式：以白名单集合 `platformLimitProductSupport` 判断产品编码是否放行（`platformLimitProductSupport.contains(productCode)`）。该口径作用于租户产品列表与已开通产品列表，属于配置驱动的过滤而非数据状态过滤。

相关实现见 [[rules/platform-product-list-filter]]。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `PlatformProductController.filterLimitProduct` 与 `ClientAppController.listOpenProductByCompanyId` 的代码证据。

```ground:caliber
name: 平台产品白名单过滤
predicate: "platformLimitProductSupport.contains(productCode)"
scope: "租户产品列表、已开通产品列表"
evidence: PlatformProductController.filterLimitProduct, ClientAppController.listOpenProductByCompanyId
```

## 关联

- 产品编码术语：[[concepts/productCode]]
- 规则：[[rules/platform-product-list-filter]]
- 表：[[tables/platform_product]]、[[tables/tenant_product]]