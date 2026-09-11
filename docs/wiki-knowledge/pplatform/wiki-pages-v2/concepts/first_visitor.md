---
type: concept
title: 首个访问用户
page_key: concepts/first_visitor
domain: 问卷
status: draft
aliases:
  - firstVisitor
  - first_visitor
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_state
  - code:WenjuanDisplayService.java
contract_version: "0.1"
maps_to: cust_company_survey_state.claimFirstVisitor / first_visitor_lottery_shown
field_targets:
  - cust_company_survey_state.first_visit_time
  - cust_company_survey_state.first_visitor_lottery_shown
  - cust_company_survey_state.first_visitor_lottery_shown_time
adjudication: synonym
also_confused_with: []
---

# 首个访问用户

「首个访问用户」（代码层 `firstVisitor` / `first_visitor`）是[[concepts/wenjuan]]（问卷星活动）的准入角色之一，判定**以企业为单位**：只有该企业的第一名访问用户可以看到转盘抽奖、指引弹窗与右下角问卷入口。同义词 `firstVisitor`、`first_visitor` 与中文叫法在本 wiki 中等价。

状态载体是 [[tables/cust_company_survey_state]] 的 `first_visit_time`（首个用户首次访问时间）与 `first_visitor_lottery_shown` / `first_visitor_lottery_shown_time`（抽奖是否/何时已展示，DB 实测均为 Y）。抽奖一旦展示过，后续访问落在 `GUIDE_ONLY` 或 `NONE` 分支，见 [[processes/wenjuan_home_display_scene]]。

它与白名单口径（[[calibers/wenjuan_whitelist_company]]）是两个正交条件：白名单决定「哪些企业有活动」，本概念决定「企业里的哪个用户看得到」。非首个访问用户直接落到 `NONE`。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：首个访问用户判定是否受企业内用户注销／离职影响。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/cust_company_survey_state]]、[[concepts/wenjuan]]、[[processes/wenjuan_home_display_scene]]、[[calibers/wenjuan_whitelist_company]]。