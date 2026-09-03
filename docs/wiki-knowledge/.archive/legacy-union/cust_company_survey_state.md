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
type: table
title: 问卷星活动运行时状态（首访认领 + 转盘展示；不存答卷完成态——答卷在外部问卷星）。
page_key: cust_company_survey_state
domain: 问卷调研
aliases:
- cust_company_survey_state
anchors:
- cust_company_survey_state
---
# cust_company_survey_state

问卷星活动运行时状态（首访认领 + 转盘展示；不存答卷完成态——答卷在外部问卷星）。

```ground:table
table: cust_company_survey_state
description: 问卷星活动运行时状态（首访认领 + 转盘展示；不存答卷完成态——答卷在外部问卷星）。
inactive: false
fields:
- name: company_id
- name: enable
- name: first_visit_time
- name: first_visitor_lottery_shown
  dictionary: lottery-shown
- name: first_visitor_lottery_shown_time
- name: first_visitor_user_id
- name: respondent
```

```ground:relation
type: SHARED_KEY
left: cust_company_survey_whitelist.company_id
right: cust_company_survey_state.company_id
cardinality: one_to_one
status: proposed
evidence: code_path:ev-srv-claim
```

```ground:relation
type: SHARED_KEY
left: cust_survey_answer.company_id
right: cust_company_survey_state.company_id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-srv-answer-grain
```
