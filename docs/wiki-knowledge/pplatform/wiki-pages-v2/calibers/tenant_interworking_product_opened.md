---
type: caliber
title: 口径：租户互通产品已开通
page_key: tenant_interworking_product_opened
domain: 互通产品
status: draft
aliases: [租户互通产品已开通]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProductOpenStatusEnum
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_interworking_product]] 中已开通的记录，写值复用 [[ProductOpenStatusEnum]] 的 Y，因此口径形态与 [[tenant_product_opened]] 一致，但作用对象是互通产品线。

## 需求背景
语义分析未附带需求文档锚点；互通产品线需要独立的"已开通"判定以驱动互通业务。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 租户互通产品已开通
predicate: "tenant_interworking_product.open_status = 'Y'"
scope: tenant_interworking_product
evidence: "code:ProductOpenStatusEnum 写值绑定"
```