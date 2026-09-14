---
type: rule
title: 仅企业首个访问用户可见活动UI
page_key: first_visitor_only_ui
domain: 客户管理
status: draft
aliases: [首访用户可见, claimFirstVisitor 规则]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
contract_version: "0.1"
belong: rules
---

`claimFirstVisitor` 判定 `isFirstVisitor`；非首个访问用户时 `displayScene` 固定 `NONE`，抽奖、指引、右下角入口一律不展示。判定与落点见 [[tables/cust_company_survey_state]] 与 [[concepts/first_visitor]]，效果见 [[processes/wenjuan_home_display_scene]]。

## 需求背景

活动权益按企业独占给首个访问用户，避免同企业多人重复领取；该判定同时决定是否把用户留在产融首页（[[rules/stay_on_home_for_survey]]）。

## 版本演进

- 「首个用户」由 `claimFirstVisitor(companyId,userId,respondent,dbTenantCode)` 动态判定，判定结果不落用户字段。

```ground:rule
name: 仅企业首个访问用户可见活动UI
content: claimFirstVisitor 判定 isFirstVisitor；非首个访问用户时 displayScene 固定 NONE（不展示抽奖、指引、右下角入口）
impact: 同企业其他用户不展示任何活动 UI
field_targets:
  - cust_company_survey_state.company_id
evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
```