---
type: caliber
title: "首个访问用户"
page_key: "first_visitor_user"
domain: "customer_survey"
status: published
aliases: ["首个访问用户"]
oid: 7
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_company_survey_state.company_id, cust_company_survey_state.first_visitor_user_id]
scope:
  databases: [lowcode_pplatform]
---

# 首个访问用户

**业务定位**：判断当前用户是否企业首个访问用户。

## 需求背景

在问卷星活动中，只有首个访问用户可看到活动 UI。该口径用于代码中比较当前用户 ID 与状态表中的第一个访问用户 ID。

## 版本演进

- v0.1 初稿，基于代码证据。

```ground:caliber
name: "首个访问用户"
predicate: "cust_company_survey_state.first_visitor_user_id = :userId AND cust_company_survey_state.company_id = :companyId"
scope: "判断当前用户是否企业首个访问用户"
evidence: "code"
```

[[cust_company_survey_state]] [[first_visitor_lottery_shown_flag]] [[first_visitor_exclusive_display]] [[first_visitor_user]]