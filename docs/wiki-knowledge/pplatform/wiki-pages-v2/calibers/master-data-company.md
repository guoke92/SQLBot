---
type: caliber
title: 主数据企业口径
page_key: master-data-company
domain: 企业集团关系
status: draft
aliases: [主数据企业, data_type=DATA_TYPE_MAIN]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
contract_version: "0.1"
belong: calibers
---

主数据企业指以企业主数据身份存在、可对外参与集团与业务关系的企业记录，判定条件为 `cust_company_info.data_type = DATA_TYPE_MAIN`，用于把企业主数据与记录数据区分开。

## 需求背景

同一套企业信息表中同时承载主数据与业务记录数据，若不显式区分，集团关系与列表类查询会把非主数据记录纳入结果集，造成同企业多行、统计重复。该口径与 [[calibers/real-operator-exclude-test-data]] 共同用于结果集净化。

## 版本演进

v0 契约按现状固化，作为企业维度查询的基础过滤条件。

## 口径锚点

```ground:caliber
name: 主数据企业
predicate: cust_company_info.data_type = DATA_TYPE_MAIN
scope: 企业主数据与记录数据区分
evidence: code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
```