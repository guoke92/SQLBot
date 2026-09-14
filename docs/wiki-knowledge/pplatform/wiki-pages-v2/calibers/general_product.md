---
type: caliber
title: 通用产品
page_key: general_product
domain: 平台产品配置
status: draft
aliases: [GENERAL, 通用类产品]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「通用产品」是 [[platform_product]] 的 `product_type = 'GENERAL'` 口径，用于 `listPlatformProduct` 与客户产品扩展点的 GENERAL 分支，并参与「进入产品项目生效校验」的类型前置判断（[[project_effective_check]]）。

## 需求背景

通用产品在 `multiple_project_flag='Y'` 时需校验企业关联项目生效状态，未命中返回「暂无操作权限」。

## 版本演进

- 代码枚举 `PlatformProductTypeEnum.GENERAL` 与 DB 落库值同值（DB 计数 9，verdict=confirm）。

```ground:caliber
name: 通用产品
predicate: "platform_product.product_type = 'GENERAL'"
scope: listPlatformProduct/客户产品扩展点 GENERAL
evidence: code
```

关联：[[platform_product]]、[[interworking_product]]、[[project_effective_check]]