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
title: 讯易链调研答题明细（一行=一道题的一个选项，多选每选项一行）。 统计答题企业数必须 COUNT(DISTINCT company_id)。
page_key: cust_survey_answer
domain: 问卷调研
aliases:
- cust_survey_answer
anchors:
- cust_survey_answer
---
# cust_survey_answer

讯易链调研答题明细（一行=一道题的一个选项，多选每选项一行）。 统计答题企业数必须 COUNT(DISTINCT company_id)。

```ground:table
table: cust_survey_answer
description: 讯易链调研答题明细（一行=一道题的一个选项，多选每选项一行）。 统计答题企业数必须 COUNT(DISTINCT company_id)。
inactive: false
fields:
- name: answer_value
- name: company_id
- name: other_text
- name: question_no
- name: submit_time
- name: survey_code
- name: user_id
```

```ground:relation
type: SHARED_KEY
left: cust_survey_answer.company_id
right: cust_company_survey_state.company_id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-srv-answer-grain
```
