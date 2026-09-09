---
type: rule
title: "首个访问用户独家展示"
page_key: first_visitor_exclusive_display
belong: rules
domain: "customer_survey"
status: published
aliases: ["首个访问用户独家展示"]
oid: 14
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_company_survey_state.first_visitor_user_id]
scope:
  databases: [lowcode_pplatform]
---

# 首个访问用户独家展示

**业务定位**：仅首个访问用户可看到抽奖和问卷入口。

## 需求背景

企业内其他用户看不到任何活动 UI。通过 `claimFirstVisitor` 并发认领首个访问用户，仅当 `first_visitor_user_id` 等于当前用户时展示活动，否则返回 `NONE`。

## 版本演进

- v0.1 初稿，基于代码证据。

```ground:rule
name: "首个访问用户独家展示"
content: "通过 claimFirstVisitor 并发认领首个访问用户；仅 first_visitor_user_id 等于当前用户时展示抽奖和问卷入口，其他用户展示 NONE"
impact: "企业内其他用户看不到任何活动UI"
field_targets:
  - "cust_company_survey_state.first_visitor_user_id"
evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
```

[[cust_company_survey_state]] [[first_visitor_user]] [[first_visitor_user]] [[wenjuan_home_display_scenario]]