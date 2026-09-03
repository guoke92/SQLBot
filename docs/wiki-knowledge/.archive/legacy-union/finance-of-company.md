---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-enterprise-rel@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 某企业对应的有效资金方有哪些
page_key: finance-of-company
domain: project-enterprise
anchors:
- cust_company_info
- cust_project_rel
---
# 某企业对应的有效资金方有哪些

问法：某企业对应的有效资金方有哪些

```ground:pattern
pattern: finance-of-company
question: 某企业对应的有效资金方有哪些
sql: SELECT DISTINCT c4.* FROM cust_company_info c1 JOIN cust_project_rel c2 ON c1.code=c2.ref_cust_project_rel_cust_company_info
  AND c2.enable='Y' JOIN cust_project_rel c3 ON c2.project_id=c3.project_id AND c3.company_type='FINANCE'
  AND c3.enable='Y' JOIN cust_company_info c4 ON c3.ref_cust_project_rel_cust_company_info=c4.code
  AND c4.cust_build_status='BUILD_SUCCESS' AND c4.cust_status='EFFECT' AND c4.data_type='1'
  AND c4.enable='Y' WHERE c1.id=:company_id
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
- [[cust_project_rel]]
