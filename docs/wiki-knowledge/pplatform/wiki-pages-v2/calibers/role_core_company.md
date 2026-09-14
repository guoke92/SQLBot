---
type: caliber
title: 口径：核心企业角色
page_key: role_core_company
domain: 租户项目
status: draft
aliases: [核心企业角色, CORE]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:CustCompanyTypeEnum
contract_version: "0.1"
belong: calibers
---

判定 [[cust_project_rel]] 中企业在项目下承担"核心企业"角色，对应 [[CustCompanyTypeEnum]] 的 CORE；导出关联企业时与 [[role_finance_company]] 一起作为过滤条件。

## 需求背景
语义分析未附带需求文档锚点；导出关联企业需按角色收敛（CORE/FINANCE）。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 核心企业角色
predicate: "cust_project_rel.company_type = 'CORE'"
scope: cust_project_rel
evidence: "code:CustCompanyTypeEnum.CORE，导出关联企业时过滤 CORE/FINANCE"
```