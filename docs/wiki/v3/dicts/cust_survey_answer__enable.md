---
type: dict
title: cust_survey_answer.enable
page_key: cust_survey_answer__enable
belong: dicts
status: draft
anchors: [cust_survey_answer.enable]
sources: ['database_profile:cust_survey_answer.enable', 'database_schema:cust_survey_answer.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_survey_answer]
---

# cust_survey_answer.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_survey_answer.enable`，表页 [[tables/cust_survey_answer]]。

## 取值

```ground:dict
dict: cust_survey_answer__enable
fields: [cust_survey_answer.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
