---
type: concept
title: "企业首个访问用户"
page_key: "first_visitor_user"
domain: "customer_survey"
status: published
aliases: ["企业首个且首次登入用户", "firstVisitor"]
oid: 11
sources: ["db"]
contract_version: "0.1"
maps_to: "cust_company_survey_state.first_visitor_user_id"
field_targets: ["cust_company_survey_state.first_visitor_user_id"]
adjudication: "synonym"
also_confused_with: []
boundary: ""
scope:
  databases: [lowcode_pplatform]
---

# 企业首个访问用户

**业务定位**：企业内首个进入产融首页并首次登入的用户。

## 需求背景

用于限定问卷星活动仅对首个访问用户展示，并通过 `first_visitor_user_id` 字段在数据库中存储该用户 ID。其他用户不可见活动 UI。

## 版本演进

- v0.1 初稿，基于术语桥同义词判定。

[[cust_company_survey_state]] [[first_visitor_user]] [[first_visitor_exclusive_display]] [[wenjuan_home_display_scenario]]