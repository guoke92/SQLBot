---
type: rule
title: 问卷活动数据跨租户兜底（all）
page_key: wenjuan_all_tenant_fallback
domain: 客户管理
status: draft
aliases: [all 租户兜底, 跨租户读写]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:markLotteryShown
  - db:cust_company_survey_state.db_tenant_code
contract_version: "0.1"
belong: rules
---

`WenjuanController.markLotteryShown/surveyUrl` 与 `WenjuanDisplayService.resolveHomeDisplay/shouldStayOnHomeForGotoProduct` 均先 `MetaDataThreadLocalConfig.setDbTenantCode("all")`。口径见 [[calibers/wenjuan_all_tenant]] 与 [[calibers/survey_answer_all_tenant]]。

## 需求背景

问卷活动状态与答案要做成全租户统一数据，因此链路内主动改写租户上下文；这让数据不再按租户隔离，也让历史遗留行成为口径外样本。

## 版本演进

- 当前观测：`cust_company_survey_state.db_tenant_code` 存在 `all`(10) 与 `LN1`(1) 并存，`LN1` 行与代码强制口径不一致，需人工核实（[[enums/cust_company_survey_state_db_tenant_code]]）。

```ground:rule
name: 问卷活动数据跨租户兜底(all)
content: "WenjuanController.markLotteryShown/surveyUrl 与 WenjuanDisplayService.resolveHomeDisplay/shouldStayOnHomeForGotoProduct 均先 MetaDataThreadLocalConfig.setDbTenantCode(\"all\")"
impact: 问卷活动状态与答案不按租户隔离；DB 实测 cust_company_survey_state 仍有 1 行 db_tenant_code=LN1，存在与代码口径不一致的历史数据
field_targets:
  - cust_company_survey_state.db_tenant_code
  - cust_survey_answer.db_tenant_code
evidence: "code_path:WenjuanController.java:markLotteryShown + db:cust_company_survey_state.db_tenant_code（all=10, LN1=1）"
```