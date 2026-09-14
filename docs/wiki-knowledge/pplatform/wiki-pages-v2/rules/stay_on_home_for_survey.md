---
type: rule
title: 问卷活动留首页策略
page_key: stay_on_home_for_survey
domain: 客户管理
status: draft
aliases: [shouldStayOnHomeForGotoProduct, gotoProduct 不跳转]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:shouldStayOnHomeForGotoProduct
contract_version: "0.1"
belong: rules
---

`shouldStayOnHomeForGotoProduct`：活动有效 + 企业在白名单 + 问卷未完成 + 当前用户为企业首个访问用户时，`gotoProduct` 不自动跳转默认业务产品。

## 需求背景

为提高问卷完成率，首个访问用户被刻意留在产融首页（否则登录后会被自动带去默认业务产品）。四个条件分别对应 [[rules/wenjuan_whitelist_participation]]、[[rules/first_visitor_only_ui]]、[[rules/survey_status_not_persisted]] 与活动自身有效性。

## 版本演进

- 该策略与首页展示决策同源，均在 `dbTenantCode='all'` 口径下计算（[[calibers/wenjuan_all_tenant]]）。

```ground:rule
name: 问卷活动留首页策略
content: "shouldStayOnHomeForGotoProduct：活动有效 + 企业在白名单 + 问卷未完成 + 当前用户为企业首个访问用户时，gotoProduct 不自动跳转默认业务产品"
impact: 首个访问用户被停留在产融首页以完成问卷
field_targets:
  - cust_company_survey_state.company_id
  - cust_company_survey_whitelist.company_id
evidence: "code_path:WenjuanDisplayService.java:shouldStayOnHomeForGotoProduct"
```