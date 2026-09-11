---
type: caliber
title: 生效企业
page_key: effective_company
domain: 企业建档与认证
status: draft
aliases:
  - 租户生效企业判断
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyUtilApplication.java:getTenantCodesWithEffectCompany
contract_version: "0.1"
---

“生效企业”是跨表查询与租户判定的核心口径：只有同时满足**认证成功**（`cust_build_status = 'BUILD_SUCCESS'`，见 [[auth_status]]）、**客户生效**（`cust_status = 'EFFECT'`，见 [[customer_status]]）、**是主数据**（`data_type = '1'`，见 [[main_data]]）、**数据启用**（`enable = 'Y'`）四个条件的记录，才算作可开展业务的生效企业。

该口径被用于“租户是否有生效企业”的判断（`getTenantCodesWithEffectCompany`），因此四个条件缺一不可；只满足认证状态或客户状态单项的记录不能视为生效企业。

```ground:caliber
name: 生效企业
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = '1' AND cust_company_info.enable = 'Y'
scope: 企业查询、租户有生效企业判断
evidence: "code_path:CustCompanyUtilApplication.java:getTenantCodesWithEffectCompany"
```

## 需求背景

暂无需求文档主张。该口径的四个条件分别来自认证状态机（[[enterprise_auth_status_machine]]）、客户状态机（[[customer_status_machine]]）与数据类型口径（[[main_data]]），是三者交叉后的复合判定。

## 版本演进

- v0.1：依据代码证据建立口径页，条件与代码实现逐字一致。