---
type: caliber
title: 互通产品
page_key: interworking_product
domain: 平台产品配置
status: draft
aliases: [INTERWORKING, 互通类产品]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「互通产品」是 [[platform_product]] 的 `product_type = 'INTERWORKING'` 口径，落到互通产品扩展点分支。

## 需求背景

与 [[general_product]] 并列构成产品分类全集；分类值在保存前由 `checkBeforeSave` 校验（[[product_code_name_unique]]）。

## 版本演进

- 代码枚举 `PlatformProductTypeEnum.INTERWORKING` 与 DB 落库值同值（DB 计数 11，verdict=confirm）。

```ground:caliber
name: 互通产品
predicate: "platform_product.product_type = 'INTERWORKING'"
scope: 互通产品扩展点
evidence: code
```

关联：[[platform_product]]、[[general_product]]、[[product_code_name_unique]]