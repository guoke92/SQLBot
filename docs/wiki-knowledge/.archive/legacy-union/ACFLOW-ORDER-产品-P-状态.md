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
type: rule
title: ACFLOW/ORDER 产品 P 状态
page_key: ACFLOW-ORDER-产品-P-状态
domain: 产品与配置
field_targets:
- tenant_product.open_status
---
# ACFLOW/ORDER 产品 P 状态

ACFLOW/ORDER 产品 activate 后先置 open_status=P（开通中），等外部多级回调才置 Y。 查询"已开通"时 P 不算——只有 Y 是终态开通。

```ground:rule
rule: acflow-order-p-status
field_targets:
- tenant_product.open_status
impact: query_constraint
content: ACFLOW/ORDER 产品 activate 后先置 open_status=P（开通中），等外部多级回调才置 Y。 查询"已开通"时 P 不算——只有
  Y 是终态开通。
scope: 按开通状态过滤产品/租户
```

## 关联
- [[tenant_product]]
