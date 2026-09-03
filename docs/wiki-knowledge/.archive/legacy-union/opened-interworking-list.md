---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:interworking-products@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 某企业已开通的互通产品
page_key: opened-interworking-list
domain: 产品与配置
anchors:
- cust_interworking_product
- tenant_interworking_product
---
# 某企业已开通的互通产品

问法：某企业已开通的互通产品

```ground:pattern
pattern: opened-interworking-list
question: 某企业已开通的互通产品
sql: "SELECT ci.platform_product_code, ci.open_time FROM cust_interworking_product\
  \ ci JOIN tenant_interworking_product ti ON ti.id = ci.product_id WHERE ci.cust_id\
  \ = ? AND ci.open_status = 'OPENED' AND ci.enable = 'Y'\n  AND ti.open_status =\
  \ 'Y' AND ti.enable = 'Y'"
verification: PENDING_VALIDATION
```

## 关联
- [[cust_interworking_product]]
- [[tenant_interworking_product]]
