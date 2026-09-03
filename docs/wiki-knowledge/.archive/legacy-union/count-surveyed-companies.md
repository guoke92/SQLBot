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
title: 已回访的企业有多少
page_key: count-surveyed-companies
domain: survey
anchors:
- cust_company_survey_state
---
# 已回访的企业有多少

问法：已回访的企业有多少

```ground:pattern
pattern: count-surveyed-companies
question: 已回访的企业有多少
sql: 'SELECT COUNT(DISTINCT company_id) AS surveyed_company_count

  FROM cust_company_survey_state

  WHERE enable = ''Y''

  '
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_survey_state]]
