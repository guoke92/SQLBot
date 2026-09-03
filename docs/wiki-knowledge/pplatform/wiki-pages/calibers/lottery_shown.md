---
type: caliber
title: "转盘已展示"
page_key: "lottery_shown"
domain: "customer_survey"
status: published
aliases: ["转盘已展示"]
oid: 8
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_company_survey_state.first_visitor_lottery_shown]
scope:
  databases: [lowcode_pplatform]
---

# 转盘已展示

**业务定位**：判断转盘是否已展示，防止重复展示。

## 需求背景

用于控制转盘展示一次，避免用户在刷新页面时重复看到转盘和中奖弹窗。

## 版本演进

- v0.1 初稿，基于代码证据。

```ground:caliber
name: "转盘已展示"
predicate: "cust_company_survey_state.first_visitor_lottery_shown = 'Y'"
scope: "防止转盘重复展示"
evidence: "code"
```

[[cust_company_survey_state]] [[first_visitor_lottery_shown_flag]] [[lottery_shown_once]] [[lottery_shown_flag]]