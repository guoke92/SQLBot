---
type: concept
title: 问卷星活动
page_key: concepts/wenjuan
domain: 问卷
status: draft
aliases:
  - Wenjuan
  - 产融首页问卷活动
  - 抽奖问卷
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_state
  - db:cust_company_survey_whitelist
  - code:WenjuanController
  - code:WenjuanDisplayService.java
contract_version: "0.1"
maps_to: WenjuanController + WenjuanDisplayService + cust_company_survey_state + cust_company_survey_whitelist
field_targets:
  - cust_company_survey_state.first_visitor_lottery_shown
  - cust_company_survey_state.first_visit_time
  - cust_company_survey_whitelist.enable
adjudication: boundary
also_confused_with:
  - 调研问卷
---

# 问卷星活动

「问卷星活动」指产融首页的问卷抽奖活动（代码层称 `Wenjuan`），入口 `/cust-web/wenjuan`，由 `WenjuanController` 与 `WenjuanDisplayService` 承载，本地状态落在 [[tables/cust_company_survey_state]] 与 [[tables/cust_company_survey_whitelist]]。

与 [[concepts/cust_survey]]（调研问卷）的边界有两条：其一，**问卷星活动不落答卷状态**，完成态每次实时调用问卷星（见 [[calibers/wenjuan_no_persist_completion]]、[[concepts/survey_completed]]）；其二，**展示范围受白名单与首个访问用户双重限制**，仅白名单企业（[[calibers/wenjuan_whitelist_company]]）且企业首个访问用户（[[concepts/first_visitor]]）能看到 UI。首页展示什么由 [[processes/wenjuan_home_display_scene]] 描述。

因此在本 wiki 中二者是 boundary 关系：看到「问卷」字样时必须先确认指的是哪一套机制，再决定去查答案表还是查活动状态表。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：活动的起止时间配置与抽奖奖品的发放链路。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/cust_company_survey_state]]、[[tables/cust_company_survey_whitelist]]、[[concepts/cust_survey]]、[[concepts/first_visitor]]、[[concepts/survey_completed]]、[[processes/wenjuan_home_display_scene]]、[[calibers/wenjuan_whitelist_company]]、[[calibers/wenjuan_no_persist_completion]]。