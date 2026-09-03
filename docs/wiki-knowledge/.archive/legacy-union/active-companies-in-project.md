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
title: 某项目下有哪些有效企业
page_key: active-companies-in-project
domain: project-enterprise
anchors:
- cust_company_info
- cust_project_rel
- tenant_project
---
# 某项目下有哪些有效企业

问法：某项目下有哪些有效企业

```ground:pattern
pattern: active-companies-in-project
question: 某项目下有哪些有效企业
sql: SELECT DISTINCT cci.id, cci.name FROM tenant_project tp JOIN cust_project_rel
  cpl ON cpl.project_id=tp.id AND cpl.enable='Y' JOIN cust_company_info cci ON cci.code=cpl.ref_cust_project_rel_cust_company_info
  AND cci.enable='Y' AND cci.data_type='1' WHERE tp.id=:project_id AND tp.enable='Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
- [[cust_project_rel]]
- [[tenant_project]]
