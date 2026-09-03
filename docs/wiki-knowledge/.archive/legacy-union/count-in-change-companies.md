---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-change@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 正在变更中的企业有多少
page_key: count-in-change-companies
domain: 企业建档
anchors:
- cust_company_info
---
# 正在变更中的企业有多少

问法：正在变更中的企业有多少

```ground:pattern
pattern: count-in-change-companies
question: 正在变更中的企业有多少
sql: "SELECT COUNT(1) AS in_change_company_count\nFROM cust_company_info\nWHERE cust_build_status\
  \ = 'CUST_CHANGE'\n  AND cust_status = 'CHANGE'\n  AND enable = 'Y'\n  AND data_type\
  \ = '1'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
