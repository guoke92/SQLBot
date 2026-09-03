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
title: 某企业已开通哪些项目
page_key: opened-projects-of-company
domain: 项目管理
anchors:
- cust_company_info
- cust_project_rel
- tenant_project
---
# 某企业已开通哪些项目

问法：某企业已开通哪些项目

```ground:pattern
pattern: opened-projects-of-company
question: 某企业已开通哪些项目
sql: "SELECT tp.id, tp.name, cpl.company_type, cpl.project_open_status FROM cust_project_rel\
  \ cpl JOIN tenant_project tp\n  ON CAST(tp.id AS CHAR) = cpl.project_id\nJOIN cust_company_info\
  \ cci\n  ON cci.code = cpl.ref_cust_project_rel_cust_company_info\nWHERE cci.id\
  \ = :company_id\n  AND cpl.enable = 'Y'\n  AND cpl.project_open_status = 'Y'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
- [[cust_project_rel]]
- [[tenant_project]]
