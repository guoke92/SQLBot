---
type: rule
title: 转盘抽奖防刷新重复（幂等标记）
page_key: lottery_shown_idempotent
domain: 客户管理
status: draft
aliases: [防重复展示, mark-lottery-shown 规则]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:markLotteryShown
  - db:cust_company_survey_state.first_visitor_lottery_shown
contract_version: "0.1"
belong: rules
---

`mark-lottery-shown` 先 `setDbTenantCode(all)`，再异步执行 `markFirstVisitorLotteryShownIfMatch(userId, companyId)`，把 `first_visitor_lottery_shown` 置 `Y`（仅匹配当前企业首个用户）。状态机见 [[processes/first_visitor_lottery_shown]]，取值见 [[enums/first_visitor_lottery_shown]]。

## 需求背景

转盘只对首个访问用户发放（[[concepts/first_visitor]]），刷新首页不能重复播放，因此用一个企业级 `Y/N` 标记做幂等，且只有单向置 `Y` 的路径。

## 版本演进

- 当前观测：该字段 11 行全为 `Y`，无 `N` 样本。

```ground:rule
name: 转盘抽奖防刷新重复（幂等标记）
content: mark-lottery-shown 先 setDbTenantCode(all)，再异步执行 markFirstVisitorLotteryShownIfMatch(userId, companyId) 将 first_visitor_lottery_shown 置 Y（仅匹配当前企业首个用户）
impact: 刷新首页不重复展示转盘；DB 实测该字段 11 行全为 Y
field_targets:
  - cust_company_survey_state.first_visitor_lottery_shown
evidence: "code_path:WenjuanController.java:markLotteryShown + WenjuanDisplayService.java:markLotteryShown + db:cust_company_survey_state.first_visitor_lottery_shown"
```