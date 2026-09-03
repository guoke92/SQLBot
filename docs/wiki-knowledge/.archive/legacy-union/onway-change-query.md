---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-product-activation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 某企业在途变更单
page_key: onway-change-query
domain: 客户与建档
anchors:
- cust_change_record
---
# 某企业在途变更单

问法：某企业在途变更单

```ground:pattern
pattern: onway-change-query
question: 某企业在途变更单
sql: SELECT * FROM cust_change_record WHERE cust_id = ? AND (status IS NULL OR status
  NOT IN ('CUST_CHECK_PASS','CUST_CHECK_REJECT')) ORDER BY id DESC LIMIT 1
verification: PENDING_VALIDATION
```

## 关联
- [[cust_change_record]]
