---
type: caliber
title: 口径：租户产品未开通
page_key: tenant_product_not_opened
domain: 租户产品
status: draft
aliases: [租户产品未开通, 产品未开通]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_product]] 中"未开通"的记录，对应 [[ProductOpenStatusEnum]] 的 N；取消开通会回退到该态（见 [[tenant_product_open_status]]）。

## 需求背景
语义分析未附带需求文档锚点；该口径是产品开通引导与权限判定的默认态。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 租户产品未开通
predicate: "tenant_product.open_status = 'N'"
scope: tenant_product
evidence: "db+code:ProductOpenStatusEnum.N 与 DB 分布 N"
```