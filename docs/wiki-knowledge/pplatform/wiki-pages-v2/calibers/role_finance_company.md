---
type: caliber
title: 口径：金融机构角色
page_key: role_finance_company
domain: 租户项目
status: draft
aliases: [金融机构角色, FINANCE]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:CustCompanyTypeEnum
contract_version: "0.1"
belong: calibers
---

判定 [[cust_project_rel]] 中企业在项目下承担"金融机构"角色，对应 [[CustCompanyTypeEnum]] 的 FINANCE；与 [[role_core_company]] 同属导出关联企业的过滤集合。

## 需求背景
语义分析未附带需求文档锚点；导出关联企业需按角色收敛（CORE/FINANCE）。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 金融机构角色
predicate: "cust_project_rel.company_type = 'FINANCE'"
scope: cust_project_rel
evidence: "code:CustCompanyTypeEnum.FINANCE，导出关联企业时过滤 CORE/FINANCE"
```