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
title: 问卷调研有多少
page_key: count-survey
domain: survey
anchors:
- cust_company_survey_state
---
# 问卷调研有多少

问法：问卷调研有多少

```ground:pattern
pattern: count-survey
question: 问卷调研有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM cust_company_survey_state WHERE enable
  = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_survey_state]]
