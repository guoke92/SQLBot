---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:survey-research@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 转盘已展示
page_key: first_visitor_lottery_shown
domain: 问卷调研
aliases:
- 抽奖
- 转盘
- 抽奖转盘
- 转盘抽奖已展示
- 中奖弹窗
anchors:
- first_visitor_lottery_shown
---
# 转盘已展示

first_visitor_lottery_shown N→Y 一次性单向翻转，仅首访用户本人可标记。

```ground:enum
enum: first_visitor_lottery_shown
fields:
- cust_company_survey_state.first_visitor_lottery_shown
values:
  Y:
    label: 已展示
  N:
    label: 未展示
```

## 关联
- [[cust_company_survey_state|cust_company_survey_state]]
