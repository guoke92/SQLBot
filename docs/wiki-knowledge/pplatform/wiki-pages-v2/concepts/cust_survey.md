---
type: concept
title: 调研问卷
page_key: cust_survey
domain: 问卷
status: draft
aliases:
  - 讯易链调研问卷
  - CustSurvey
  - survey
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_survey_answer
  - code:CustSurveyController
  - code:CustSurveyAnswerService
contract_version: "0.1"
maps_to: CustSurveyController + CustSurveyAnswerService + cust_survey_answer
field_targets:
  - cust_survey_answer.answer_value
  - cust_survey_answer.other_text
  - cust_survey_answer.submit_time
adjudication: boundary
also_confused_with:
  - 问卷星活动
belong: concepts
---

# 调研问卷

「调研问卷」指讯易链调研问卷（代码层称 `CustSurvey` / `survey`），入口为 `/cust-web/survey`，由 `CustSurveyController` 与 `CustSurveyAnswerService` 提供服务。

它与 [[concepts/wenjuan]]（问卷星活动）的最主要边界是**是否落库**：调研问卷会提交并持久化答案到 [[tables/cust_survey_answer]]，DB 中 `survey_code` 为 `XYL_2024_Q1`；而问卷星活动不落答卷状态。因此在本 wiki 中二者是 boundary 关系而非同义词。

答案取数的归属口径见 [[calibers/survey_answer_attribution]]。答案形态上，一道多选题会拆成多行（`answer_value` 每个选项单独一行），「其他」选项的补充文本进 `other_text`。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：问卷题干的配置位置、调研结果的统计与导出路径。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/cust_survey_answer]]、[[concepts/wenjuan]]、[[concepts/survey_completed]]、[[calibers/survey_answer_attribution]]。