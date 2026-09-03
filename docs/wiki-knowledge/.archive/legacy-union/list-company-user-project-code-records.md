---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-code@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 某企业某用户已启用的项目码记录
page_key: list-company-user-project-code-records
domain: 项目管理
anchors:
- cust_project_code_record
---
# 某企业某用户已启用的项目码记录

问法：某企业某用户已启用的项目码记录

```ground:pattern
pattern: list-company-user-project-code-records
question: 某企业某用户已启用的项目码记录
sql: "SELECT id, code, name, channel_code, status, company_type, type FROM cust_project_code_record\
  \ WHERE company_id = :company_id AND use_id = :user_id\n  AND company_type LIKE\
  \ :company_type AND enable = 'Y'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_project_code_record]]
