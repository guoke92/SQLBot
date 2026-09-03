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
title: 在途变更单有多少
page_key: count-inflight-records
domain: 企业建档
anchors:
- cust_change_record
---
# 在途变更单有多少

问法：在途变更单有多少

```ground:pattern
pattern: count-inflight-records
question: 在途变更单有多少
sql: SELECT COUNT(1) FROM cust_change_record WHERE enable = 'Y' AND status NOT IN
  ('CUST_CHECK_PASS', 'CUST_CHECK_REJECT')
verification: PENDING_VALIDATION
```

## 关联
- [[cust_change_record]]
