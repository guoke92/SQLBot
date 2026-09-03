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
title: 某平台产品被多少租户开通（精确值）
page_key: platform-product-ref-count-exact
domain: 产品与配置
anchors:
- platform_product
- tenant_product
---
# 某平台产品被多少租户开通（精确值）

问法：某平台产品被多少租户开通（精确值）

```ground:pattern
pattern: platform-product-ref-count-exact
question: 某平台产品被多少租户开通（精确值）
sql: SELECT pp.product_code, COUNT(tp.id) AS tenant_count FROM platform_product pp
  LEFT JOIN tenant_product tp ON tp.platform_product_id = pp.id AND tp.open_status
  = 'Y' WHERE pp.enable = 'Y' AND pp.product_status = '1' GROUP BY pp.product_code
verification: PENDING_VALIDATION
```

## 关联
- [[platform_product]]
- [[tenant_product]]
