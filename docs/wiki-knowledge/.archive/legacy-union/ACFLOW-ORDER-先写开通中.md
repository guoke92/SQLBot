---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:tenant-product-lifecycle@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: ACFLOW/ORDER 先写开通中
page_key: ACFLOW-ORDER-先写开通中
domain: product
field_targets:
- tenant_product.open_status
- tenant_product.platform_product_code
---
# ACFLOW/ORDER 先写开通中

ACFLOW/ORDER 产品开通时先写 open_status=P，待多级回调后再置 Y。

```ground:rule
rule: acflow-order-pending
field_targets:
- tenant_product.open_status
- tenant_product.platform_product_code
impact: query_constraint
content: ACFLOW/ORDER 产品开通时先写 open_status=P，待多级回调后再置 Y。
scope: 租户产品开通
```

## 关联
- [[tenant_product]]
