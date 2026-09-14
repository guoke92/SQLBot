---
type: caliber
title: 口径：租户产品已开通
page_key: tenant_product_opened
domain: 租户产品
status: draft
aliases: [租户产品已开通, 产品已开通]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_product]] 中"已开通"的租户产品，是 [[tenant_product_open_status]] 的终态，对应枚举 [[ProductOpenStatusEnum]] 的 Y。与开通中（[[tenant_product_opening]]）、未开通（[[tenant_product_not_opened]]）互斥。

## 需求背景
语义分析未附带需求文档锚点；该口径用于产品开通情况统计与下游产品校验，避免把开通中的租户误判为已开通。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 租户产品已开通
predicate: "tenant_product.open_status = 'Y'"
scope: tenant_product
evidence: "db+code:ProductOpenStatusEnum.Y 与 DB 分布 Y"
```