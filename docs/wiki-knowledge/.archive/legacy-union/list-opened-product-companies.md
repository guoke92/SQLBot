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
title: 已开通某产品的企业清单
page_key: list-opened-product-companies
domain: 客户与建档
anchors:
- cust_auth_application
---
# 已开通某产品的企业清单

问法：已开通某产品的企业清单

```ground:pattern
pattern: list-opened-product-companies
question: 已开通某产品的企业清单
sql: "SELECT DISTINCT ref_cust_company_info FROM cust_auth_application WHERE open_status\
  \ = 'OPENED' AND enable = 'Y'\n  AND ref_cust_auth_application_tenant_product =\
  \ ?"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_auth_application]]
