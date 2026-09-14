---
type: concept
title: 企业首个访问用户
page_key: first_visitor
domain: 客户管理
status: draft
aliases: [firstVisitor, first_visitor_user_id, claimFirstVisitor]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - code_path:WenjuanDisplayService.java:shouldStayOnHomeForGotoProduct
  - db:cust_company_survey_state
contract_version: "0.1"
maps_to: cust_company_survey_state.company_id
field_targets:
  - cust_company_survey_state.company_id
  - cust_company_survey_state.first_visitor_lottery_shown
adjudication: boundary
also_confused_with:
  - cust_survey_answer.user_id
belong: concepts
field_targets: [cust_company_survey_state.company_id]
sources: ["enrich:wiki-admin"]
---

「首个用户」由 `claimFirstVisitor(companyId, userId, respondent, dbTenantCode)` 动态判定，当前可见表结构中未出现独立的 `first_visitor_user_id` 列（表结构证据在该列后截断），判定结果不落用户字段，只落 `first_visitor_lottery_shown`。它与 [[tables/cust_survey_answer]] 的 `user_id`（答题人）不是同一概念。

## 需求背景

活动权益按企业级独占：同企业只有首个访问用户能看到活动 UI（[[rules/first_visitor_only_ui]]）、会被留在首页（[[rules/stay_on_home_for_survey]]）、会触发转盘抽奖与幂等标记（[[processes/first_visitor_lottery_shown]]）。

## 版本演进

- 当前观测：`cust_company_survey_state` 11 行状态记录，`first_visitor_lottery_shown` 全为 `Y`；表结构在该列附近出现截断，是否存在首访用户列待核实（见 REVIEW）。

相关：[[cust_company_survey_state]]
