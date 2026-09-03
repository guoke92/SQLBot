---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:company-group@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 某集团有哪些生效融资企业
page_key: list-group-finance-companies
domain: 企业建档
anchors:
- cust_company_info
- cust_group_rel
- cust_project_rel
---
# 某集团有哪些生效融资企业

问法：某集团有哪些生效融资企业

```ground:pattern
pattern: list-group-finance-companies
question: 某集团有哪些生效融资企业
sql: "SELECT DISTINCT c4.*\nFROM cust_company_info c1\nJOIN cust_project_rel c2 ON\
  \ c1.code = c2.ref_cust_project_rel_cust_company_info AND c2.enable = 'Y'\nJOIN\
  \ cust_project_rel c3 ON c2.project_id = c3.project_id AND c3.company_type = 'FINANCE'\
  \ AND c3.enable = 'Y'\nJOIN cust_company_info c4 ON c3.ref_cust_project_rel_cust_company_info\
  \ = c4.code\nWHERE c1.id IN (SELECT cust_id FROM cust_group_rel WHERE root_cust_id\
  \ = :groupCustId AND enable = 'Y' AND cust_type LIKE '%CORE%' UNION SELECT :groupCustId)\n\
  \  AND c4.cust_build_status = 'BUILD_SUCCESS' AND c4.cust_status = 'EFFECT' AND\
  \ c4.data_type = '1' AND c4.enable = 'Y'"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
- [[cust_group_rel]]
- [[cust_project_rel]]
