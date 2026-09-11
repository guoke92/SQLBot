---
type: caliber
title: 企业生效口径
page_key: calibers/company_effect
domain: 企业画像
status: draft
aliases:
  - 生效企业口径
  - listEffectCompany
  - EFFECT 口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
---

# 企业生效口径

「企业生效」是[[concepts/company_profile]]最常被引用的查询口径，由四个条件合取而成：`cust_build_status = 'BUILD_SUCCESS'`（认证成功，见 [[processes/cust_company_info_cust_build_status]]）、`cust_status = 'EFFECT'`（客户生效，见 [[processes/cust_company_info_cust_status]]）、`data_type = 'MAIN'`（主数据，常量 `DATA_TYPE_MAIN`）、`enable = 'Y'`（逻辑有效）。

适用范围是 `listEffectCompany` / `listEffectCompanyByTenantAndType` 等企业生效查询。因为四条件横跨认证状态、客户状态与数据分层三类字段，任何单字段的运营操作（例如仅冻结企业而不动认证状态）都会即时改变企业是否出现在生效结果集中。

在[[tables/cust_company_info]]中，`data_type` 与 `mainDataId` 一起区分主数据 / 记录数据，这解释了为什么同一家企业在库中可能存在多行而只有主数据行参与生效判定。

## 需求背景

本分析未提供本口径的需求文档（reqdoc_claims）证据。待业务补充：记录数据行（非主数据）在业务上承担的场景。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 企业生效口径
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = 'MAIN' AND cust_company_info.enable = 'Y'
scope: listEffectCompany/listEffectCompanyByTenantAndType 等企业生效查询
evidence: code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
```

相关页面：[[concepts/company_profile]]、[[tables/cust_company_info]]、[[processes/cust_company_info_cust_build_status]]、[[processes/cust_company_info_cust_status]]、[[calibers/platform_operator_unique]]、[[calibers/main_data_certification_unique]]。