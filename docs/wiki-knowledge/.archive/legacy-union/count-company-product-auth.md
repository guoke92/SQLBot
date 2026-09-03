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
title: 企业产品授权有多少
page_key: count-company-product-auth
domain: product
anchors:
- authorization_agreement
---
# 企业产品授权有多少

问法：企业产品授权有多少

```ground:pattern
pattern: count-company-product-auth
question: 企业产品授权有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM authorization_agreement WHERE enable =
  'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[authorization_agreement]]
