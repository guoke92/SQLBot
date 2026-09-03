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
title: 查某企业当前认证状态（Dubbo 建档状态查询）
page_key: query-company-cert-status
domain: 客户与建档
anchors:
- cust_company_info
---
# 查某企业当前认证状态（Dubbo 建档状态查询）

问法：查某企业当前认证状态（Dubbo 建档状态查询）

```ground:pattern
pattern: query-company-cert-status
question: 查某企业当前认证状态（Dubbo 建档状态查询）
sql: SELECT id, code, name, identify_style, cust_build_status, cust_status, check_status
  FROM cust_company_info WHERE name = ? AND certification_no = ? AND db_tenant_code
  = ? AND enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[cust_company_info]]
