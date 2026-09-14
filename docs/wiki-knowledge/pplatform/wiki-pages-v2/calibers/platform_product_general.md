---
type: caliber
title: 口径：平台通用产品类型
page_key: platform_product_general
domain: 租户产品
status: draft
aliases: [平台通用产品类型]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:PlatformProductTypeEnum
contract_version: "0.1"
belong: calibers
---

判定 [[platform_product]] 中属于通用产品线的产品，对应 [[PlatformProductTypeEnum]] 的 GENERAL，用于通用产品查询；与 [[platform_product_interworking]] 互斥。

## 需求背景
语义分析未附带需求文档锚点；产品查询按类型分流是 [[tenant_product_term]] 与 [[interworking_product_term]] 边界的技术实现。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 平台通用产品类型
predicate: "platform_product.product_type = 'GENERAL'"
scope: platform_product
evidence: "code:PlatformProductTypeEnum.GENERAL 用于通用产品查询"
```