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
type: pattern
title: 某轮调研已提交的企业有多少
page_key: count-answer-companies
domain: survey
anchors:
- cust_survey_answer
---
# 某轮调研已提交的企业有多少

问法：某轮调研已提交的企业有多少

```ground:pattern
pattern: count-answer-companies
question: 某轮调研已提交的企业有多少
sql: 'SELECT COUNT(DISTINCT company_id) AS answered_company_count

  FROM cust_survey_answer

  WHERE survey_code = ''<survey_code>''

  '
verification: PENDING_VALIDATION
```

## 关联
- [[cust_survey_answer]]
