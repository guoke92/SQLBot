---
type: caliber
title: 平台运营方唯一口径
page_key: platform_operator_unique
domain: 企业画像
status: draft
aliases:
  - PLATFORM_OPERATOR_COMPANY 口径
  - 平台运营企业唯一性
  - checkCustInfoBeforeSave
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
belong: calibers
---

# 平台运营方唯一口径

本口径约束「每个租户最多只能有一个平台运营方企业」：`cust_company_info.cust_company_type LIKE '%PLATFORM_OPERATOR_COMPANY%'`，且 `enable = 'Y'`、`db_tenant_code` 等于当前租户。校验发生在企业建档保存之前（`checkCustInfoBeforeSave`）。

判定使用 `LIKE '%...%'` 而非等值比较，与 [[tables/cust_company_info]] 中 `custCompanyType` 按 JSON 数组字符串处理（如 `["FINANCE"]`）的存储形态一致——同一个字段可以承载多个角色，因此需要子串匹配。

本口径与 [[calibers/main_data_certification_unique]]（主数据信用代码唯一）同属建档保存前的重复校验，但关注对象不同：本口径约束「角色」，后者约束「主体身份」。两者都以当前租户为范围。

## 需求背景

本分析未提供本口径的需求文档（reqdoc_claims）证据。待业务补充：子串匹配是否会误命中其它包含 `PLATFORM_OPERATOR_COMPANY` 字样的角色值。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 平台运营方唯一口径
predicate: cust_company_info.cust_company_type LIKE '%PLATFORM_OPERATOR_COMPANY%' AND cust_company_info.enable = 'Y' AND cust_company_info.db_tenant_code = 当前租户
scope: 企业建档保存前校验
evidence: code_path:CustCompanyIfoEnchanceService.java:checkCustInfoBeforeSave
```

相关页面：[[concepts/company_profile]]、[[tables/cust_company_info]]、[[calibers/main_data_certification_unique]]、[[calibers/company_effect]]。