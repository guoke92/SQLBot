---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-status-operations@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 冻结企业清单及冻结原因
page_key: list-frozen-companies
domain: 客户与建档
anchors:
- cust_company_info
- cust_company_lifecycle_info
---
# 冻结企业清单及冻结原因

问法：冻结企业清单及冻结原因

```ground:pattern
pattern: list-frozen-companies
question: 冻结企业清单及冻结原因
sql: SELECT c.id, c.name, c.certification_no, l.type, l.reason, l.enable FROM cust_company_lifecycle_info
  l JOIN cust_company_info c ON c.id = l.company_id WHERE l.type = 'FRZ' AND l.enable
  = 'Y' AND c.cust_status = 'FREEZE'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
- [[cust_company_lifecycle_info]]
