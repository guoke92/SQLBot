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
type: pattern
title: 某题各选项的答题企业数
page_key: option-distribution-query
domain: 问卷调研
anchors:
- cust_survey_answer
---
# 某题各选项的答题企业数

问法：某题各选项的答题企业数

```ground:pattern
pattern: option-distribution-query
question: 某题各选项的答题企业数
sql: SELECT answer_value, COUNT(DISTINCT company_id) AS company_count FROM cust_survey_answer
  WHERE survey_code = 'XYL_2024_Q1' AND question_no = ? GROUP BY answer_value
verification: PENDING_VALIDATION
```

## 关联
- [[cust_survey_answer]]
