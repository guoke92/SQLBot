---
type: rule
title: 产品协议签署后激活
page_key: rules/product-agreement-activate
domain: 平台产品配置
status: draft
aliases: [协议签署激活, createProductAggrement]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustProductDomainService.createProductAggrement
  - code:CustProductDomainService.activeProduct
contract_version: "0.1"
---

根据产品协议配置决定激活路径：无需签署则直接激活；需要签署则先创建合同，签署成功后激活。激活最终将 [[tables/cust_auth_application]] 的 `open_status` 推进到已开通，对应 [[processes/cust-product-open-status]] 中 `activeProduct` 的迁移。企业是否需要电子签章由 [[tables/cust_company_info]] 的 `need_register_ca` 标识。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `CustProductDomainService.createProductAggrement` 与 `CustProductDomainService.activeProduct` 的代码证据。

```ground:rule
name: 产品协议签署后激活
content: "根据产品协议配置，无需签署则直接激活；需要签署则创建合同，签署成功后激活。"
impact: "激活客户产品。"
field_targets:
  - cust_auth_application.open_status
evidence: CustProductDomainService.createProductAggrement, activeProduct
```

## 关联

- 表：[[tables/cust_auth_application]]、[[tables/cust_company_info]]
- 状态机：[[processes/cust-product-open-status]]
- 口径：[[calibers/cust-open-product]]