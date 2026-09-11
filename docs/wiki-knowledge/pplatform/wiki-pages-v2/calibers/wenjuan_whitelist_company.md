---
type: caliber
title: 问卷星活动-白名单企业口径
page_key: calibers/wenjuan_whitelist_company
domain: 问卷
status: draft
aliases:
  - isParticipating
  - 问卷活动白名单口径
  - 参与企业口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_whitelist
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---

# 问卷星活动-白名单企业口径

本口径决定[[concepts/wenjuan]]对哪些企业开放：企业必须出现在 [[tables/cust_company_survey_whitelist]] 中且 `enable = 'Y'`，同时 `isParticipating(company_id)` 为真。判定点有三处：`WenjuanDisplayService.resolveHomeDisplay`（首页展示场景）、`getSurveyUrl`（问卷链接获取）、`shouldStayOnHomeForGotoProduct`（跳转商品页时是否留在首页）。

这是[[processes/wenjuan_home_display_scene]]中进入 `FIRST_VISITOR_LOTTERY` 的前置条件之一；不满足时场景直接落到 `NONE`。它与「首个访问用户」（[[concepts/first_visitor]]）是两个正交条件：白名单是「企业级」准入，首个访问用户是「用户在企业的次序」准入。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：`isParticipating` 除白名单外的判定构成（分析中仅给出该调用名，未展开其内部逻辑）。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 问卷星活动-白名单企业口径
predicate: cust_company_survey_whitelist.enable = 'Y' 且 isParticipating(company_id) 为真
scope: WenjuanDisplayService.resolveHomeDisplay / getSurveyUrl / shouldStayOnHomeForGotoProduct
evidence: db + code_path:WenjuanDisplayService.java:resolveHomeDisplay
```

相关页面：[[concepts/wenjuan]]、[[concepts/first_visitor]]、[[tables/cust_company_survey_whitelist]]、[[tables/cust_company_survey_state]]、[[processes/wenjuan_home_display_scene]]。