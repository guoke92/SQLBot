---
type: concept
title: 问卷完成态
page_key: concepts/survey_completed
domain: 问卷
status: draft
aliases:
  - 答卷状态
  - surveyCompleted
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:WenjuanOpenApiClient
  - code:WenjuanDisplayService.java
contract_version: "0.1"
maps_to: WenjuanOpenApiClient.isSurveyCompleted(respondent)
field_targets: []
adjudication: boundary
also_confused_with:
  - cust_survey_answer 提交答案
---

# 问卷完成态

「问卷完成态」特指[[concepts/wenjuan]]（问卷星活动）中的「该企业是否已完成问卷」这一实时判定，来源是 `WenjuanOpenApiClient.isSurveyCompleted(respondent)`，其中 `respondent` 是 [[tables/cust_company_survey_state]] 中的问卷星答卷标识（代码取 `String.valueOf(companyId)`）。

它与「[[tables/cust_survey_answer]] 提交答案」是 boundary 关系：后者是[[concepts/cust_survey]]调研问卷的落库行为，前者**不落库**，每次访问都实时查询问卷星（见 [[calibers/wenjuan_no_persist_completion]]）。因此不能用一条 SQL 在本地统计问卷星活动的完成人数。

完成态参与首页展示场景的判定：抽奖已展示且问卷未完成 → `GUIDE_ONLY`；问卷已完成 → 亦停在 `GUIDE_ONLY`，细节见 [[processes/wenjuan_home_display_scene]]。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：问卷星接口的可用性 SLA 与失败重试策略。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[concepts/wenjuan]]、[[concepts/cust_survey]]、[[tables/cust_company_survey_state]]、[[tables/cust_survey_answer]]、[[calibers/wenjuan_no_persist_completion]]、[[processes/wenjuan_home_display_scene]]。