---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-build-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 按管理员手机号+统码查跨企业清单
page_key: list-company-by-admin-phone
domain: 客户与建档
anchors:
- cust_company_info
- cust_person_info
---
# 按管理员手机号+统码查跨企业清单

问法：按管理员手机号+统码查跨企业清单

```ground:pattern
pattern: list-company-by-admin-phone
question: 按管理员手机号+统码查跨企业清单
sql: "SELECT c.* FROM cust_company_info c JOIN cust_person_info p ON p.ref_cust_company_info\
  \ = c.code\n   AND p.phone = ? AND p.user_type = 'admin' AND p.enable = 'Y'\nWHERE\
  \ c.certification_no = ? AND c.cust_build_status = 'BUILD_SUCCESS' AND c.enable\
  \ = 'Y' ORDER BY c.identify_style, c.create_time DESC"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
- [[cust_person_info]]
