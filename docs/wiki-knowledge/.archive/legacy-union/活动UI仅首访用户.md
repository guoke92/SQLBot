---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:survey@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 活动UI仅首访用户
page_key: 活动UI仅首访用户
domain: survey
field_targets:
- cust_company_survey_state.company_id
- cust_company_survey_state.first_visitor_user_id
---
# 活动UI仅首访用户

同企业非首个访问用户不展示抽奖、指引和右下角入口；首访用户依据 first_visitor_user_id 判定。

```ground:rule
rule: first-visitor-only-ui
field_targets:
- cust_company_survey_state.company_id
- cust_company_survey_state.first_visitor_user_id
impact: query_constraint
content: 同企业非首个访问用户不展示抽奖、指引和右下角入口；首访用户依据 first_visitor_user_id 判定。
scope: 产融首页活动展示
```

## 关联
- [[cust_company_survey_state]]
