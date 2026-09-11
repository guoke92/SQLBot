---
type: rule
title: 平台产品保存前置校验
page_key: rules/platform-product-save-check
domain: 平台产品配置
status: draft
aliases: [产品保存校验, checkBeforeSave]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductApplication.checkBeforeSave
  - code:PlatformProductDomainService.checkBeforeSave
contract_version: "0.1"
---

保存或更新平台产品前，系统执行前置校验：产品基本信息合法性、产品 code 唯一性、产品类型枚举有效性等。校验失败抛出 BaseException 阻断保存。

该规则的字段落点为 [[tables/platform_product]] 的 `product_code` 与 `product_type`；编码术语见 [[concepts/productCode]]，类型口径见 [[calibers/general-product-scope]]。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `PlatformProductApplication.checkBeforeSave` → `PlatformProductDomainService.checkBeforeSave` 的调用链证据。

```ground:rule
name: 平台产品保存前置校验
content: "保存或更新平台产品前，校验产品基本信息合法性、产品 code 唯一性、产品类型枚举有效性等。"
impact: "校验失败抛出 BaseException 阻断保存。"
field_targets:
  - platform_product.product_code
  - platform_product.product_type
evidence: PlatformProductApplication.checkBeforeSave -> PlatformProductDomainService.checkBeforeSave
```

## 关联

- 表：[[tables/platform_product]]
- 术语：[[concepts/productCode]]
- 口径：[[calibers/general-product-scope]]