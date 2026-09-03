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
title: 本轮调研已答题企业清单
page_key: list-answered-companies
domain: 问卷调研
anchors:
- cust_survey_answer
---
# 本轮调研已答题企业清单

问法：本轮调研已答题企业清单

```ground:pattern
pattern: list-answered-companies
question: 本轮调研已答题企业清单
sql: SELECT DISTINCT company_id FROM cust_survey_answer WHERE survey_code = 'XYL_2024_Q1'
  AND enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_survey_answer]]
