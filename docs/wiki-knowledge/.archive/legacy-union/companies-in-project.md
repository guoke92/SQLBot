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
title: 某项目下有效已建档企业有哪些
page_key: companies-in-project
domain: 项目管理
anchors:
- cust_company_info
- cust_project_rel
---
# 某项目下有效已建档企业有哪些

问法：某项目下有效已建档企业有哪些

```ground:pattern
pattern: companies-in-project
question: 某项目下有效已建档企业有哪些
sql: "SELECT DISTINCT cci.id, cci.code, cci.name FROM cust_project_rel cpl JOIN cust_company_info\
  \ cci\n  ON cci.code = cpl.ref_cust_project_rel_cust_company_info\nWHERE cpl.project_id\
  \ = :project_id\n  AND cpl.enable = 'Y'\n  AND cci.cust_build_status = 'BUILD_SUCCESS'\n\
  \  AND cci.cust_status = 'EFFECT'\n  AND cci.enable = 'Y'\n  AND cci.data_type =\
  \ '1'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
- [[cust_project_rel]]
