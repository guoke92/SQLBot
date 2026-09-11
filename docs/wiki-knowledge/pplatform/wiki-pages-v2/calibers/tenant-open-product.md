---
type: caliber
title: 租户已开通产品
page_key: calibers/tenant-open-product
domain: 平台产品配置
status: draft
aliases: [租户已开通产品口径, tenant_product open_status=Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.listOpenByTenant
  - code:TenantProductDao.listOpenByTenant
contract_version: "0.1"
---

「租户已开通产品」定义租户维度「已开通」的判定口径：`tenant_product.open_status = 'Y'`。该口径适用于查询租户已开通产品的场景，是租户产品列表过滤（[[rules/platform-product-list-filter]]）的前置数据范围。

对应状态机的终态见 [[processes/tenant-product-open-status]]；与客户侧口径（[[calibers/cust-open-product]]）枚举值不同，注意区分。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `TenantProductApplication.listOpenByTenant` 与 `TenantProductDao.listOpenByTenant` 的代码证据。

```ground:caliber
name: 租户已开通产品
predicate: "tenant_product.open_status = 'Y'"
scope: "查询租户已开通产品"
evidence: TenantProductApplication.listOpenByTenant, TenantProductDao.listOpenByTenant
```

## 关联

- 表：[[tables/tenant_product]]
- 状态机：[[processes/tenant-product-open-status]]
- 术语：[[concepts/openStatus]]
- 相关口径：[[calibers/cust-open-product]]