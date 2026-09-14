---
type: caliber
title: 客户已开通产品
page_key: cust-open-product
domain: 平台产品配置
status: draft
aliases: [客户已开通产品口径, cust_auth_application OPENED]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustProductDomainService.doActiveProduct
  - code:CustGeneralProductApplication.listOpenProduct
contract_version: "0.1"
belong: calibers
---

「客户已开通产品」定义客户维度「已开通」的判定口径：`cust_auth_application.open_status = 'OPENED'`。该口径适用于查询企业已开通产品的所有场景，是客户侧产品可见性的统一收口条件。

对应状态机的迁移终点见 [[processes/cust-product-open-status]]；与租户侧同名概念的区别见 [[concepts/openStatus]]。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `CustProductDomainService.doActiveProduct` 与 `CustGeneralProductApplication.listOpenProduct` 的代码证据。

```ground:caliber
name: 客户已开通产品
predicate: "cust_auth_application.open_status = 'OPENED'"
scope: "查询企业已开通产品"
evidence: CustProductDomainService.doActiveProduct, CustGeneralProductApplication.listOpenProduct
```

## 关联

- 表：[[tables/cust_auth_application]]、[[tables/cust_company_info]]
- 状态机：[[processes/cust-product-open-status]]
- 术语：[[concepts/openStatus]]