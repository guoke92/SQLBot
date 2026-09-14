---
type: rule
title: 进入产品前企业角色检查
page_key: goto-product-company-type-check
domain: 平台产品配置
status: draft
aliases: [企业角色检查, gotoProductSupplierByCompanyType]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductApplication.gotoProductSupplierByCompanyType
contract_version: "0.1"
belong: rules
---

多角色产品且产品为通用产品时，进入产品前检查企业是否完成认证，未完成则禁止进入；平台运营方不检查项目状态。字段落点为 [[tables/cust_company_info]] 的 `cust_build_status`，角色语义见 [[concepts/companyType]]，通用产品前提见 [[calibers/general-product-scope]]。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `PlatformProductApplication.gotoProductSupplierByCompanyType` 的代码证据。

```ground:rule
name: 进入产品前企业角色检查
content: "多角色产品且产品为通用产品时，检查企业是否完成认证，平台运营方不检查项目状态。"
impact: "阻止进入产品。"
field_targets:
  - cust_company_info.cust_build_status
evidence: PlatformProductApplication.gotoProductSupplierByCompanyType
```

## 关联

- 表：[[tables/cust_company_info]]
- 口径：[[calibers/general-product-scope]]
- 术语：[[concepts/companyType]]
- 同类校验：[[rules/goto-product-project-status-check]]