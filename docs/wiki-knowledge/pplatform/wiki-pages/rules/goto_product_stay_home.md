---
type: rule
title: "gotoProduct 留存首页条件"
page_key: "goto_product_stay_home"
domain: "customer_survey"
status: published
aliases: ["gotoProduct 留存首页条件"]
oid: 17
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_company_survey_state.first_visitor_user_id, cust_company_survey_whitelist.enable]
scope:
  databases: [lowcode_pplatform]
---

# gotoProduct 留存首页条件

**业务定位**：满足条件时登录后留存产融首页，不自动跳转默认业务产品。

## 需求背景

改变登录后产品跳转决策。活动有效、企业在白名单、企业未完成答题且当前用户为企业首个访问用户时，登录后留存产融首页。

## 版本演进

- v0.1 初稿，基于代码证据。

```ground:rule
name: "gotoProduct 留存首页条件"
content: "活动有效、企业在白名单、企业未完成答题且当前用户为企业首个访问用户时，登录后留存产融首页不自动跳转默认业务产品"
impact: "改变登录后产品跳转决策"
field_targets:
  - "cust_company_survey_whitelist.enable"
  - "cust_company_survey_state.first_visitor_user_id"
evidence: "code_path:WenjuanDisplayService.java:shouldStayOnHomeForGotoProduct"
```

[[cust_company_survey_whitelist]] [[cust_company_survey_state]] [[survey_whitelist]] [[first_visitor_user]] [[wenjuan_home_display_scenario]]