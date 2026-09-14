---
type: caliber
title: 问卷活动数据跨租户口径（all）
page_key: wenjuan_all_tenant
domain: 客户管理
status: draft
aliases: [问卷 all 租户口径, setDbTenantCode all]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - db:cust_company_survey_state.db_tenant_code
contract_version: "0.1"
belong: calibers
---

问卷活动链路的读写口径是「不按租户隔离」：`WenjuanController.markLotteryShown/surveyUrl` 与 `WenjuanDisplayService.resolveHomeDisplay/shouldStayOnHomeForGotoProduct` 均先 `MetaDataThreadLocalConfig.setDbTenantCode("all")`。对应规则 [[rules/wenjuan_all_tenant_fallback]]，落点表 [[tables/cust_company_survey_state]]。

## 需求背景

活动状态与答案被视为全租户统一数据，避免同一企业在不同租户下出现两套活动状态；代价是数据不再按租户隔离，历史遗留行可能落在非 `all` 租户下。

## 版本演进

- 当前观测：`cust_company_survey_state.db_tenant_code` 为 `all`(10) 与 `LN1`(1) 并存，`LN1` 行与代码强制口径不一致，属历史/异常数据，需人工核实（见 [[enums/cust_company_survey_state_db_tenant_code]]）。

```ground:caliber
name: 问卷活动数据跨租户口径（all）
predicate: cust_company_survey_state.db_tenant_code = 'all'
scope: 问卷活动首个访问用户 claim 与抽奖标记读写前强制 MetaDataThreadLocalConfig.setDbTenantCode("all")
evidence: "code_path:WenjuanController.java:markLotteryShown + WenjuanDisplayService.java:resolveHomeDisplay + db:cust_company_survey_state.db_tenant_code all=10"
```