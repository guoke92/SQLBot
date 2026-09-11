---
type: caliber
title: 问卷星活动-完成态不落库口径
page_key: calibers/wenjuan_no_persist_completion
domain: 问卷
status: draft
aliases:
  - 完成态实时查询口径
  - 不落库口径
  - syncAndResolve
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---

# 问卷星活动-完成态不落库口径

本口径规定[[concepts/wenjuan]]（问卷星活动）的「问卷是否已完成」不写入本地库：不写 `cust_survey_answer`（那是[[concepts/cust_survey]]调研问卷的表），而是每次调用 `WenjuanOpenApiClient.isSurveyCompleted(respondent)` 实时获取。作用点是 `WenjuanDisplayService.syncAndDisplayConfig` 与 `resolveHomeDisplay`。

这一设计带来两个直接后果：其一，本地无法通过 SQL 直接统计「谁完成了问卷星活动」，只能依赖问卷星侧数据；其二，完成态每次访问都产生一次外部调用，展示结果（[[processes/wenjuan_home_display_scene]] 中的 `GUIDE_ONLY` 分支）依赖外部接口的可用性。

企业级的本地状态只保存在 [[tables/cust_company_survey_state]]（首个访问时间、抽奖是否已展示）。这一点也是「[[concepts/survey_completed]]」与 [[concepts/cust_survey]] 提交答案最容易被混淆的地方。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：问卷星接口不可用时的降级展示策略与超时处理。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 问卷星活动-完成态不落库口径
predicate: 不写 cust_survey_answer；每次调 WenjuanOpenApiClient.isSurveyCompleted(respondent)
scope: syncAndDisplayConfig / resolveHomeDisplay
evidence: code_path:WenjuanDisplayService.java:syncAndResolve
```

相关页面：[[concepts/wenjuan]]、[[concepts/survey_completed]]、[[concepts/cust_survey]]、[[tables/cust_company_survey_state]]、[[tables/cust_survey_answer]]、[[processes/wenjuan_home_display_scene]]。