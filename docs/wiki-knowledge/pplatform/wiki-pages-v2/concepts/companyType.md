---
type: concept
title: companyType 企业角色类型
page_key: companyType
domain: 平台产品配置
status: draft
aliases: [companyType, custCompanyType, 企业角色]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:cust_company_info.cust_company_type
  - code:cust_person_info.company_type
  - code:cust_project_rel.company_type
maps_to: cust_company_info.cust_company_type
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
belong: concepts
field_targets: [cust_company_info.cust_company_type]
---

companyType、custCompanyType 与「企业角色」是同一语义，映射到 [[tables/cust_company_info]] 的 `cust_company_type`。

边界：companyType 是枚举值，如 CORE、SUPPLIER、DEALER、FINANCE 等。同一语义在 [[tables/cust_person_info]] 与 [[tables/cust_project_rel]] 上以 `company_type` 命名出现。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 表：[[tables/cust_company_info]]、[[tables/cust_person_info]]、[[tables/cust_project_rel]]
- 规则：[[rules/cust-role-combine-check]]、[[rules/goto-product-company-type-check]]
- 术语：[[concepts/custRoleCombine]]

相关：[[cust_company_info]]
