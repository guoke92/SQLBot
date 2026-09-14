---
type: caliber
title: 口径：平台互通产品类型
page_key: platform_product_interworking
domain: 租户产品
status: draft
aliases: [平台互通产品类型]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:PlatformProductTypeEnum
contract_version: "0.1"
belong: calibers
---

判定 [[platform_product]] 中属于互通产品线的产品，对应 [[PlatformProductTypeEnum]] 的 INTERWORKING，用于互通产品查询；与 [[platform_product_general]] 互斥。

## 需求背景
语义分析未附带需求文档锚点；产品查询需按类型分流，避免互通产品混入通用产品查询。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 平台互通产品类型
predicate: "platform_product.product_type = 'INTERWORKING'"
scope: platform_product
evidence: "code:PlatformProductTypeEnum.INTERWORKING 用于互通产品查询"
```