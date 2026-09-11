---
type: caliber
title: 主数据信用代码唯一口径
page_key: calibers/main_data_certification_unique
domain: 企业画像
status: draft
aliases:
  - 统一社会信用代码唯一
  - certificationNo 唯一口径
  - getMainDataByCertification
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
---

# 主数据信用代码唯一口径

本口径用于企业统一社会信用代码的重复校验：`cust_company_info.certification_no` 等于目标信用代码、`db_tenant_code` 等于当前租户、`data_type = 'MAIN'`。实现为 `getMainDataByCertification`。

三个条件缺一不可，其中 `data_type = 'MAIN'` 是本口径与「全局唯一」的差别所在：只有主数据行参与判重，记录数据行可以携带相同信用代码而不冲突。这与 [[calibers/company_effect]] 中对 `data_type = 'MAIN'` 的使用相互印证——主数据行是企业画像的权威行。

字段 `certificationNo`（统一信用代码）在 [[tables/cust_company_info]] 与法人相关字段（`legalCertificationNo`、`legalCertificationType`）并存，取数时注意区分企业主体与法人个人证件。

## 需求背景

本分析未提供本口径的需求文档（reqdoc_claims）证据。待业务补充：跨租户是否存在同一信用代码的合法场景。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 主数据信用代码唯一口径
predicate: cust_company_info.certification_no = 信用代码 AND cust_company_info.db_tenant_code = 当前租户 AND cust_company_info.data_type = 'MAIN'
scope: 企业统一社会信用代码重复校验
evidence: code_path:CustCompanyIfoEnchanceService.java:getMainDataByCertification
```

相关页面：[[concepts/company_profile]]、[[tables/cust_company_info]]、[[calibers/platform_operator_unique]]、[[calibers/company_effect]]。