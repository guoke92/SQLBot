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
title: 哪些企业签署了平台授权协议
page_key: list-signed-platform-companies
domain: product
anchors:
- authorization_agreement
---
# 哪些企业签署了平台授权协议

问法：哪些企业签署了平台授权协议

```ground:pattern
pattern: list-signed-platform-companies
question: 哪些企业签署了平台授权协议
sql: 'SELECT DISTINCT cust_id

  FROM authorization_agreement

  WHERE platform_product_code = ''PLATFORM_PRODUCT_TYPE'' AND authed_status = ''Y''
  AND enable = ''Y'''
verification: PENDING_VALIDATION
```

## 关联
- [[authorization_agreement]]
