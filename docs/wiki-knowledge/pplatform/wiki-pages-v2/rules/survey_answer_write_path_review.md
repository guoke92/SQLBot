---
type: rule
title: 调研问卷答案落库路径未在本链路给出
page_key: survey_answer_write_path_review
domain: 客户管理
status: draft
aliases: [答案写值点缺失, submit 未实现]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:CustSurveyController.java:submit
  - pplatform-apaas-service/CustSurveyAnswerService.java
  - db:cust_survey_answer
contract_version: "0.1"
belong: rules
---

本页记录一条「无法闭环」的规则：`CustSurveyController.submit` 调用 `custSurveyAnswerService.submit(req, companyId, userId)`，`checkPopup` 调用 `checkPopup(companyId, currentCompanyType)`；但 apaas 侧 `CustSurveyAnswerService` 仅提供通用 BaseService/查询 helper，没有 submit / checkPopup 实现，因此写值点与 `answer_value` / `other_text` / `question_no` 的赋值逻辑无法核对。

## 需求背景

这条缺口的直接影响是：[[tables/cust_survey_answer]] 的 338 行数据「字段怎么填」不可验证；`checkPopup` 的「已过期或已填写则不弹」判定逻辑也不可验证。本页作为待核项保留，见页末 REVIEW。

## 版本演进

- 当前观测：答案表 338 行、`survey_code` 恒为 `XYL_2024_Q1`，但写入侧实现未见。

```ground:rule
name: 调研问卷答案落库路径未在本链路给出（REVIEW）
content: "CustSurveyController.submit 调用 custSurveyAnswerService.submit(req, companyId, userId)，checkPopup 调用 checkPopup(companyId, currentCompanyType)；apaas 侧 CustSurveyAnswerService 仅提供通用 BaseService/查询 helper，无 submit/checkPopup 实现，写值点与 answer_value/other_text/question_no 的赋值逻辑无法核对"
impact: cust_survey_answer 338 行数据字段填充规则不可验证，checkPopup 的「已过期或已填写则不弹」判定逻辑不可验证
field_targets:
  - cust_survey_answer.answer_value
  - cust_survey_answer.other_text
  - cust_survey_answer.question_no
  - cust_survey_answer.submit_time
evidence: "code_path:CustSurveyController.java:submit + pplatform-apaas-service/CustSurveyAnswerService.java + db:cust_survey_answer 338 行（survey_code 恒 XYL_2024_Q1）"
```