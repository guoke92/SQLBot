---
type: dict
title: cust_company_survey_state.first_visitor_lottery_shown
page_key: cust_company_survey_state__first_visitor_lottery_shown
belong: dicts
status: draft
anchors: [cust_company_survey_state.first_visitor_lottery_shown]
sources: ['database_profile:cust_company_survey_state.first_visitor_lottery_shown',
  'database_schema:cust_company_survey_state.first_visitor_lottery_shown']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_company_survey_state]
---

# cust_company_survey_state.first_visitor_lottery_shown

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_company_survey_state.first_visitor_lottery_shown`，表页 [[tables/cust_company_survey_state]]。

## 取值

```ground:dict
dict: cust_company_survey_state__first_visitor_lottery_shown
fields: [cust_company_survey_state.first_visitor_lottery_shown]
values:
  Y: {trust: proposed, label: 是}
  N: {trust: proposed, label: 否, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
