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
type: rule
title: 互通产品开通状态使用 Y/P/N
page_key: 互通产品开通状态使用-Y-P-N
domain: interworking
field_targets:
- tenant_interworking_product.open_status
- cust_interworking_product.open_status
---
# 互通产品开通状态使用 Y/P/N

ProductOpenStatusEnum 的物理键为 Y=已开通、P=开通中、N=未开通；企业申请的 OPENED/OPENING 不属于本三表口径。

```ground:rule
rule: interworking-status-ynp
field_targets:
- tenant_interworking_product.open_status
- cust_interworking_product.open_status
impact: query_constraint
content: ProductOpenStatusEnum 的物理键为 Y=已开通、P=开通中、N=未开通；企业申请的 OPENED/OPENING 不属于本三表口径。
scope: 互通产品和企业互通产品开通查询
```

## 关联
- [[cust_interworking_product]]
- [[tenant_interworking_product]]
