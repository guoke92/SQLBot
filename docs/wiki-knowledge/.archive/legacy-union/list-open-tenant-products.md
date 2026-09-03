---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:product-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 某租户已开通产品清单
page_key: list-open-tenant-products
domain: 产品与配置
anchors:
- platform_product
- tenant_product
---
# 某租户已开通产品清单

问法：某租户已开通产品清单

```ground:pattern
pattern: list-open-tenant-products
question: 某租户已开通产品清单
sql: SELECT tp.*, pp.name AS platform_product_name FROM tenant_product tp JOIN platform_product
  pp ON pp.id = tp.platform_product_id WHERE tp.tenant_id = ? AND tp.open_status =
  'Y' AND tp.enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[platform_product]]
- [[tenant_product]]
