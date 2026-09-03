---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:interworking@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 已开通的互通产品有多少
page_key: count-opened-interworking-products
domain: interworking
anchors:
- tenant_interworking_product
---
# 已开通的互通产品有多少

问法：已开通的互通产品有多少

```ground:pattern
pattern: count-opened-interworking-products
question: 已开通的互通产品有多少
sql: SELECT COUNT(DISTINCT id) AS opened_interworking_product_count FROM tenant_interworking_product
  WHERE open_status = 'Y' AND enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[tenant_interworking_product]]
