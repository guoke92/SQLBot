---
type: rule
title: 同一企业同一调研只答一次
page_key: survey_answer_once_per_company
belong: rules
domain: cust
status: draft
field_targets: [cust_survey_answer.company_id, cust_survey_answer.survey_code]
sources: ['code_path:CustSurveyAnswerDao.java:18']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_survey_answer]
---

# 同一企业同一调研只答一次

已存在 company_id+survey_code 则忽略重复提交。问「是否已填调研」按这两列，不要按 user_id 去重。

```ground:rule
rule: 同一企业同一调研只答一次
field_targets: [cust_survey_answer.company_id, cust_survey_answer.survey_code]
impact: write_constraint
content: 已存在 company_id+survey_code 则忽略重复提交。问「是否已填调研」按这两列，不要按 user_id 去重。
evidence: code_path:CustSurveyAnswerDao.java:18
```

## 页面链接

- [[tables/cust_survey_answer]]
