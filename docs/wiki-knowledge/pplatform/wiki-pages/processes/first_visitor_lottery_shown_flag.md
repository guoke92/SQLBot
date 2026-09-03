---
type: process
title: "企业首个访问用户转盘展示标记"
page_key: "first_visitor_lottery_shown_flag"
domain: "customer_survey"
status: published
aliases: ["企业首个访问用户转盘展示标记", "first_visitor_lottery_shown"]
oid: 5
sources: ["code", "db"]
contract_version: "0.1"
field_targets: [cust_company_survey_state.first_visitor_lottery_shown]
scope:
  databases: [lowcode_pplatform]
---

# 企业首个访问用户转盘展示标记

**业务定位**：控制企业首个访问用户的转盘是否已展示，防止重复展示。

## 需求背景

通过状态字段 `Y/N` 和数据库更新，确保转盘仅展示一次。状态由数据库分布（`db_dist`）和代码枚举（`code_enum`）共同支撑。

## 版本演进

- v0.1 初稿，基于代码与 DB 证据。

```ground:process
name: "企业首个访问用户转盘展示标记"
field: "cust_company_survey_state.first_visitor_lottery_shown"
states:
  - value: "N"
    label: "转盘未展示"
    source: "code_enum"
  - value: "Y"
    label: "转盘已展示"
    source: "db_dist"
transitions:
  - from: "N"
    event: "markFirstVisitorLotteryShownIfMatch(userId, companyId)"
    to: "Y"
    evidence: "code_path:CustCompanySurveyStateDao.java:markFirstVisitorLotteryShownIfMatch"
```

[[cust_company_survey_state]] [[first_visitor_user]] [[lottery_shown]] [[lottery_shown_once]] [[first_visitor_user]] [[lottery_shown_flag]]