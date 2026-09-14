---
type: process
title: 首个用户转盘抽奖展示标记
page_key: first_visitor_lottery_shown
domain: 客户管理
status: draft
aliases: [转盘展示标记, lottery_shown, 防刷新标记]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:markLotteryShown
  - db:cust_company_survey_state.first_visitor_lottery_shown
contract_version: "0.1"
belong: processes
---

该状态机描述 `cust_company_survey_state.first_visitor_lottery_shown` 的单向翻转：代码只会把标记置 `Y`，不存在置回 `N` 的路径。取值见 [[enums/first_visitor_lottery_shown]]，规则见 [[rules/lottery_shown_idempotent]]，落点表见 [[tables/cust_company_survey_state]]。

## 需求背景

转盘抽奖是「首个访问用户」独占的权益（[[concepts/first_visitor]]），刷新首页不能重复展示，因此用一个企业级标记做幂等：前端动效播完后调 `POST /cust-web/wenjuan/mark-lottery-shown`，服务端先 `setDbTenantCode("all")`，再异步执行 `markFirstVisitorLotteryShownIfMatch(userId, companyId)`，只对企业首个用户生效。该幂等标记是 `NONE → FIRST_VISITOR_LOTTERY` 之后不回落的关键（见 [[processes/wenjuan_home_display_scene]]）。

## 版本演进

- 当前观测：11 行全为 `Y`，DB 未出现 `N` 样本；`N` 作为初始态仅由代码语义推断。
- 写入为异步线程，且写前强制跨租户 `all`（[[calibers/wenjuan_all_tenant]]、[[rules/wenjuan_all_tenant_fallback]]）。

```ground:process
name: 首个用户转盘抽奖展示标记
field: cust_company_survey_state.first_visitor_lottery_shown
states:
  - value: Y
    label: 已展示（防刷新重复）
    source: db_dist
  - value: N
    label: 未展示（初始态，代码仅单向置 Y，DB 未观测到 N 样本）
    source: code_const
transitions:
  - from: N
    event: POST /cust-web/wenjuan/mark-lottery-shown（异步线程执行，先 setDbTenantCode(all)）
    to: Y
    evidence: "code_path:WenjuanController.java:markLotteryShown + WenjuanDisplayService.java:markLotteryShown"
```