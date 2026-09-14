---
type: concept
title: respondent（受访者）
page_key: respondent
domain: 客户管理
status: draft
aliases: [答题人, 受访人]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:markLotteryShown
  - db:cust_company_survey_state.respondent
contract_version: "0.1"
maps_to: cust_company_survey_state.respondent
field_targets:
  - cust_company_survey_state.respondent
adjudication: boundary
also_confused_with:
  - cust_company_survey_state.company_id
belong: concepts
field_targets: [cust_company_survey_state.respondent]
sources: ["enrich:wiki-admin"]
---

字段名像个人，实际写入的是 `String.valueOf(companyId)`，即企业ID字符串。它是传给问卷星开放接口的「答题人」标识，与 [[tables/cust_company_survey_state]] 的 `company_id` 同值，DB 值形如 `1993860367081840641`，与 snowflake 企业ID量级一致。

## 需求背景

活动按企业独占给首个访问用户（[[concepts/first_visitor]]），问卷星侧的身份标识也只用企业维度，因此不需要真实答题人ID。使用方的典型误区是按 `respondent` 关联用户画像或做用户级去重——那会得到企业级结果。

## 版本演进

- 当前观测：`cust_company_survey_state` 中 `respondent` 与企业ID同值，无个人标识样本。
- 完成态查询 `isSurveyCompleted(respondent)` 实时调用外部接口（[[rules/survey_status_not_persisted]]）。

相关：[[cust_company_survey_state]]
