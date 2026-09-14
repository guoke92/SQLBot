---
type: caliber
title: 口径：有效租户产品
page_key: valid_tenant_product
domain: 租户产品
status: draft
aliases: [有效租户产品]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_product]] 中未被逻辑删除的记录。该口径与开通状态口径（[[tenant_product_opened]] 等）正交，是查询 [[tenant_project]] 产品维度时的前置过滤。

## 需求背景
语义分析未附带需求文档锚点；`enable` 为全表逻辑有效标记，用于统一逻辑删除语义。

## 版本演进
语义分析未记录该口径的版本演进；DB 实测 `enable` 全为 Y，暂无 N 的实测样本。

```ground:caliber
name: 有效租户产品
predicate: "tenant_product.enable = 'Y'"
scope: tenant_product
evidence: "db:enable 全为 Y"
```