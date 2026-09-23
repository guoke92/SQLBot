---
type: dict
title: cust_company_survey_whitelist.enable
page_key: cust_company_survey_whitelist__enable
belong: dicts
status: draft
anchors: [cust_company_survey_whitelist.enable]
sources: ['database_profile:cust_company_survey_whitelist.enable', 'database_schema:cust_company_survey_whitelist.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_company_survey_whitelist]
---

# cust_company_survey_whitelist.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_company_survey_whitelist.enable`，表页 [[tables/cust_company_survey_whitelist]]。

## 取值

```ground:dict
dict: cust_company_survey_whitelist__enable
fields: [cust_company_survey_whitelist.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
