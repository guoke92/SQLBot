---
type: rule
title: "转盘仅展示一次"
page_key: lottery_shown_once
belong: rules
domain: "customer_survey"
status: published
aliases: ["转盘仅展示一次"]
oid: 15
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_company_survey_state.first_visitor_lottery_shown]
scope:
  databases: [lowcode_pplatform]
---

# 转盘仅展示一次

**业务定位**：防止刷新重复展示转盘和中奖弹窗。

## 需求背景

首个用户已展示转盘后，通过 `markLotteryShown` 将 `first_visitor_lottery_shown` 置为 `Y`，后续刷新不再展示转盘和中奖弹窗。

## 版本演进

- v0.1 初稿，基于代码证据。

```ground:rule
name: "转盘仅展示一次"
content: "markLotteryShown 在首个用户已展示转盘后置 first_visitor_lottery_shown=Y，后续刷新不再展示转盘和中奖弹窗"
impact: "防刷新重复展示转盘"
field_targets:
  - "cust_company_survey_state.first_visitor_lottery_shown"
evidence: "code_path:WenjuanDisplayService.java:markLotteryShown"
```

[[cust_company_survey_state]] [[lottery_shown]] [[lottery_shown_flag]] [[first_visitor_lottery_shown_flag]]