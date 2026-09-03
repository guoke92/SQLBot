---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:company-product-auth@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 企业已开通的产品申请有多少
page_key: count-opened-company-products
domain: product
anchors:
- cust_auth_application
---
# 企业已开通的产品申请有多少

问法：企业已开通的产品申请有多少

```ground:pattern
pattern: count-opened-company-products
question: 企业已开通的产品申请有多少
sql: 'SELECT COUNT(DISTINCT id) AS opened_company_product_count

  FROM cust_auth_application

  WHERE open_status = ''OPENED'' AND enable = ''Y'''
verification: PENDING_VALIDATION
```

## 关联
- [[cust_auth_application]]
