---
type: dict
title: cust_survey_answer.db_tenant_code
page_key: cust_survey_answer__db_tenant_code
belong: dicts
status: draft
anchors: [cust_survey_answer.db_tenant_code]
sources: ['database_profile:cust_survey_answer.db_tenant_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_survey_answer]
---

# cust_survey_answer.db_tenant_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `cust_survey_answer.db_tenant_code`，表页 [[tables/cust_survey_answer]]。

## 取值

```ground:dict
dict: cust_survey_answer__db_tenant_code
fields: [cust_survey_answer.db_tenant_code]
values:
  all: {trust: proposed}
triage: hold
needs_review: true
```
