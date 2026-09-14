---
type: rule
title: 答卷完成态不落库，实时调问卷星
page_key: survey_status_not_persisted
domain: 客户管理
status: draft
aliases: [不落完成态, isSurveyCompleted 实时查询]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:syncAndDisplayConfig
  - code_path:WenjuanDisplayService.java:syncAndResolve
contract_version: "0.1"
belong: rules
---

`syncAndResolve` 即 `resolveHomeDisplay`，每次实时调 `wenjuanOpenApiClient.isSurveyCompleted(respondent)`；接口注释明确「答卷状态不落库」。

## 需求背景

答卷数据由外部问卷星持有，本地只保留企业级活动状态（[[tables/cust_company_survey_state]]），因此完成态无法离线判断，接口响应时间受外部依赖影响。`respondent` 实际存的是企业ID字符串，见 [[concepts/respondent]]。

## 版本演进

- 当前观测：`cust_company_survey_state` 中不存在问卷完成态字段，与「不落库」的说法一致。

```ground:rule
name: 答卷完成态不落库，实时调问卷星
content: syncAndResolve 即 resolveHomeDisplay，每次实时调 wenjuanOpenApiClient.isSurveyCompleted(respondent)；接口注释明确「答卷状态不落库」
impact: cust_company_survey_state 中不存在问卷完成态字段，本地无法离线判断完成情况
field_targets:
  - cust_company_survey_state.company_id
evidence: "code_path:WenjuanController.java:syncAndDisplayConfig + WenjuanDisplayService.java:syncAndResolve"
```