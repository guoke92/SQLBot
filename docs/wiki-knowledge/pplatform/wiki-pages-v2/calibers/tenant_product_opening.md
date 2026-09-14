---
type: caliber
title: 口径：租户产品开通中
page_key: tenant_product_opening
domain: 租户产品
status: draft
aliases: [租户产品开通中, 产品开通中]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:ProductOpenStatusEnum
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_product]] 中处于"开通中"的记录，对应 [[ProductOpenStatusEnum]] 的 P，由多级产品开通回调期间的中间态产生，见 [[tenant_product_open_status]]。

## 需求背景
语义分析未附带需求文档锚点；该口径用于识别已发起但尚未回调成功的产品开通，避免误计为已开通（[[tenant_product_opened]]）。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 租户产品开通中
predicate: "tenant_product.open_status = 'P'"
scope: tenant_product
evidence: "db+code:ProductOpenStatusEnum.P 与 DB 分布 P"
```