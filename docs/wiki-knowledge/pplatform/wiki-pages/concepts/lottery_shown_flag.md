---
type: concept
title: "转盘抽奖已展示"
page_key: lottery_shown_flag
belong: concepts
domain: "customer_survey"
status: published
aliases: ["first_visitor_lottery_shown"]
oid: 12
sources: ["db"]
contract_version: "0.1"
maps_to: "cust_company_survey_state.first_visitor_lottery_shown"
field_targets: ["cust_company_survey_state.first_visitor_lottery_shown"]
adjudication: "synonym"
also_confused_with: []
boundary: "Y/N"
scope:
  databases: [lowcode_pplatform]
---

# 转盘抽奖已展示

**业务定位**：企业首个访问用户转盘抽奖是否已展示的标记。

## 需求背景

防止转盘重复展示，字段值域为 `Y/N`。当标记为 `Y` 后，后续刷新不再展示转盘和中奖弹窗。

## 版本演进

- v0.1 初稿，基于术语桥同义词判定。

[[cust_company_survey_state]] [[lottery_shown]] [[lottery_shown_once]] [[first_visitor_lottery_shown_flag]]