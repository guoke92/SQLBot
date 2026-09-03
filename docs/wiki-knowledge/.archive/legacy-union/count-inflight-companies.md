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
page_key: count-inflight-companies
domain: 企业建档
anchors:
- cust_company_info
---
# 正在变更中的企业有多少

问法：正在变更中的企业有多少

```ground:pattern
pattern: count-inflight-companies
question: 正在变更中的企业有多少
sql: SELECT COUNT(DISTINCT id) FROM cust_company_info WHERE cust_build_status = 'CUST_CHANGE'
  AND cust_status = 'CHANGE'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
